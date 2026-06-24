# Troubleshooting

## SSH Permission Denied

Confirm the mounted key is readable by the container user and the public key is installed on the VM.

## Host Key Errors

FleetLens does not disable host key checking. Update `known_hosts` on the host and mount the `.ssh` directory read-only.

If the container reports `Host key verification failed`, verify that the host and port used in the inventory match an entry in the mounted `known_hosts` file. For non-standard SSH ports, OpenSSH stores entries in bracket form:

```text
[example.com]:2222 ssh-ed25519 ...
```

You can add the key on the host before running FleetLens:

```bash
ssh-keyscan -p <port> <host> >> "$HOME/.ssh/known_hosts"
```

Do not disable host key checking just to make the first run pass.

## Bind-Mounted Workspace Permissions

FleetLens uses `/tmp/fleetlens-ansible` for Ansible controller temp files so the container does not need to write temp state into `/workspace/.ansible`.

The container runs as root inside rootless Podman so bind-mounted repo output and read-only SSH keys work with normal host file permissions. Rootless Podman maps that container root back to the invoking user outside the VM.

## Sudo Fails

The default example inventory is no-sudo. If you enabled `ansible_become=true`, disable it again for a first read-only test.

Run the ping playbook first, then test a single host interactively with Ansible. If sudo prompts for a password, cron runs will fail unless configured deliberately.

## Reports Are Missing

Check `reports/raw-ansible.json`, then run:

```bash
python -m fleetlens.cli render
```

## Source Edits Do Not Appear

Make sure the repository is mounted as `.:/workspace:Z`. Rebuild the image only for dependency changes.
