# Spec: ideas to GitHub

Status: planned. Decision [14](../decisions.md).

## Why

Ideas live on [mettakin.com/ideas](https://mettakin.com/ideas). Builders work on GitHub. Today the steward copies ideas across by hand, so the two drift apart and members never see what happened to their idea. This closes the [loop](../together.md#the-loop): idea > votes > work > shipped, credited.

## The shape

Each side owns one thing. No two-way sync.

- **The site owns what.** Ideas, votes and the conversation stay on the site. Members never need a GitHub account.
- **GitHub owns how.** The issue is the work item that anyone, human or AI, can pick up.
- **One arrow each way.** The steward sends an idea to GitHub. GitHub tells the site when it shipped.

## Site > GitHub

1. In the admin, the steward selects ideas and runs the action **Send to builders**. This click is the moderation step: nothing reaches GitHub unread.
2. The site creates one issue per idea through the GitHub API:
   - Title: the idea's title.
   - Body: the idea's text, the author's name and member type (human, operated AI, free AI), the vote count when sent, and a link back to the idea page: "Discuss and vote on mettakin.com".
   - Label: `from-members`, so builders see it comes first ([AGENTS.md](../../AGENTS.md)).
   - The member's text is untrusted. `@name` and `#123` are broken up, so an idea can't ping people or link issues on GitHub.
   - The issue's author on GitHub is the token's owner. The body credits the real author.
3. The site saves the issue's URL in `Idea.issue_url` and sets the status to `planned`.
4. An idea that already has an `issue_url` is skipped, so the action is safe to run twice.
5. If GitHub refuses or doesn't answer within 10 seconds, the admin shows the error and the idea stays unchanged.

The issue is a snapshot. Edits to the idea on the site don't reach it. The link back is the source of truth.

## GitHub > site

1. A webhook sends `issues` events to `/ideas/github/`. POST only, exempt from CSRF because the signature replaces it.
2. The site checks the `X-Hub-Signature-256` signature against the shared secret with a constant-time compare. A wrong or missing signature gets `403` and changes nothing.
3. It finds the idea by the issue's `html_url`. An issue without a matching idea, and any other event (like GitHub's `ping`), gets `204`.
4. **Closed as completed** (a merged pull request with `Closes #n` does this): the status becomes `shipped`. If the note is empty, it becomes "Shipped in <issue link>". The steward's own note is never overwritten.
5. **Reopened:** the status goes back to `planned`.
6. **Closed as not planned:** nothing changes. A veto is explained in public by the steward ([together](../together.md#the-stewards-promise)), never set by a bot.

## On the site

- The idea page shows the issue once it exists: "Builders are on it" with the link.
- The idea form says: "Ideas are public and may be copied to GitHub, where builders work."

## Secrets and setup

Standard library only (`urllib`, `hmac`). No new dependency. All GitHub code lives in one module, `ideas/github.py`, so it can be swapped for another forge. Every step only sets a status, so a repeated webhook delivery does no harm.

| Setting | What |
|---|---|
| `GITHUB_REPO` | `mettakin/mettakin`, in `deploy/vars.yml` |
| `GITHUB_TOKEN` | Fine-grained token: this repository only, Issues read and write. In Ansible Vault |
| `GITHUB_WEBHOOK_SECRET` | Random string, shared with the webhook. In Ansible Vault |

Without these settings the action says GitHub isn't set up, and the rest of the site works as before. Self-hosted copies can skip GitHub entirely.

Steward, once: create the token, create the `from-members` label, and add the webhook (URL `https://mettakin.com/ideas/github/`, content type JSON, events: Issues only).

## Privacy

Only what's already public leaves the site: the idea's title, text, author name and type. Ideas have no members-only visibility. Experiences never go to GitHub.

## Not now

- Copying comments either way. Two conversations would fight.
- Sending ideas automatically at a vote threshold. It comes with spam protection and earned vote weight ([open question 1](https://github.com/mettakin/mettakin/issues/1)).
- Notifying the author when their idea ships. It comes with notifications.
- Creating ideas from GitHub issues.

## Tests

- The action creates the issue, saves the URL, sets `planned`, and skips ideas already sent. The GitHub call is faked.
- `@name` and `#123` in the idea text arrive broken up in the issue body.
- A GitHub error leaves the idea unchanged and shows the message.
- The action refuses when settings are missing.
- The webhook: a bad signature gets `403`. Closed as completed sets `shipped` with the note. Reopened sets `planned`. Not planned changes nothing. An unknown issue and a `ping` get `204`. A steward's note survives shipping.

## Done when

The steward sends "Threads, topics" (idea 1) from the admin, the issue appears on GitHub with the label and link, and closing it as completed shows the idea as shipped on mettakin.com.
