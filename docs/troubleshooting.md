# Troubleshooting

## SSH Permission Denied

Confirm the same tuple works by hand from the scheduler host:

```bash
ssh -i "$HOME/.ssh/<key>" -p <port> <user>@<host>
```

Then mirror those values in the inventory:

```ini
ansible_host=<host>
ansible_user=<user>
ansible_port=<port>
ansible_ssh_private_key_file=~/.ssh/<key>
```

If FleetLens is run by cron or systemd, test as that same user. SSH agents and macOS Keychain prompts are usually unavailable in non-interactive schedules, so use a key that can be used unattended by that scheduler user.

## Host Key Errors

FleetLens does not disable host key checking. Add the host key before scheduling:

```bash
ssh-keyscan -p <port> <host> >> "$HOME/.ssh/known_hosts"
```

For non-standard SSH ports, OpenSSH stores entries in bracket form:

```text
[example.com]:2222 ssh-ed25519 ...
```

## Python Interpreter Warning

If Ansible warns that it discovered `/usr/bin/python3.12` or another remote Python path, pin the interpreter in inventory:

```ini
ansible_python_interpreter=/usr/bin/python3
```

## Sudo Fails

The default example inventory is no-sudo. If you enabled `ansible_become=true`, disable it again for a first read-only test.

Run the ping playbook first, then test a single host interactively with Ansible. If sudo prompts for a password, cron or systemd runs will fail unless configured deliberately.

## A Host Shows "no result collected"

The host was in the inventory but its collection stopped before producing a result, usually because fact gathering or a task failed outright (for example, a wrong `ansible_python_interpreter`). The Ansible output above the FleetLens summary shows the failing task. FleetLens still renders the other hosts; `ansible-playbook` exits with rc 2 or 4 in this case and FleetLens treats that as report data rather than a failed run.

## A Check Shows "check failed (rc=N)"

A collector command such as `apt list --upgradable`, `systemctl --failed`, or `journalctl` returned a non-zero exit code on a reachable host. FleetLens reports this as a WARNING because the check's "nothing found" result cannot be trusted. Run the command by hand as the collection user to see the error.

## Reports Are Missing

Check `reports/raw-ansible.json`, then run:

```bash
python -m fleetlens.cli render
```

## Email Is Delayed

FleetLens prints a `message_id=...` after SMTP submission. Use that ID, the recipient, and the timestamp to search your SMTP provider logs. SMTP acceptance means the provider accepted the message; it does not guarantee immediate inbox delivery.
