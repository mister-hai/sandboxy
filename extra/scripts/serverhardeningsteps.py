#harden ssh
addtofile={"thing1":
    ["/etc/ssh/sshd_config",
    """
Protocol2
IgnoreRhosts to yes
HostbasedAuthentication no
PermitEmptyPasswords no
X11Forwarding no
MaxAuthTries 5
Ciphers aes128-ctr,aes192-ctr,aes256-ctr
ClientAliveInterval 900
ClientAliveCountMax 0
UsePAM yes
"""
    ]
}

command="chown root:root /etc/ssh/sshd_config"
command = "chmod 600 /etc/ssh/sshd_config"