# Ansible Proxmox Setup

## Register Proxmox from the GUI

Make sure that Proxmox, is registered so we can get accesso to the `Enterprise repository`

## Install Ansible on your PC

Debian / Ubuntu

```
sudo apt install ansible
```

Fedora

```
sudo dnf install ansible
```

Run `ansible-playbook` :

```
ansible-playbook -i "192.168.110.83," -c paramiko -k -u root setup.yml --extra-vars "myuser=utente"
```
Where:
- `192.168.110.83` it's the ip address of Proxmox Host, do not remove the ending  `,`
- `utente` it's the name of the new user created with the admin privileges, the password for the account will be random generated.

Example:

```
TASK [Done!] *************************************************************************************************************************************************
ok: [192.168.110.83] => {
    "msg": [
        "An additional user has been create with Administrator privileges.",
        "Username : utente",
        "Password : yojVRNpyWFkHhAy",
        "A new cron file has been generated to automate the daily vm snapshot",
        "located at : /etc/cron.d/10-autosnap-px",
        ""
    ]
}
```
