# Ansible Proxmox Autosnap Setup

Ansible playbook that installs and configures
[cv4pve-autosnap](https://github.com/Corsinvest/cv4pve-autosnap) on a Proxmox VE node.

The playbook creates a dedicated Proxmox service user, a least-privilege role, an API token, and a cron job that snapshots all VMs and containers.

## Behavior

- Default `cv4pve-autosnap` version is pinned in `setup.yml`.
- Current pinned version: `2.1.1`.
- Override the version explicitly with `-e cv4pve_autosnap_version=X.Y.Z`.
- No automatic upgrade to an unknown release.
- Re-running the playbook is supported.
- Existing API token is preserved and never regenerated.
- An empty existing token parameter file causes a safe failure.
- Binary releases are kept under `/usr/local/libexec/cv4pve-autosnap/<version>`.
- `/usr/local/bin/cv4pve-autosnap` points to the selected version.
- The API token parameter file is stored at `/etc/pve/priv/cv4pve-autosnap.conf` with mode `0600`.
- Snapshots target all VMs and containers by default with `--vmid=@all`.

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
ansible-playbook \
  -i '192.168.129.1,' \
  -u root \
  -k \
  setup.yml
```

The playbook does not require SSH keys. A key can be used instead for automation or development:

```bash
ansible-playbook \
  -i '192.168.129.1,' \
  -u root \
  --private-key ~/.ssh/proxmox-test \
  setup.yml
```

## Override version and snapshot settings

```bash
ansible-playbook \
  -i '192.168.129.1,' \
  -u root \
  -k \
  setup.yml \
  -e cv4pve_autosnap_version=2.1.1 \
  -e cv4pve_autosnap_vmid=@all \
  -e cv4pve_autosnap_keep=4 \
  -e cv4pve_autosnap_label=daily
```

Other supported variables:

```yaml
cv4pve_autosnap_version: "2.1.1"
cv4pve_autosnap_vmid: "@all"
cv4pve_autosnap_label: daily
cv4pve_autosnap_keep: 4
cv4pve_autosnap_hour: "20"
cv4pve_autosnap_minute: "55"
cv4pve_autosnap_user: autosnap@pve
cv4pve_autosnap_token_id: daily
```

## Permissions

The generated `AutoSnap` role contains only:

```text
VM.Audit
VM.Snapshot
Datastore.Audit
Pool.Audit
```

The token uses Proxmox privilege separation. The token secret is returned only during creation, so the playbook refuses to overwrite or recreate it automatically.

## Verification

The playbook verifies the installed binary version and configures:

```text
/etc/pve/priv/cv4pve-autosnap.conf
/etc/cron.d/10-autosnap-px
```

Manual status check:

```bash
ssh root@192.168.129.1 \
  /usr/local/bin/cv4pve-autosnap \
  @/etc/pve/priv/cv4pve-autosnap.conf \
  --vmid=@all \
  status
```

Before testing a real snapshot, create a disposable VM or container. Verify the QEMU Guest Agent and application consistency separately.

## Development checks

Syntax check:

```bash
uv run --with ansible-core ansible-playbook --syntax-check setup.yml
```

Test on the dedicated Proxmox instance first. Use its Proxmox snapshot to restore a clean state between destructive experiments.
