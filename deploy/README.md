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

## On the server

```sh
sudo -u mettakin mettakin-manage createsuperuser
journalctl -u mettakin
```
