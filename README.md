# Ansible Proxmox Autosnap Setup

Ansible playbook that installs and configures
[cv4pve-autosnap](https://github.com/Corsinvest/cv4pve-autosnap) on a Proxmox VE node.

The playbook creates a dedicated Proxmox service user, a least-privilege role, an API token, and a cron job that snapshots all VMs and containers.

## Behavior

- Default `cv4pve-autosnap` version is pinned in `setup.yml`.
- Current pinned version: [`2.1.1`](setup.yml#L9).
- Override the version explicitly with `-e cv4pve_autosnap_version=X.Y.Z`.
- No automatic upgrade to an unknown release.
- Re-running the playbook is supported.
- Existing API token is preserved and never regenerated.
- An empty existing token parameter file causes a safe failure.
- The selected binary is installed directly at `/usr/local/bin/cv4pve-autosnap`.
- Scheduled snapshots target running VMs and containers only by default.
- The API token parameter file is stored at `/etc/pve/priv/cv4pve-autosnap.conf` with mode `0600`.
- VM selection defaults to all VMs and containers with `--vmid=@all`.

Snapshots are not backups. Test restore procedures separately.

## Requirements

The target must be a supported Proxmox VE node with:

- root SSH access;
- outbound HTTPS access to GitHub;
- Proxmox API enabled;
- at least one VM or container for an end-to-end snapshot test.

The playbook installs `unzip` when needed.

## Run with SSH password

The IP is supplied as an inline Ansible inventory. `-k` asks for the SSH password interactively and keeps it out of the command line and repository:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml
```

The playbook does not require SSH keys.

## Override version and snapshot settings

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e cv4pve_autosnap_version=2.1.1 -e cv4pve_autosnap_vmid=@all -e cv4pve_autosnap_keep=4 -e cv4pve_autosnap_label=daily -e cv4pve_autosnap_only_running=true
```

Other supported variables:

```yaml
cv4pve_autosnap_version: "2.1.1"
cv4pve_autosnap_vmid: "@all"
cv4pve_autosnap_label: daily
cv4pve_autosnap_keep: 4
cv4pve_autosnap_only_running: true
cv4pve_autosnap_hour: "20"
cv4pve_autosnap_minute: "55"
cv4pve_autosnap_user: autosnap@pve
cv4pve_autosnap_token_id: autosnap
```

## Permissions

The generated `AutoSnap` role contains only:

```text
VM.Audit
VM.Snapshot
Datastore.Audit
Pool.Audit
```

## Proxmox service account and API token

The playbook creates the following Proxmox credentials when they do not already exist:

- service user: `autosnap@pve`;
- privilege-separated API token: `autosnap@pve!autosnap`;
- token configuration: `/etc/pve/priv/cv4pve-autosnap.conf` with mode `0600`.

The token secret is returned only during its initial creation. The playbook does not print it, store it in the repository, or regenerate it on later runs. If the existing token configuration is empty, the playbook stops instead of overwriting it.

The token uses Proxmox privilege separation and is granted the least-privilege `AutoSnap` role.

## Verification

The playbook verifies the installed binary version and configures:

```text
/etc/pve/priv/cv4pve-autosnap.conf
/etc/cron.d/10-autosnap-px
```

Manual status check:

```bash
ssh root@192.168.129.1 /usr/local/bin/cv4pve-autosnap @/etc/pve/priv/cv4pve-autosnap.conf --vmid=@all status
```

Direct snapshot command, explicitly limited to running VMs and containers:

```bash
/usr/local/bin/cv4pve-autosnap @/etc/pve/priv/cv4pve-autosnap.conf --vmid=@all snap --only-running --label=daily --keep=4
```

Before testing a real snapshot, create a disposable VM or container. Verify the QEMU Guest Agent and application consistency separately.

## Development checks

Syntax check:

```bash
uv run --with ansible-core ansible-playbook --syntax-check setup.yml
```

Test on the dedicated Proxmox instance first. Use its Proxmox snapshot to restore a clean state between destructive experiments.
