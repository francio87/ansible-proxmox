# Ansible Proxmox Setup

Dumb ansible playbook to prep Proxmox Host, using [cv4pve-autosnap](https://github.com/Corsinvest/cv4pve-autosnap).

## Register Proxmox from the GUI

Make sure that Proxmox, is registered so we can get access to the `Enterprise repository`

## Install Ansible on your PC

Debian / Ubuntu

```
sudo apt install ansible git python3-paramiko
```

Fedora

```
sudo dnf install ansible git python3-paramiko
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
