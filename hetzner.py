#!/usr/bin/env -S uv run -q
import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen

import configargparse
import yaml
from decouple import config
from dotenv import load_dotenv
from hcloud import Client
from hcloud.images import Image
from hcloud.locations import Location
from hcloud.server_types import ServerType
from hcloud.servers import Server

import settings

load_dotenv()

HETZNER_TOKEN = config("HETZNER_TOKEN")
PROJECT_NAME = config("AUTODEV_PROJECT_NAME", default="autodev")
SSH_KEYS_URL = config("AUTODEV_SSH_KEYS_URL", default=settings.SSH_KEYS_URL)
TS_AUTH_KEY = config("TS_AUTH_KEY")
OS_IMAGE = config("OS_IMAGE", default="ubuntu-24.04")

def get_client():
    return Client(token=HETZNER_TOKEN)


def read_cloud_init():
    script_path = Path(__file__).parent / "cloud-init.yaml"
    return script_path.read_text()


def fetch_ssh_keys(url):
    data = urlopen(url).read().decode("utf-8")
    keys = [line.strip() for line in data.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not keys:
        raise ValueError("No SSH public keys found at AUTODEV_SSH_KEYS_URL")
    return keys


def create_vm(args):
    client = get_client()
    cloud_init = read_cloud_init()

    location = Location(name=args.location)
    server_type = ServerType(name=args.instance_type)
    image = Image(name=OS_IMAGE)

    data = yaml.safe_load(cloud_init)
    keys = fetch_ssh_keys(SSH_KEYS_URL)
    users = data.get("users", [])
    for user in users:
        user["ssh_authorized_keys"] = keys

    # Dump back to YAML and keep cloud-config header
    dumped = yaml.safe_dump(data, sort_keys=False)
    user_data = "#cloud-config\n" + dumped
    user_data = user_data.replace("TS_AUTH_KEY", TS_AUTH_KEY)
    print(user_data)

    response = client.servers.create(
        name=f"{PROJECT_NAME}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        server_type=server_type,
        image=image,
        location=location,
        user_data=user_data,
        networks=[] if args.network_type == "ipv4" else None,
    )

    server = response.server
    print(f"Created VM: {server.name}")
    print(f"IP: {server.public_net.ipv4.ip}")
    print(f"Status: {server.status}")


def destroy_vm(args):
    client = get_client()
    server = client.servers.get_by_name(args.name)
    if not server:
        print(f"VM '{args.name}' not found", file=sys.stderr)
        sys.exit(1)
    server.delete()
    print(f"Destroyed VM: {args.name}")


def cleanup_vms(args):
    client = get_client()
    cutoff_time = datetime.now() - timedelta(hours=args.hours)
    cutoff_timestamp = cutoff_time.timestamp()

    servers = client.servers.get_all()
    destroyed_count = 0

    for server in servers:
        if not server.name.startswith(f"{PROJECT_NAME}-"):
            continue

        created_timestamp = server.created.timestamp()
        if created_timestamp < cutoff_timestamp:
            print(f"Destroying {server.name} (created {server.created})")
            server.delete()
            destroyed_count += 1

    print(f"Destroyed {destroyed_count} VM(s)")


def main():
    parser = configargparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument(
        "--location", default=settings.LOCATION, help="Hetzner location"
    )
    create_parser.add_argument(
        "--instance-type",
        default=settings.INSTANCE_TYPE,
        help="Instance type",
    )
    create_parser.add_argument(
        "--network-type",
        default=settings.NETWORK_TYPE,
        choices=["ipv4", "ipv6"],
        help="Network type",
    )

    destroy_parser = subparsers.add_parser("destroy")
    destroy_parser.add_argument("name", help="VM name to destroy")

    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.add_argument(
        "--hours",
        type=int,
        default=settings.CLEANUP_HOURS,
        help="Destroy VMs older than this many hours",
    )

    args = parser.parse_args()

    if args.command == "create":
        create_vm(args)
    elif args.command == "destroy":
        destroy_vm(args)
    elif args.command == "cleanup":
        cleanup_vms(args)


if __name__ == "__main__":
    main()
