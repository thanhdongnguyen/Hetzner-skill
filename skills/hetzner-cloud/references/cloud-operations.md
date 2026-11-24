# Hetzner Cloud operations

Commands below use `hc` to mean `env -u HCLOUD_TOKEN hcloud --context CONTEXT`. Run that expanded command explicitly, or define a local shell function with the intended context:

```sh
hc() { env -u HCLOUD_TOKEN hcloud --context personal "$@"; }
```

## Inventory and provisioning

- Check `hc server list -o json` to inventory VPSs and `hc server describe SERVER -o json` for a specific server. Pass IDs to mutation commands after looking up names and labels.
- Inspect `hc location list`, `hc server-type list`, `hc server-type describe TYPE` and `hc image list --architecture x86` (or `arm`). Compare the installed CLI output and [billing terms](https://docs.hetzner.com/cloud/billing/faq/). Prices and capacity vary by location. A type can be offered at a location but temporarily out of stock. Offer alternatives before changing the location or cost agreed with the user.
- List `hc ssh-key list` and compare the selected key to `ssh-keygen -E md5 -lf KEY.pub` (ignoring the local `MD5:` prefix). If needed, register only the public key with `hc ssh-key create --name KEY_NAME --public-key-from-file KEY.pub`.
- Create using the bundled helper for a single server, or use `hc server create --help` for optional networks, volumes, IPs, backups and labels. A partial failure can leave resources created. Check the same name or returned ID and inspect its state before trying again. The helper protects newly created servers against delete and rebuild.

## Resource map

| Resource | Command group and operation |
| --- | --- |
| VPS | `server` for list, describe, power, resize, backup, snapshots and recovery |
| Images and ISOs | `image` and `iso` for OS images, snapshots, backups and rescue media |
| Public addresses | `primary-ip` to manage server addresses, `floating-ip` for movable addresses |
| Ingress | `firewall` for network rules, `load-balancer` and `load-balancer-type` for services and targets |
| Private connectivity | `network` for subnets and routes, `server attach-to-network` for membership |
| Storage and placement | `volume`, `placement-group`, `storage-box` and `storage-box-type` when available in the installed CLI |
| DNS and TLS | `zone` and `zone rrset`, `certificate` |
| Setups and lookups | `context`, `config`, `location`, `server-type`, `ssh-key`, `all list` |
| API fallback | `api` if the needed endpoint has no dedicated command; inspect `hcloud api --help` |

## Change and recovery

- **Firewall.** Inspect all inbound rules and attachment scope before editing. Preserve the operator's SSH source CIDR and verify a second SSH connection before removing earlier access rules. For a private browser VPS allow SSH from the approved source and keep the GUI port out of the inbound allow list. Read `hc firewall add-rule --help` and `hc firewall apply-to-resource --help` for syntax.
- **Power and resize.** Prefer graceful `server shutdown` for a planned stop. Check type compatibility, downtime and disk resize reversibility before `server change-type`. A powered-off server still accrues charges.
- **Backup and restore.** Use `server create-image` for snapshots and `server enable-backup` for scheduled backups when requested. Identify mounted volumes and back up their contents separately. Verify restore from a separate server when feasible. Rebuild replaces the system disk, so resolve snapshots and data recovery first.
- **Broken SSH.** Check resource state, address, firewall, SSH user and the expected client key. If needed, use the Hetzner Console's VNC console to inspect boot or retrieve the expected SSH host fingerprint. Rescue mode or reset changes the server's state and belongs in the recovery operation itself.
- **Delete.** Identify the server ID, backups, volumes and public IPs before deletion. Check which resources are configured to survive and may continue billing. Delete protected resources only after confirming the target and explicitly disabling only the applicable protection.

References: [CLI manual](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud.md), [CLI configuration and precedence](https://github.com/hetznercloud/cli/blob/main/docs/reference/configuration.md), [Hetzner Cloud API](https://docs.hetzner.cloud/).
