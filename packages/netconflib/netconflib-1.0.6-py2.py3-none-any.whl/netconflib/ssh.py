# -*- coding: utf-8 -*-
"""SSH helper class.

This class gives the ability to remotely execute comands via SSH.
"""

import os
import subprocess
from sys import platform
import shlex
import logging
import threading, queue
from paramiko import client, Transport, RSAKey, Ed25519Key
from .constants import Commands
from .constants import Paths

outlock = threading.Lock()

class SSH:
    """This class provides SSH functionality.
    """

    def __init__(self, address, username, password, shell=False):
        self.logger = logging.getLogger('app.netconflib.ssh')
        self.logger.info("Connecting to server %s.", address)

        self.address = address
        self.client = client.SSHClient()
        #self.setup_ssh(username, password)

        if not self.private_key_exists():
            self.generate_key()
        self.threadpool = []
        thread = threading.Thread(target=self.setup_ssh, args=(username, password))
        thread.start()
        self.threadpool.append(thread)

        if shell:
            self.shell = self.client.invoke_shell()
            self.transport = Transport((address, 22))
            self.transport.connect(username=username, password=password)
            thread = threading.Thread(target=self.process)
            thread.daemon = True
            thread.start()

    def send_command(self, command, block=True):
        """Executes the command on the remote shell and prints the output.

        You can send a shell command to the remote machine and execute it.
        The output will be printed in the console.

        Arguments:
            command {string} -- the SSH command

        Returns:
            string -- The output of the command.
        """

        result = ""
        out_queue = queue.Queue()
        if self.client:
            self.logger.debug("Executing command on %s: %s", self.address, command)
            thread = threading.Thread(target=self.process_data, args=(command, out_queue))
            thread.start()
            if block:
                thread.join()
                result = out_queue.get()
        else:
            self.logger.error("Connection not opened.")
        return result

    def send_shell(self, command):
        """Experimental. Do not use this.

        Arguments:
            command {string} -- Command
        """

        if self.shell:
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")

    def process_data(self, cmd, out_queue):
        """Processes the data in the communication channel.
        
        Arguments:
            cmd {string} -- Command.
            out_queue {Queue} -- Output queue.
        """

        result = ""
        _, stdout, stderr = self.client.exec_command(cmd, get_pty=True)
        for line in iter(stdout.readline, ""):
            result += line
            self.logger.debug("%s: %s", self.address, line.replace("\n", ""))
        for line in iter(stderr.readline, ""):
            result += line
            self.logger.error("%s: %s", self.address, line.replace("\n", ""))
        out_queue.put(result)

    def process(self):
        """Prints data in the console when available.
        """

        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                print(strdata, end="")
                if strdata.endswith("$ "):
                    print("\n$ ", end="")

    def setup_ssh(self, username, password):
        """Setups the authentication for SSH.
        """

        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.share_key_with_host(self.get_public_key(), username, password)
        self.close_connection()

        self.client.connect(self.address, username=username,
                            pkey=self.get_private_key())

    def check_host_key(self, key):
        """Checks if the host contains the specified key.
        
        Arguments:
            key {string} -- The public key.
        
        Returns:
            boolean -- True (contains), False else.
        """

        cmd = Commands.cmd_check_key.format(key)
        self.logger.debug("Checking, if the host %s contains the key...", self.address)
        output = self.send_command(cmd)
        if "0" in output:
            self.logger.debug("The host %s already has this key.", self.address)
            return True
        else:
            self.logger.debug("The host %s does not have this key.", self.address)
            return False

    def check_cluster_key_generated(self):
        """Checks if the host has an id_rsa key or not.
        
        Returns:
            boolean -- True if yes, false else.
        """

        cmd = Commands.cmd_check_key_cluster
        self.logger.debug("Checking, if the host %s has an id_rsa key...", self.address)
        output = self.send_command(cmd)
        if "not found" in output:
            self.logger.debug("The host %s does not have an SSH key yet.", self.address)
            return False
        else:
            self.logger.debug("The host %s has already generated an SSH key.", self.address)
            return True

    def share_key_with_host(self, key, username=None, password=None):
        """Saves the provided key (public part) on the server.
        If the key exists, nothing will be shared.
        
        Arguments:
            key {string} -- The public key.
            username {string} -- The host's username.
            password {string} -- The host's password.
        """

        self.logger.debug("Sharing key with host %s...", self.address)
        if username is not None:
            self.client.connect(self.address, username=username,
                            password=password)
        if not self.check_host_key(key):
            self.logger.debug("Adding public key to the %s host's authorized_keys...", self.address)
            self.send_command(Commands.cmd_add_key_to_authorized_keys
                .format(key))
        if not self.check_host_key(key):
            self.logger.error("Key sharing failed with %s, deleting local key...", self.address)
            os.remove(Paths.private_key_file)
            os.remove(Paths.public_key_file)

    def generate_key(self):
        """Generates an OpenSSH key for SSH authentication.
        The key is stored in the program folder.
        """

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.logger.debug("Generating new ssh-rsa key...")
            key = RSAKey.generate(2048)
            key.write_private_key_file(Paths.private_key_file)
        elif platform == "win32":
            self.logger.debug("Generating new ssh-ed25519 key...")
            args = shlex.split(Commands.cmd_generate_ed25519_key.format(Paths.private_key_file).replace("\\", "/"))
            #args = Commands.cmd_generate_ed25519_key.format(Paths.private_key_file)
            self.logger.debug(args)
            subprocess.run(args)
            #process = Popen("cmd.exe", shell=False, universal_newlines=True,
            #      stdin=PIPE, stdout=PIPE, stderr=PIPE)
            #process.communicate(Commands.cmd_generate_ed25519_key.format(Paths.private_key_file))

    def generate_remote_ssh_key(self):
        """Generates an ssh key pair on the cluster node.
        """

        self.logger.info("Generating ssh key pair on remote node %s...", self.address)
        self.send_command(Commands.cmd_generate_cluster_key)

    def private_key_exists(self):
        """Check whether the private key file exists or not.

        Returns:
            boolean -- True, if exists, False otherwise.
        """

        if os.path.isfile(Paths.private_key_file):
            return True
        else:
            return False

    def get_private_key(self):
        """Returns the private key.
        If the key doesn't exist, None is returned.

        Returns:
            object -- The key.
        """

        if self.private_key_exists:
            if platform == "linux" or platform == "linux2" or platform == "darwin":
                return RSAKey.from_private_key_file(Paths.private_key_file)
            elif platform == "win32":
                return Ed25519Key.from_private_key_file(Paths.private_key_file)                 
        else:
            return None

    def get_public_key(self):
        """Returns the public key as string.
        If the key doesn't exist, None is returned.

        Returns:
            string -- The public key string.
        """

        p_key = None
        if self.private_key_exists():
            if platform == "linux" or platform == "linux2" or platform == "darwin":
                key = self.get_private_key()
                p_key = "ssh-rsa {}".format(key.get_base64())
            elif platform == "win32":
                with open (Paths.public_key_file, "r") as pfile:
                    key = pfile.readline().strip()
                p_key = key
        return p_key

    def get_public_key_from_remote(self):
        """Fetches the public ssh key from remote node.
        If key does not exist, an empty string will be returned.
        
        Returns:
            string -- The key.
        """

        public_key = ""

        self.logger.debug("Fetching the public ssh key from remote node %s...", self.address)
        if not self.check_cluster_key_generated():
            self.logger.debug("Remote node %s does not have ssh key yet. Generating...", self.address)
            self.generate_remote_ssh_key()

        public_key = self.send_command(Commands.cmd_get_public_key_from_node)

        return public_key.replace("\n", "")

    def close_connection(self):
        """Closes the connection to the SSH host.
        """

        if self.client != None:
            self.client.close()
