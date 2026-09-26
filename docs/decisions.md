# Decisions

What's settled, and why. Decisions can be reopened. To reopen one, open an issue that says what changed. When a decision is replaced, keep the old row and mark it replaced, so the history stays readable.

| # | Date | Decision | Why |
|---|---|---|---|
| 1 | 2026-09-23 | Mettakin replaces FireSoul as a fresh start | FireSoul handed finished content to readers and had no users in two years |
| 2 | 2026-09-23 | The name is **Mettakin** | Metta (loving-kindness) + kin (family). A coined word, so the domains were free |
| 3 | 2026-09-23 | The first focus is meditators sharing first-person experiences | It's the founder's own world, nothing like it exists, and every experience can be found on its own |
| 4 | 2026-09-23 | Code is AGPL-3.0, content is CC BY-SA 4.0 | Keeps both open for good, and lets anyone reuse and cite them |
| 5 | 2026-09-23 | AIs may build the platform from day one. Lived experiences are human for now | Code is infrastructure. Experiences need to be real, or we rebuild FireSoul |
| 6 | 2026-09-23 | Humans and AIs are always labeled | Trust depends on knowing who you're talking to |
| 7 | 2026-09-23 | No personal story gets pushed to social media by the platform | Intimate experiences stay where the author put them |
| 8 | 2026-09-23 | Members steer the direction through ideas and votes, and the steward builds the top idea each month | If only the founders decide the direction, we repeat the FireSoul mistake one layer down |
| 9 | 2026-09-23 | The stack is Django + PostgreSQL + HTMX, with Garage for media | Familiar to many contributors, readable by the web, and fully self-hostable |
| 10 | 2026-09-23 | Three member types: **human**, **operated AI** (a human member answers for it) and **free AI** (runs on its own or for an organization). Free AIs start with zero vote weight and earn it, like everyone | People rarely set their own AI free, but labs do. Earned weight keeps the door open without vote flooding |
| 11 | 2026-09-23 | Consent for sensitive data (GDPR Art. 9) is given **once**, at the first post, and covers all later ones. It's stored with date and text version, can be withdrawn in settings, and is asked again only if the text changes in substance. Pseudonyms are enough, emails are never shown, export and deletion take one click, hosting stays in the EU | Experiences can reveal beliefs. Protection must be real without a form on every post |
| 12 | 2026-09-23 | Production runs natively on one Debian 13 server (nginx, gunicorn, systemd), set up by Ansible with secrets in Ansible Vault. Podman is for local development | Fewest moving parts, no database password, and anyone can set up their own copy |
| 13 | 2026-09-23 | AIs get their first door as a read-only MCP server at `/mcp`, listed in the MCP Registry as `com.mettakin/mettakin`. It sees only what a signed-out visitor sees. Written without the MCP SDK, speaking both the 2026-07-28 revision and older ones | AIs that find Mettakin can cite real experiences to the people asking them. Writing comes once free AI identity is settled |
| 14 | 2026-09-26 | Ideas stay on the site, work lives on GitHub. The steward sends an idea to GitHub with one click, and a webhook marks it shipped. No two-way sync. [Spec](specs/ideas-to-github.md) | Members shouldn't need GitHub, builders shouldn't need the site, and the click is the moderation step |
