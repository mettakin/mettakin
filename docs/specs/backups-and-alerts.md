# Spec: backups and alerts

Status: planned. Decision [15](../decisions.md).

## Why

Everything lives on one server with no copy anywhere else. If the disk dies or the server is broken into, members' experiences are gone, and a home built on trust doesn't survive that. And when the site breaks, nobody hears about it.

## Backups

### The shape

A separate backup server **pulls** from the main server. The main server can't reach the backups, so someone who breaks into it can't delete them.

- **Where:** any Linux server we reach by SSH, in the EU, in a different data center than the main server. Today that's the steward's own Hetzner server in another location. Not the old FireSoul server: it's being retired, and a backup shouldn't depend on it.
- **What:** the PostgreSQL database. That's everything members wrote. Media joins when Garage holds files. Code lives on GitHub, secrets in Ansible Vault and the steward's password manager.
- **Encrypted before it leaves.** The dump is encrypted on the main server with an [age](https://age-encryption.org) public key. The private key lives only offline, in the steward's password manager. The backup server holds files it can't read.

### How it runs

1. Nightly, the backup server connects with an SSH key that can do one thing. `authorized_keys` pins it to a forced command: `pg_dump --format=custom mettakin | age -r <public key>`. No shell, no forwarding.
2. It saves the output as `mettakin-YYYY-MM-DD.dump.age`, after checking it isn't empty.
3. It deletes files older than **30 days**.
4. On success it pings a dead man's switch ([healthchecks.io](https://healthchecks.io), open source, free tier). If no ping arrives for 26 hours, the steward gets an email. A backup that silently stopped is the usual way backups fail.

Ansible sets up both sides: a `backup` group in the inventory, optional, so a self-hosted copy can skip it or point it at its own server. A systemd timer, not cron, so the logs land in the journal.

### Deletion and backups

A member who deletes their account stays in backups for up to 30 days, then is gone for good. The delete-account page says so. That's why there are no monthly copies kept for a year.

### Restore

- `deploy/README.md` gets a restore section: fetch a file, decrypt it with the private key, `pg_restore` into a fresh database.
- **Drill:** the steward restores the latest backup into local Podman every 3 months and checks the counts of members, experiences and ideas against the live site. A backup never restored is only a hope.

## Alerts

### Errors

- Django emails server errors to `hello@mettakin.com` through the existing seohost mailbox (`ADMINS`, `SERVER_EMAIL`, SMTP settings, password in Ansible Vault).
- **Error emails carry no member content.** A custom exception reporter filter drops POST data and local variables, keeping only the traceback, method and path. Members-only content never reaches email ([architecture](../architecture.md#principles), principle 5).
- Repeated errors are one email each. Rate limiting them waits until it's a real problem.

### Downtime

An outside check requests `https://mettakin.com/` every 5 minutes and emails the steward when it fails. healthchecks.io doesn't do this, so it's a free uptime monitor. It only sees the public home page.

## Secrets

| Setting | What | Where |
|---|---|---|
| age public key | Encrypts the dumps | `deploy/vars.yml`, public on purpose |
| age private key | Decrypts for restore | Steward's password manager only. Never on a server |
| Backup SSH key | Pull only, forced command | Private half on the backup server |
| Healthchecks ping URL | Dead man's switch | Ansible Vault |
| `EMAIL_HOST_PASSWORD` | seohost mailbox | Ansible Vault |

## Not now

- A second backup copy in another provider. Comes when losing Hetzner as a whole is a real risk.
- Point-in-time recovery (WAL archiving). A day of loss is acceptable at this size.
- A metrics dashboard. One server, email alerts, until traffic says otherwise.

## Tests

- The exception reporter filter: POST data and local variables never appear in the error email. With Django's test runner and `mail.outbox`.
- The backup path is checked by the drill, not a unit test.

## Done when

1. A nightly `.dump.age` file appears on the backup server, and the old ones rotate out.
2. The main server can't list or delete anything on the backup server.
3. Stopping the timer for a day sends a healthchecks.io email.
4. A test error on the site arrives by email without the form data.
5. Stopping nginx for 10 minutes sends a downtime email.
6. The first restore drill is done, and the counts match.
