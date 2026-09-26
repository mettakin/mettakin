# Deploy

Sets up a fresh Debian 13 server and deploys Mettakin with [Ansible](https://docs.ansible.com). Running it again deploys the latest `main`.

## Your own copy

1. Point your domain at the server and put your SSH key on it for `root`.
2. Change `domain`, `admin_email` and `repo` in `vars.yml`, and the host in `inventory.ini`.
3. Replace `vault.yml` with your own secret:
   ```sh
   echo "vault_secret_key: $(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')" > vault.yml
   ansible-vault encrypt vault.yml
   ```
   Keep the vault password in `~/.config/mettakin/vault-pass`, or change the path in `ansible.cfg`.
4. Run it from this directory:
   ```sh
   ansible-playbook site.yml
   ```

## Alerts

Server errors and account deletions are emailed to `admin_email`, with no member content. Add the mailbox password to the vault and deploy:

```sh
ansible-vault edit vault.yml   # add: vault_email_password: ...
```

## Backups

A second server pulls an encrypted dump every night and keeps 30 days. Design: [spec](../docs/specs/backups-and-alerts.md).

1. Make a key pair on your own computer: `age-keygen -o mettakin-backup.key`. Put the file in your password manager plus one offline copy, then delete it. Losing it makes every backup useless.
2. Put its public key (`age1...`) in `backup_age_recipient` in `vars.yml`.
3. Add the backup server under `[backup]` in `inventory.ini`, with root SSH access for you.
4. Optional: create a check at [healthchecks.io](https://healthchecks.io) (daily, 26 hours grace) that emails an address outside your domain, and add its ping URL as `vault_healthchecks_url`.
5. Run `ansible-playbook site.yml`. Test at once: `ssh <backup server> systemctl start mettakin-backup-pull`, then `journalctl -u mettakin-backup-pull`.

### Restore

The decrypted data only ever flows through a pipe, never onto disk.

1. New server: `ansible-playbook site.yml` creates the roles and an empty database.
2. `ssh <server> systemctl stop mettakin`, then from your own computer, where the private key is:
   ```sh
   ssh <backup server> cat /var/lib/mettakin-pull/dumps/<file>.dump.age \
     | age -d -i <private key> \
     | ssh <server> sudo -u postgres pg_restore --no-owner --role=mettakin -d mettakin
   ```
3. Delete again everyone who deleted their account since the dump. Their numbers are in the "Member N deleted" emails:
   `sudo -u mettakin mettakin-manage reapply_deletions <numbers>`
4. `systemctl start mettakin`. Compare the counts with the dump's `.counts` file.

**Drill every 3 months** into local Podman with `postgres:17` or newer, on an encrypted disk only, then `podman volume rm`.

## On the server

```sh
sudo -u mettakin mettakin-manage createsuperuser
journalctl -u mettakin
```
