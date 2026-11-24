# Private remote Chromium

This optional deployment runs Chromium on the VPS. Access its GUI through an SSH tunnel and let the operator handle login and MFA. The browser keeps its profile in a Docker volume across ordinary container restarts and replacements.

1. Confirm Docker Compose works on the VPS. Inspect the Hetzner firewall and allow only the required ingress; the browser connection uses the existing SSH port. Keep the GUI and any browser debugging endpoint off the public network.
2. Create a stable VPS directory such as `/opt/remote-browser` and copy `assets/remote-browser/compose.yaml` into it. Use the same directory or Compose project name for future updates so the volume is reused. From that directory on the VPS:

   ```sh
   (umask 077; test -s browser-password || openssl rand -hex 32 | tr -d '\n' > browser-password)
   docker compose config --quiet
   docker compose up -d
   docker compose ps
   ```

   Put the GUI password in the operator's password manager via a private channel. `operator` is the default login name. `BROWSER_USER` overrides it and `CHROMIUM_IMAGE` can select a tested image tag or digest. The password file stays alongside the Compose file on the VPS.

3. On the operator's Mac, keep this SSH session open using the account authorized for port forwarding:

   ```sh
   ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:13001:127.0.0.1:3001 vps-user@VPS_IP
   ```

   Open `https://localhost:13001` in a local browser. The container serves HTTPS with a self-signed certificate by default. After verifying the tunnel and the endpoint, use the GUI credentials and complete login inside the remote Chromium window. The website's session is created in the remote Chromium profile.

4. Verify the GUI loads through the tunnel and that the same browser profile appears when reconnecting. Check `docker compose logs --tail=100 chromium` if the GUI fails. Preserve the `chromium-profile` volume when updating, and treat it as sensitive session data.

Agent control requires a browser integration supported by the chosen runtime. If the runtime can attach to this existing Chromium session, follow its documented private connection method and verify it can see the same window and session without a separate login. A separate browser process or profile generally has a separate session. Hand over control during manual authentication, then resume automation after the operator finishes.

Reference: [LinuxServer Chromium image](https://docs.linuxserver.io/images/docker-chromium/).
