# Ansible Proxmox Setup
## How to use

Install Ansible:

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
- `utente` it's the name of the new user created with the admin privileges