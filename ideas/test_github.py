import hashlib
import hmac
import io
import json
from unittest import mock
from urllib.error import HTTPError

from django.test import TestCase, override_settings
from django.urls import reverse

from experiences.tests import member

from .models import Idea, Vote

SECRET = "test-webhook-secret"
ISSUE = "https://github.com/test/repo/issues/7"
GITHUB = {"GITHUB_REPO": "test/repo", "GITHUB_TOKEN": "test-token"}


def github_answers(url=ISSUE):
    return mock.patch(
        "ideas.github.urlopen", return_value=io.BytesIO(json.dumps({"html_url": url}).encode())
    )


@override_settings(**GITHUB)
class SendToBuildersTests(TestCase):
    def setUp(self):
        self.client.force_login(member("test-steward", is_staff=True, is_superuser=True))
        self.idea = Idea.objects.create(
            author=member(), title="Test idea #1", body="Test body for @someone about #123."
        )
        Vote.objects.create(member=self.idea.author, idea=self.idea)

    def send(self):
        return self.client.post(
            reverse("admin:ideas_idea_changelist"),
            {"action": "send_to_builders", "_selected_action": [self.idea.pk]},
            follow=True,
        )

    def test_sending_opens_an_issue_and_plans_the_idea(self):
        with github_answers() as urlopen:
            self.send()
        request = urlopen.call_args.args[0]
        sent = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.github.com/repos/test/repo/issues")
        self.assertEqual(sent["labels"], ["from-members"])
        self.assertIn("test-member (Human), 1 votes when sent", sent["body"])
        self.assertIn(f"http://testserver{self.idea.get_absolute_url()}", sent["body"])
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.issue_url, ISSUE)
        self.assertEqual(self.idea.status, Idea.Status.PLANNED)

    def test_members_words_cant_ping_or_link_on_github(self):
        with github_answers() as urlopen:
            self.send()
        sent = json.loads(urlopen.call_args.args[0].data)
        for text in [sent["title"], sent["body"]]:
            self.assertNotRegex(text, r"[@#]\w")
        self.assertIn("@​someone", sent["body"])

    def test_an_idea_already_sent_is_skipped(self):
        Idea.objects.filter(pk=self.idea.pk).update(issue_url=ISSUE)
        with github_answers() as urlopen:
            self.send()
        urlopen.assert_not_called()

    def test_a_github_error_leaves_the_idea_unchanged(self):
        refused = HTTPError(ISSUE, 401, "Unauthorized", {}, None)
        with mock.patch("ideas.github.urlopen", side_effect=refused):
            page = self.send()
        self.assertContains(page, "GitHub said: HTTP Error 401: Unauthorized")
        self.idea.refresh_from_db()
        self.assertEqual((self.idea.issue_url, self.idea.status), ("", Idea.Status.OPEN))

    @override_settings(GITHUB_TOKEN="")
    def test_refuses_without_settings(self):
        with github_answers() as urlopen:
            page = self.send()
        urlopen.assert_not_called()
        self.assertContains(page, "GitHub isn&#x27;t set up.")


@override_settings(GITHUB_WEBHOOK_SECRET=SECRET)
class WebhookTests(TestCase):
    def setUp(self):
        self.idea = Idea.objects.create(
            author=member(),
            title="Test idea",
            body="Test.",
            status=Idea.Status.PLANNED,
            issue_url=ISSUE,
        )

    def deliver(
        self, action="closed", reason="completed", url=ISSUE, event="issues", secret=SECRET
    ):
        body = json.dumps(
            {"action": action, "issue": {"html_url": url, "state_reason": reason}}
        ).encode()
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        response = self.client.post(
            reverse("github_webhook"),
            body,
            content_type="application/json",
            headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": event},
        )
        self.idea.refresh_from_db()
        return response

    def test_a_bad_signature_changes_nothing(self):
        self.assertEqual(self.deliver(secret="test-wrong-secret").status_code, 403)
        self.assertEqual(self.idea.status, Idea.Status.PLANNED)

    def test_no_signature_is_refused(self):
        response = self.client.post(
            reverse("github_webhook"), "{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    @override_settings(GITHUB_WEBHOOK_SECRET="")
    def test_refused_when_no_secret_is_set(self):
        self.assertEqual(self.deliver(secret="").status_code, 403)

    def test_closed_as_completed_ships_the_idea(self):
        self.assertEqual(self.deliver().status_code, 204)
        self.assertEqual(self.idea.status, Idea.Status.SHIPPED)
        self.assertEqual(self.idea.note, f"Shipped in {ISSUE}")

    def test_the_stewards_note_survives_shipping(self):
        Idea.objects.filter(pk=self.idea.pk).update(note="Test steward note.")
        self.deliver()
        self.assertEqual(self.idea.note, "Test steward note.")

    def test_reopened_plans_it_again(self):
        self.deliver()
        self.deliver(action="reopened", reason=None)
        self.assertEqual(self.idea.status, Idea.Status.PLANNED)

    def test_closed_as_not_planned_changes_nothing(self):
        self.deliver(reason="not_planned")
        self.assertEqual((self.idea.status, self.idea.note), (Idea.Status.PLANNED, ""))

    def test_unknown_issues_and_pings_are_ignored(self):
        self.assertEqual(
            self.deliver(url="https://github.com/test/repo/issues/99").status_code, 204
        )
        self.assertEqual(self.deliver(event="ping").status_code, 204)
        self.assertEqual(self.idea.status, Idea.Status.PLANNED)

    def test_an_issue_without_a_url_matches_no_unsent_idea(self):
        unsent = Idea.objects.create(author=self.idea.author, title="Test unsent", body="Test.")
        self.deliver(url="")
        unsent.refresh_from_db()
        self.assertEqual(unsent.status, Idea.Status.OPEN)
