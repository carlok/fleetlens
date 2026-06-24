# Troubleshooting

## SSH Permission Denied

Confirm the mounted key is readable by the container user and the public key is installed on the VM.

## Host Key Errors

FleetLens does not disable host key checking. Update `known_hosts` on the host and mount the `.ssh` directory read-only.

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
