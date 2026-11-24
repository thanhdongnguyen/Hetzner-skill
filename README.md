# Hetzner Cloud Agent Skill

Give Codex or Claude Code a repeatable workflow for operating Hetzner Cloud with the official [`hcloud` CLI](https://github.com/hetznercloud/cli). The skill covers provisioning, SSH, Docker deployment, resource operations and an optional private Chromium session for manual sign-in.

## Install

With a recent GitHub CLI, choose your agent:

```sh
gh skill install thanhdongnguyen/Hetzner-skill hetzner-cloud --agent codex --scope user
gh skill install thanhdongnguyen/Hetzner-skill hetzner-cloud --agent claude-code --scope user
```

For manual installation, clone this repository and copy the entire `skills/hetzner-cloud` folder into `.agents/skills/` for Codex or `.claude/skills/` for Claude Code in your project. Use `~/.agents/skills/` or `~/.claude/skills/` for a user-wide installation.

## Connect to Hetzner

Install `hcloud`, OpenSSH and Python 3.8+ where your agent runs. On macOS, install the CLI with `brew install hcloud`. In [Hetzner Console](https://console.hetzner.com/), open the target project and create an API token under **Security → API tokens**. Use **Read** for inventory or **Read & Write** for provisioning. Paste the token at the terminal prompt.

```sh
hcloud context create personal
env -u HCLOUD_TOKEN hcloud --context personal server list
```

Register your SSH public key in that project before provisioning. Keep the API token and SSH private key in the environment that needs them.

## Use it

In Codex, invoke `$hetzner-cloud`. In Claude Code, invoke `/hetzner-cloud`. For example:

> Check which VPSs exist in my `personal` Hetzner project and summarize their status.

> Plan an Ubuntu 24.04 VPS in Singapore for an always-on agent. Include SSH access, Docker and a private Chromium browser for manual login. Check the current price and availability.

You can also run the provisioning helper directly from the repository root. Replace the example type and key with values you verified in your project.

```sh
python3 skills/hetzner-cloud/scripts/provision.py \
  --context personal --name agent-vps --type cpx22 --location sin \
  --image ubuntu-24.04 --ssh-key my-ssh-key \
  --user-data skills/hetzner-cloud/assets/cloud-init/ubuntu-24.04-docker.yaml
```

This prints a read-only plan. Add `--apply` to create the VPS, then follow the SSH and verification steps. Hetzner bills for the VPS while it exists. Add `--firewall` to attach an existing firewall when creating the server.

See [the skill](skills/hetzner-cloud/SKILL.md), [cloud operations](skills/hetzner-cloud/references/cloud-operations.md), [VPS setup](skills/hetzner-cloud/references/vps-setup.md) and [remote browser setup](skills/hetzner-cloud/references/remote-browser.md) for the full workflows.
