---
name: hetzner-cloud
description: Manage Hetzner Cloud VPS and infrastructure with the official hcloud CLI. Use when asked to inspect, provision, configure, SSH into, deploy to, troubleshoot, resize, back up, or remove Hetzner Cloud servers, or to run an agent and a persistent remote browser on a Hetzner VPS.
---

# Hetzner Cloud

Use `hcloud` for project resources and OpenSSH for the guest OS. Locate bundled files relative to this `SKILL.md`. Run local commands in the environment that has the CLI and SSH credentials.

1. Identify the target project and operation. Run `hcloud version` and `hcloud context list`, then inspect resources with `env -u HCLOUD_TOKEN hcloud --context CONTEXT server list`. An exported `HCLOUD_TOKEN` overrides a context's token. For headless runs that intentionally use an environment token, inject it through the runner's secret store and keep that mode separate from named contexts. Avoid printing credentials or the CLI config.
2. For inventory or operations on existing resources, read [Cloud operations](references/cloud-operations.md). Verify the exact resource ID, location and state before edits. Use `hcloud GROUP COMMAND --help` for flags supported by the installed version.
3. For a new server, identify the server type, location, image, registered SSH public key and any required firewall. Check region availability and cost, including public IPv4 or other extras. Run `python3 scripts/provision.py` with the selected inputs to produce a read-only plan. Add `--apply` when the user has authorized creation. If a server already matches, reuse it. Investigate an interrupted create by querying the same name in the same project before retrying.
4. To configure the guest, read [VPS setup and deployment](references/vps-setup.md). For a fresh Ubuntu 24.04 server, [`assets/cloud-init/ubuntu-24.04-docker.yaml`](assets/cloud-init/ubuntu-24.04-docker.yaml) is an optional bootstrap. For an existing host, inventory its users, packages and services before changing anything. Verify SSH host identity and check `cloud-init` before deploying.
5. For manual sign-in on a VPS browser, use [Remote browser](references/remote-browser.md) with the optional [Chromium Compose template](assets/remote-browser/compose.yaml). The operator signs in through a private SSH tunnel. Check the selected agent runtime's documented browser integration before promising it can control that same profile.
6. Verify the requested outcome from the appropriate layer: Hetzner resource state, SSH connectivity, then service health or application response. Report the context, server identity, what changed, how to access it, and any checks that remain.

Treat delete, rebuild, firewall changes that can cut off access, and recovery actions as separate operations. Apply them only when the request covers their effects, and identify data and attached resources before proceeding. If provisioning fails after the API may have created a server, inspect first and preserve the resource for diagnosis.
