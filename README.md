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

Playbook defaults:

```yaml
cv4pve_autosnap_vmid: "@all"
cv4pve_autosnap_label: cron
cv4pve_autosnap_keep: 4
cv4pve_autosnap_only_running: true
cv4pve_autosnap_hour: "20"
cv4pve_autosnap_minute: "55"
```

`cv4pve_autosnap_keep` keeps the newest matching snapshots per VM/CT and label. `cv4pve_autosnap_only_running: true` excludes stopped guests; set it to `false` to include them.

`cv4pve_autosnap_hour` and `cv4pve_autosnap_minute` accept standard cron syntax: `*`, `*/N`, lists, and ranges. Quote values containing `*` in shell commands.

### Modify `setup.yml`

Example: snapshot guests `102`, `104`, and `106` every three hours at minute 55:

```yaml
cv4pve_autosnap_vmid: "102,104,106"
cv4pve_autosnap_only_running: true
cv4pve_autosnap_hour: "*/3"
cv4pve_autosnap_minute: "55"
```

Example: snapshot all guests except `100` and `104` every 30 minutes:

```yaml
cv4pve_autosnap_vmid: "@all,-100,-104"
cv4pve_autosnap_only_running: true
cv4pve_autosnap_hour: "*"
cv4pve_autosnap_minute: "*/30"
```

Example: snapshot all guests once daily at 02:30, including stopped guests:

```yaml
cv4pve_autosnap_vmid: "@all"
cv4pve_autosnap_only_running: false
cv4pve_autosnap_hour: "2"
cv4pve_autosnap_minute: "30"
```

Apply changes:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml
```

### Override at launch

Use the same variables with `-e`, without editing the file:

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_vmid=102,104,106' -e 'cv4pve_autosnap_only_running=true' -e 'cv4pve_autosnap_hour=*/3' -e 'cv4pve_autosnap_minute=55'
```

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_vmid=@all,-100,-104' -e 'cv4pve_autosnap_hour=*' -e 'cv4pve_autosnap_minute=*/30'
```

```bash
ansible-playbook -i '192.168.129.1,' -u root -k setup.yml -e 'cv4pve_autosnap_vmid=@all' -e 'cv4pve_autosnap_only_running=false' -e 'cv4pve_autosnap_hour=2' -e 'cv4pve_autosnap_minute=30'
```

VM/CT selection values:

| Goal | `cv4pve_autosnap_vmid` |
| --- | --- |
| All VMs and containers | `@all` |
| Only guests 102, 104, and 106 | `102,104,106` |
| All guests except 100 and 104 | `@all,-100,-104` |
| Guests in a pool | `@pool-production` |
| Guests with a tag | `@tag-production` |

The playbook renders these variables into `/etc/cron.d/10-autosnap-px`. The default generated schedule is:

```cron
55 20 * * *
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

The playbook checks `/usr/local/bin/cv4pve-autosnap --version` before contacting GitHub. When the installed version matches the pinned version, it skips release lookup, archive download, extraction, and replacement. The only persistent autosnap executable is `/usr/local/bin/cv4pve-autosnap`; ZIP, extraction, and other staging files are used only under `/tmp` during updates and removed after successful installation and verification. The final task verifies the installed binary version and repeated runs do not regenerate the API token.

Local checks:

```bash
uv run --with yamllint yamllint .
uv run --with ansible-lint ansible-lint setup.yml
uv run --with ansible-core ansible-playbook -i tests/fixtures/inventory.ini --syntax-check setup.yml
```

Use a disposable VM or container for real snapshot tests. Use an external Proxmox snapshot to restore a clean test state when needed.
