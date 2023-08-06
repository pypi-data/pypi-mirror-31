"""This module encapsulates constants."""

from pathlib import Path

class Commands:
    """This class holds many shell commands.

    You can use this class to access many constant shell commands.
    """

    cmd_echo = "echo hello"
    cmd_ipforward = "sudo sysctl -w net.ipv4.ip_forward=1"
    cmd_check_key = "grep -q '{}' ~/.ssh/authorized_keys && echo $?"
    cmd_check_key_cluster = "[ -f ~/.ssh/id_rsa ] && echo 'found' || echo 'not found'"
    cmd_get_public_key_from_node = 'echo "$(cat ~/.ssh/id_rsa.pub)"'
    cmd_generate_ed25519_key = 'ssh-keygen -f {} -t ed25519 -N ""'
    cmd_start_client = "sudo python3 -m netconflib -sniff {} {}"
    cmd_start_shell_win = "start cmd /c ssh -i {} pi@{}"
    cmd_start_shell_lin = "gnome-terminal -x ssh -i {} pi@{}"
    cmd_start_shell_mac = 'tell application "Terminal" to do script "ssh -i {} pi@{}"'
    cmd_generate_cluster_key = "ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa"
    cmd_add_key_to_authorized_keys = "umask 077 && mkdir -p ~/.ssh && echo '{}' >> ~/.ssh/authorized_keys"

    quit_string = "--QUIT--"

class Paths:
    """This class holds all the paths.
    """

    home = Path.home()
    program_home = home / "netconflib"
    config_file = str(program_home / "config.ini")
    config_file_test = str(program_home / "config_test.ini")
    config_file_test_programfolder = "tests/config.ini"
    private_key_file = str(program_home / "key")
    public_key_file = str(program_home / "key.pub")
    log_file = str(program_home / "app.log")
    log_file_test = str(program_home / "test.log")