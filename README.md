# autodev

Personal environment for agent-assisted development using throwaway virtual machine.

## Tools

`hetzner.py` CLI tool and a library to create and destroy VM on Hetzner. It uses Hetzner API, it creates a VM according to the specs below. It uses ConfigArgParse library for configuration.

Commands:

* create
* destroy
* cleanup

 Cleanup command destroys all the VMs ruining longer than 24 hours (configurable).

# autodev

Personal environment for agent-assisted development using a throwaway virtual machine.

## Tools

### Hetzner

`hetzner.py` is a CLI tool and a Python library to create and destroy VMs on Hetzner Cloud. It uses the Hetzner Cloud API to operate VMs, ConfigArgParse, python-dotenv and python-decouple libraries for configuration. All the default settings are in `settings.py`.

Configuration is loaded from a project-local `.env` file that contains environment variables required by the tool. This lets me keep credentials and per-project settings outside of the code, but still colocated with the project.

When creating a new VM, `hetzner.py` initializes it via `cloud-init` by passing a user data script to the Hetzner Cloud API so the machine comes up preconfigured for agent-assisted development.

By default, the VM is created in Hetzner’s Finland data center, instance type CX23 with IPv4 networking (configurable).

Commands:

* `create` – create a VM with the above specs and run the configured cloud-init.
* `destroy` – destroy a given VM.
* `cleanup` – destroy all VMs that have been running for longer than 24 hours (configurable).

Cleanup cron task runs daily at 02:00 UTC, stdout and stderr go to syslog via `... |& logger -t autodev`.

### Telegram

`telegram.py` notifies me about the events requring my attention. It uses `python-telegram-bot` library and the configuration method described above. When running whithout dash-optins, it sends me (chat ID is configurable) a Telegram message consisting of all its arguments.

### Provisioning

`provision.yaml` is an Ansible single-file playbook, that logs in to the server as root, creates `autodev` user (username is configurable via Ansible variables), sets `bash` as user shell, installs cleanup cron task (cron shell should be Bash).

```bash
./provision.yaml -i host.name,
```

## Programming style

Don't be defensive, fail fast. It's much better to just show me an exception, than trying to handle all the possible errors. Keep the code concise, with minimal comments.

## Environment configuration

The tool reads configuration from a `.env` file in the project directory and exports those values into the environment before running.

Example:

```bash
HETZNER_TOKEN=your-api-token-here
AUTODEV_PROJECT_NAME=your-project-name
AUTODEV_SSH_PUBLIC_KEY=~/.ssh/id_ed25519.pub
```
