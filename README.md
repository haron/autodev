# autodev

Personal environment for agent-assisted development using throwaway virtual machines on Hetzner Cloud.

## Quick Start

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create `.env` file:
   ```bash
   HETZNER_TOKEN=your-api-token-here
   AUTODEV_PROJECT_NAME=your-project-name
   AUTODEV_SSH_KEYS_URL=https://github.com/haron.keys
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```

3. Create a VM:
   ```bash
   ./hetzner.py create
   ```

4. Provision the VM:
   ```bash
   ./provision.yaml -i <vm-ip-or-hostname>
   ```

## Usage

### Creating VMs

Create a new VM with default settings:
```bash
./hetzner.py create
```

Customize VM creation:
```bash
./hetzner.py create --location hel1 --instance-type cx23 --network-type ipv4
```

The VM will be automatically configured via cloud-init with:
- SSH keys from the configured URL
- Development tools (git, tailscale, ripgrep, mosh, tmux, vim, neovim, etc.)
- Python 3 and UV
- Claude CLI

### Managing VMs

Destroy a specific VM:
```bash
./hetzner.py destroy <vm-name>
```

Cleanup old VMs (default: older than 24 hours):
```bash
./hetzner.py cleanup --hours 24
```

### Telegram Notifications

Send a simple message:
```bash
./telegram.py Your message here
```

With options:
```bash
./telegram.py --chat-id <chat-id> Your message here
```

### Provisioning

After creating a VM, provision it with Ansible:
```bash
./provision.yaml -i <vm-ip-or-hostname>
```

This will:
- Create the `autodev` user
- Set bash as the shell
- Install the cleanup cron task

## Configuration

All configuration is done via environment variables in `.env`:

- `HETZNER_TOKEN` - Hetzner Cloud API token (required)
- `AUTODEV_PROJECT_NAME` - Project name prefix for VMs (default: "autodev")
- `AUTODEV_SSH_KEYS_URL` - URL to fetch SSH public keys from (default: https://github.com/haron.keys)
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (required for telegram.py)
- `TELEGRAM_CHAT_ID` - Telegram chat ID (required for telegram.py)

Default VM settings can be changed in `settings.py`:
- `LOCATION` - Hetzner data center (default: "hel1")
- `INSTANCE_TYPE` - VM instance type (default: "cx23")
- `NETWORK_TYPE` - Network type (default: "ipv4")
- `CLEANUP_HOURS` - Hours before cleanup (default: 24)
- `SSH_KEYS_URL` - Default SSH keys URL

## Workflow

1. Create a VM: `./hetzner.py create`
2. Note the IP address from the output
3. Provision: `./provision.yaml -i <ip>`
4. SSH into the VM: `ssh dev@<ip>`
5. Work on your project
6. Destroy when done: `./hetzner.py destroy <vm-name>`

Old VMs are automatically cleaned up daily at 02:00 UTC via cron.
