# Spec: backups and alerts

Status: planned. Decision [15](../decisions.md).

## Why

Everything lives on one server with no copy anywhere else. If the disk dies or the server is broken into, members' experiences are gone, and a home built on trust doesn't survive that. And when the site breaks, nobody hears about it.

Targets: lose at most one day (RPO 24 hours), be back within about an hour (RTO 1 hour). Enough at this size.

## Backups

### The shape

A separate backup server **pulls** from the main server. The main server can't reach the backups, so someone who breaks into it can't delete them. The dump is **encrypted before it leaves**, so the backup server only ever holds files it can't read.

- **Where:** any Linux server we reach by SSH, in the EU, in a different data center than the main server. Today that's the steward's own Hetzner server in another location. Not the old FireSoul server: it's being retired.
- **What:** the PostgreSQL database, which holds everything members wrote. Session data is left out: it's secret and useless after a restore. Media joins when Garage holds files. Code lives on GitHub. Database roles need no backup, Ansible creates them.
- **Encryption:** [age](https://age-encryption.org), to a public key in `deploy/vars.yml`. The private key lives only offline.

### The main server

Ansible creates:

1. A system user `mettakin-backup` with `/bin/sh` as its shell and a locked password. It can't be `mettakin` (its shell is `nologin`, which stops forced commands) or root (Postgres maps root to no role).
2. A database role `mettakin-backup` with `pg_read_all_data`: read only, matched by name over the local socket.
3. A script `/usr/local/bin/mettakin-backup-dump`, run with `set -euo pipefail`. It:
   - fails when `/` is more than 85% full, so a filling disk is caught by the backup alert,
   - runs `pg_dump --format=custom --no-owner --no-acl --exclude-table-data=django_session mettakin | age -r <public key>` to stdout,
   - writes the row counts of members, experiences and ideas to stderr, so a restore can be checked against the same moment,
   - ignores any command the caller sends.
4. One line in that user's `authorized_keys`:
   `restrict,from="<backup IP>",command="/usr/local/bin/mettakin-backup-dump" ssh-ed25519 ...`
   `restrict` turns off shells, terminals and forwarding. `from` accepts only the backup server.

### The backup server

Ansible sets up a `backup` group in the inventory. It's optional, so a self-hosted copy can skip it or point it at its own server. It creates a user `mettakin-pull` with a `0700` directory and a systemd timer (logs go to the journal). The main server's host key is pinned in `known_hosts`.

Nightly, as `mettakin-pull`:

1. Pull into `mettakin-YYYY-MM-DD.dump.age.partial`. A non-zero exit from SSH (and so from `pg_dump`, thanks to `pipefail`) is a failure.
2. Check the file starts with the age header and is at least half the size of the last good one. A sudden shrink means something went wrong.
3. fsync, rename to `.dump.age`, and log the counts and the file's sha256.
4. Only then delete dumps older than **30 days**, always keeping the newest 7, so a month of silent failures can't prune away the last good copies.
5. Ping the dead man's switch ([healthchecks.io](https://healthchecks.io), open source). On any failure, ping its `/fail` URL. If no ping arrives for 26 hours, the steward gets an email.

### Deletion and backups

A member who deletes their account stays in encrypted backups for up to 30 days, then is gone. The delete-account page says so. That's why there are no monthly copies kept for a year.

A restore brings back accounts deleted after the dump. So every deletion leaves a trail outside the database: one line in the journal and an email to the steward, both with the member's number only, no name or content. After any restore, `mettakin-manage reapply_deletions <numbers>` deletes them again. The email survives even when the server is gone. The steward deletes these emails after 30 days, once no backup still holds that member.

### Restore

`deploy/README.md` gets the steps:

1. Fresh server > `ansible-playbook site.yml` (creates the roles and the empty database).
2. Stop `mettakin`. Fetch the latest dump and pipe it straight through: `age -d -i <key> dump.age | pg_restore --no-owner --role=mettakin -d mettakin`. The decrypted data never lands on disk.
3. `reapply_deletions` with the numbers from the deletion emails since the dump's date.
4. Start `mettakin`. Compare the counts with the ones logged for that dump.

**Drill every 3 months:** the same steps into local Podman with `postgres:17` or newer (`pg_restore` can't read a dump from a newer version), decrypted through the same pipe, only on an encrypted disk, never on a shared machine. Afterwards, `podman volume rm`. A backup never restored is only a hope.

### Recovery secrets

Losing these makes every backup useless, so each has two copies:

- **age private key:** the steward's password manager, plus one offline copy (paper or USB). Never on a server.
- **Ansible Vault password:** `~/.config/mettakin/vault-pass` and the password manager.

## Alerts

### Errors

Django's built-in error email carries far too much: POST and GET data, cookies, headers, the full URL (whose slug can be a members-only title), local variables, and exception messages that can echo stored values. Filtering it is fragile, so we don't use it.

Instead, a small logging handler of our own on `django.request`, level `ERROR`, builds the email from a whitelist:

- **Subject:** `Server error: <exception type> in <view name>`. The view name, never the path.
- **Body:** the traceback lines: file, line number, function and the line of code. The code is public anyway. No exception message, no variables, nothing from the request.
- **Rate limit:** one email per exception type and view every 10 minutes, so an outage doesn't send thousands of emails from inside requests.
- **Never:** 404 emails, and nothing from `django.security` (like `DisallowedHost`). nginx already answers unknown hosts before Django sees them.

Sent through the seohost mailbox: port 465 with SSL, `EMAIL_TIMEOUT = 10`, from `hello@mettakin.com` so SPF and DKIM line up. Without the email settings, alerts are off and the site works as before.

### Downtime

An outside uptime service checks `https://mettakin.com/` every 5 minutes for the word "mettakin" on the page, not just a `200`. Free tier of any service (UptimeRobot today). It only sees the public home page.

**Where alerts go:** healthchecks.io and the uptime service email an address outside `mettakin.com`. If the domain or mail breaks, the alert still arrives.

## Security

What each place can do if it's broken into:

| Broken into | What they get | What they can't do |
|---|---|---|
| Main server | The live database, as before | Reach, read or delete backups. The main server has no key to the backup server |
| Backup server | Encrypted dumps, and a key that can only start a new encrypted dump | Read any of it without the offline private key, or get a shell on the main server |
| Laptop during a drill | The restored database | Nothing lasting: plaintext only in an encrypted Podman volume, removed afterwards |
| seohost mailbox | Exception types, code lines, member numbers | Read any member's words or names |
| Repository | Could swap the age public key in a pull request | Decrypt old dumps. The steward reviews every change to `deploy/`, and a new key there is a red flag |

The backup server may also serve the steward's own use. Then: SSH by key only, firewall closed except SSH, automatic security updates, and backups owned by `mettakin-pull` alone. The healthchecks ping URL is a secret: whoever has it can fake a good backup. It lives in the vault and in a `0600` file.

## Settings

| Setting | What | Where |
|---|---|---|
| `backup_age_recipient` | age public key | `deploy/vars.yml`, public on purpose |
| `backup_ssh_key`, `backup_from` | The backup server's public key and IP | `deploy/vars.yml` |
| `vault_healthchecks_url` | Ping URL of the dead man's switch | Ansible Vault |
| `vault_email_password` | seohost mailbox | Ansible Vault |

Each part turns on only when its settings exist.

## Not now

- A second copy at another provider. Comes when losing Hetzner as a whole is a real risk.
- Point-in-time recovery (WAL archiving). A day of loss is acceptable at this size.
- A metrics dashboard.

## Tests

- **Error email:** raise in a view that holds a members-only experience, with POST data, a query string, cookies and a Referer. The title, body, member's email, query string and Referer appear nowhere in `mail.outbox`, subject or body.
- An exception whose message contains a stored value: the value isn't in the email.
- Ten identical errors send one email. A 404 sends none. Without email settings, nothing is sent and nothing crashes.
- **Deletion:** deleting an account logs and emails only the number. `reapply_deletions` deletes the given members and ignores unknown numbers.
- The dump script and the pull are checked by the drill and the "Done when" steps, not unit tests.

## Done when

1. A nightly `.dump.age` appears on the backup server, and old ones rotate out while the newest 7 stay.
2. From the main server, as root, nothing on the backup server can be reached. The backup key can't get a shell on the main server.
3. Stopping the timer for a day sends a healthchecks.io email. A failing dump pings `/fail`.
4. A test error arrives by email with the exception type and traceback only.
5. Stopping nginx for 10 minutes sends a downtime email.
6. The first restore drill is done, and the counts match the logged ones.
