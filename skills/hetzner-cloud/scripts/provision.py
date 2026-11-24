#!/usr/bin/env python3
"""Plan or create a single Hetzner Cloud server in an explicit context."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, help="Named hcloud context")
    parser.add_argument("--name", required=True, help="Unique lowercase server name")
    parser.add_argument("--type", required=True, help="Hetzner server type name")
    parser.add_argument("--location", required=True, help="Hetzner location name")
    parser.add_argument("--image", required=True, help="Image name or numeric ID")
    parser.add_argument("--ssh-key", required=True, help="Registered SSH key name or ID")
    parser.add_argument("--firewall", help="Existing firewall name or ID to attach")
    parser.add_argument("--user-data", type=Path, help="Optional non-secret cloud-init file")
    parser.add_argument("--apply", action="store_true", help="Create if no matching server exists")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?", args.name):
        parser.error("--name must be 1–63 lowercase letters, digits or hyphens and start with a letter")
    for option in ("type", "location", "image", "ssh_key", "firewall"):
        value = getattr(args, option)
        if value is not None and (not value.strip() or value.startswith("-")):
            parser.error(f"--{option.replace('_', '-')} must be a resource name or ID, not an option")
    if args.user_data and (not args.user_data.is_file() or args.user_data == Path("-")):
        parser.error("--user-data must be a readable file path other than '-'")
    return args


def run(command, env, *, capture=True):
    result = subprocess.run(command, env=env, text=True, check=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout


def matches_reference(resource, reference):
    if not resource:
        return False
    return reference in (resource.get("name"), str(resource.get("id")))


def matching_server(server, args, firewall):
    location = server.get("location") or (server.get("datacenter") or {}).get("location") or {}
    actual = {"type": (server.get("server_type") or {}).get("name"), "location": location.get("name")}
    conflicts = [f"{key}: {actual[key]!r}" for key in actual if actual[key] != getattr(args, key)]
    if not matches_reference(server.get("image"), args.image):
        conflicts.append("image differs or is no longer reported")
    public_net = server.get("public_net") or {}
    applied_firewalls = {item.get("id") for item in (public_net.get("firewalls") or [])
                         if item.get("status") == "applied"}
    if firewall and firewall["id"] not in applied_firewalls:
        conflicts.append("requested firewall is not applied")
    if conflicts:
        raise ValueError(f"Server {server['id']} already uses this name with different settings: " + ", ".join(conflicts))
    return {
        "action": "reuse",
        "context": args.context,
        "id": server["id"],
        "name": server["name"],
        "status": server["status"],
        "ipv4": (public_net.get("ipv4") or {}).get("ip"),
        "note": "SSH keys and user data are only injected at creation. Verify guest access separately.",
    }


def provision(args):
    env = os.environ.copy()
    env.pop("HCLOUD_TOKEN", None)
    cli = ["hcloud", f"--context={args.context}"]

    def read_json(*parts):
        return json.loads(run([*cli, *parts, "-o", "json"], env))

    servers = read_json("server", "list")
    firewall = read_json("firewall", "describe", args.firewall) if args.firewall else None
    for server in servers:
        if server.get("name") == args.name:
            print(json.dumps(matching_server(server, args, firewall), indent=2))
            return

    run([*cli, "ssh-key", "describe", "--", args.ssh_key], env)
    run([*cli, "location", "describe", "--", args.location], env)
    server_type = read_json("server-type", "describe", args.type)
    locations = {entry.get("name", entry.get("location")) for entry in (server_type.get("locations") or [])}
    prices = {entry["location"]: entry for entry in (server_type.get("prices") or [])}
    if (locations or prices) and args.location not in (locations or prices):
        raise ValueError(f"{args.type} is not offered in {args.location}")
    architecture = server_type["architecture"]
    images = read_json("image", "list", f"--architecture={architecture}")
    if not any(matches_reference(image, args.image) and not image.get("deprecated") for image in images):
        raise ValueError(f"No current {architecture} image matches {args.image!r}")

    create = [*cli, "server", "create", f"--name={args.name}", f"--type={args.type}",
              f"--location={args.location}", f"--image={args.image}", f"--ssh-key={args.ssh_key}",
              "--enable-protection=delete,rebuild"]
    if args.firewall:
        create.append(f"--firewall={args.firewall}")
    if args.user_data:
        create.append(f"--user-data-from-file={args.user_data.resolve()}")
    print(json.dumps({"action": "create" if args.apply else "plan", "context": args.context,
                      "server_type_price": prices.get(args.location),
                      "command": shlex.join(["env", "-u", "HCLOUD_TOKEN", *create]),
                      "note": "Server type pricing excludes separately billed resources such as public IPv4."},
                     indent=2), flush=True)
    if args.apply:
        run(create, env, capture=False)


if __name__ == "__main__":
    try:
        provision(arguments())
    except subprocess.CalledProcessError as error:
        print(f"hcloud returned status {error.returncode}. If creation was attempted, inspect the server by name before retrying.", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Unable to finish provisioning: {error}", file=sys.stderr)
        sys.exit(1)
