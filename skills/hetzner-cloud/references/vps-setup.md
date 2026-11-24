# VPS setup and deployment

Use `hcloud` to look up the server and OpenSSH to work inside it. The API token identifies the project. OpenSSH authenticates the operator to the guest separately.

## First connection

```sh
env -u HCLOUD_TOKEN hcloud --context personal server describe agent-vps
env -u HCLOUD_TOKEN hcloud --context personal server ip agent-vps
env -u HCLOUD_TOKEN hcloud --context personal server ssh agent-vps -- -i ~/.ssh/hcloud -o IdentitiesOnly=yes
```

The CLI's SSH helper resolves the address and runs the local SSH client. Replace the key path and pass `--user USER` before the server name if the image or your configuration uses a user other than `root`. Validate the host key on the first connection using a trusted channel such as the server console. On an unexpected change, investigate the change before accepting a replacement.

For a fresh Ubuntu 24.04 server created with the Docker cloud-init template, run on the VPS:

```sh
cloud-init status --wait
systemctl is-active docker
docker compose version
```

Use `sudo` when required. Package installation is a first-boot task, so the server can accept SSH before Docker is ready. Inspect `journalctl -u cloud-final -b` and `/var/log/cloud-init-output.log` if cloud-init reports errors. For an existing Ubuntu 24.04 host, inspect its current Docker packages first. If Docker is absent and installation is authorized, Ubuntu provides `docker.io` and `docker-compose-v2` through its package repositories.

## Launch a persistent service

1. Inspect the chosen application's supported installation, image, architecture, ports, health endpoint and state directories. Use the application's architecture-specific instructions and pin the intended deployment version when possible.
2. Put the Compose project in a stable directory owned by the operator, such as `/opt/agent-stack`. Bind UI ports to loopback unless public reachability is part of the task. Store runtime credentials out of Git and cloud-init. Map persistent state to a volume or directory, and set the service to restart under Docker or systemd.
3. Verify the Compose config with `docker compose config --quiet`, start with `docker compose up -d`, then inspect `docker compose ps`, `docker compose logs --tail=100` and the application's health endpoint. Test through the same channel the user will use. For a systemd deployment, check `systemctl status UNIT` and `journalctl -u UNIT` instead.
4. Before an update, record the running application version and how to restore its data. Use the same Compose project and volume when redeploying. Coordinate any restart if the service is already in use.

For an agent with a browser, verify the agent, browser and operator access separately. A healthy container alone does not prove the agent can use a browser profile.
