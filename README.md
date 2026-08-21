# Ansible Proxmox Autosnap Setup

Ansible playbook that installs and configures [cv4pve-autosnap](https://github.com/Corsinvest/cv4pve-autosnap) on a Proxmox VE node.

The playbook creates a least-privilege Proxmox service account, installs the pinned binary, and configures a scheduled snapshot command.

## Quick start

Requirements:

- supported Proxmox VE node;
- root SSH access;
- outbound HTTPS access to GitHub;
- `unzip` (installed by the playbook when missing).

Run with an interactive SSH password:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml
```

The playbook does not create or require SSH keys. An operator may provide a key separately with Ansible's normal SSH options.

Current pinned release: [`2.1.1`](setup.yml#L9). The version is pinned in `setup.yml`; override it explicitly with `-e cv4pve_autosnap_version=X.Y.Z`.

## Main parameters

Edit the variables in `setup.yml`, or override them with `-e`:

```yaml
cv4pve_autosnap_version: "2.1.1"
cv4pve_autosnap_vmid: "@all"
cv4pve_autosnap_label: cron
cv4pve_autosnap_keep: 4
cv4pve_autosnap_only_running: true
cv4pve_autosnap_hour: "20"
cv4pve_autosnap_minute: "55"
cv4pve_autosnap_user: autosnap@pve
cv4pve_autosnap_token_id: autosnap
```

`cv4pve_autosnap_only_running: true` is the default. The scheduled command then adds `--only-running` after `snap`. Set it to `false` to include stopped guests.

`cv4pve_autosnap_keep` is the retention count per VM/CT and label. For example, `4` keeps the four newest `cron` snapshots for each guest and removes older matching snapshots when the `snap` command runs.

`cv4pve_autosnap_hour` and `cv4pve_autosnap_minute` are the cron schedule fields. The default `20` and `55` runs every day at `20:55`. To run every three hours at minute `55`, use `cv4pve_autosnap_hour: "*/3"` and `cv4pve_autosnap_minute: "55"`.

## VM/CT selection examples

The `--vmid` value is passed to `cv4pve-autosnap`. Use these patterns in `cv4pve_autosnap_vmid` or as a direct command option:

| Goal | Value |
| --- | --- |
| All VMs and containers | `@all` |
| Only guests 102, 104, and 106 | `102,104,106` |
| All guests except 100 and 104 | `@all,-100,-104` |
| Guests in a pool | `@pool-production` |
| Guests with a tag | `@tag-production` |
| Guest names or IDs | `web-server,102` |

The scheduled cron command uses these values from `setup.yml`. Override them with `-e`:

All VMs and containers, running guests only:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_vmid=@all' -e 'cv4pve_autosnap_only_running=true'
```

Only guests 102, 104, and 106. Guest 105 is excluded:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_vmid=102,104,106'
```

All guests except 100 and 104:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_vmid=@all,-100,-104'
```

Every three hours at minute 55:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_hour=*/3' -e 'cv4pve_autosnap_minute=55'
```

To include stopped guests, use `-e 'cv4pve_autosnap_only_running=false'`.

For a manual snapshot, use the generated cron arguments after `@/etc/pve/priv/cv4pve-autosnap.conf`; `--only-running` must come after `snap`:

```bash
/usr/local/bin/cv4pve-autosnap @/etc/pve/priv/cv4pve-autosnap.conf --vmid=@all snap --only-running --label=cron --keep=4
```

## Proxmox account and token

When absent, the playbook creates:

- service user: `autosnap@pve`;
- privilege-separated API token: `autosnap@pve!autosnap`;
- least-privilege role: `AutoSnap`.

The token configuration is stored at `/etc/pve/priv/cv4pve-autosnap.conf` with mode `0600`. The token secret is returned only during initial creation, is never printed or stored in the repository, and is never regenerated. An empty existing token configuration causes a safe failure.

Role permissions:

```text
VM.Audit
VM.Snapshot
Datastore.Audit
Pool.Audit
```

## Installed files and schedule

```text
/usr/local/bin/cv4pve-autosnap
/etc/pve/priv/cv4pve-autosnap.conf
/etc/cron.d/10-autosnap-px
```

Default schedule:

```cron
55 20 * * *
```

Snapshots are not backups. Test restore procedures separately.

## Verification and development

The playbook verifies the installed binary version and supports repeated runs without regenerating the API token.

Local checks:

```bash
uv run --with yamllint yamllint .
uv run --with ansible-lint ansible-lint setup.yml
uv run --with ansible-core ansible-playbook -i tests/fixtures/inventory.ini --syntax-check setup.yml
```

Use a disposable VM or container for real snapshot tests. Use an external Proxmox snapshot to restore a clean test state when needed.
