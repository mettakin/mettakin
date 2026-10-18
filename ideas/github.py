"""Everything that talks to GitHub, in one place, so another forge can replace it.

The site owns ideas and votes, GitHub owns the work. One arrow each way: the steward
sends an idea as an issue, and GitHub's webhook says when it shipped.
"""

import hashlib
import hmac
import json
import re
from urllib.request import Request, urlopen

from django.conf import settings

from .models import Idea

TIMEOUT = 10
LABEL = "from-members"


class GitHubError(Exception):
    pass


def is_set_up():
    return bool(settings.GITHUB_REPO and settings.GITHUB_TOKEN)


def defuse(text):
    """Break up @name and #123, so a member's words can't ping people or link issues."""
    return re.sub(r"([@#])(?=\w)", "\\1\u200b", text)


def issue_body(idea, link):
    author = idea.author
    kind = author.get_kind_display()
    if author.operator:
        kind += f", run by {author.operator.username}"
    credit = f"Suggested by {author.username} ({kind}), {idea.vote_count} votes when sent."
    # The link is ours, so it stays whole.
    return (
        defuse(f"{idea.body}\n\n---\n\n{credit}")
        + f"\n\n[Discuss and vote on mettakin.com]({link})"
    )


def create_issue(title, body):
    """Open an issue and return its URL."""
    request = Request(
        f"https://api.github.com/repos/{settings.GITHUB_REPO}/issues",
        data=json.dumps({"title": title, "body": body, "labels": [LABEL]}).encode(),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    # HTTPError and timeouts are OSErrors. Their text names the status, never the token.
    try:
        with urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310 = fixed https URL
            return json.load(response)["html_url"]
    except (OSError, ValueError) as error:
        raise GitHubError(str(error)) from error


def send(idea, link):
    """Send one idea, annotated with vote_count, to the builders."""
    idea.issue_url = create_issue(defuse(idea.title), issue_body(idea, link))
    idea.status = Idea.Status.PLANNED
    idea.save(update_fields=["issue_url", "status"])


def is_signed(payload, signature):
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.encode(), signature.encode())


def apply_event(event, payload):
    """Follow an issue's fate. Only ever sets a status, so a repeated delivery does no harm."""
    if event != "issues":
        return
    url = payload.get("issue", {}).get("html_url")
    idea = Idea.objects.filter(issue_url=url).first() if url else None
    if idea is None:
        return
    action, reason = payload.get("action"), payload["issue"].get("state_reason")
    if action == "closed" and reason == "completed":
        idea.status = Idea.Status.SHIPPED
        idea.note = idea.note or f"Shipped in {url}"
    elif action == "reopened":
        idea.status = Idea.Status.PLANNED
    else:
        # Closed as not planned stays as it is: a veto is the steward's to explain.
        return
    idea.save(update_fields=["status", "note"])
