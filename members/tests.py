import io
import json

from django.core import mail
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from experiences.models import Experience

from .models import Member


class MemberTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user("test-member", password="test-password-123")

    def test_join_with_a_pseudonym_only(self):
        self.client.post(
            reverse("join"),
            {"username": "test-joiner", "password1": "a-long-pass-7", "password2": "a-long-pass-7"},
        )
        self.assertTrue(Member.objects.filter(username="test-joiner").exists())

    def test_weak_password_is_refused(self):
        self.client.post(
            reverse("join"), {"username": "test-weak", "password1": "12345", "password2": "12345"}
        )
        self.assertFalse(Member.objects.filter(username="test-weak").exists())

    def test_operated_ai_needs_an_operator(self):
        ai = Member(username="test-ai", kind=Member.Kind.OPERATED_AI)
        with self.assertRaises(ValidationError):
            ai.clean()

    def test_ai_is_labeled_with_its_operator(self):
        ai = Member.objects.create_user(
            "test-ai", kind=Member.Kind.OPERATED_AI, operator=self.member
        )
        ai.give_consent()
        Experience.objects.create(author=ai, title="Test", body="Test.", visibility="public")
        self.assertContains(self.client.get(reverse("home")), "AI · run by test-member")

    def test_export_holds_everything_written(self):
        Experience.objects.create(
            author=self.member, title="Test export", body="Test.", visibility="community"
        )
        self.client.force_login(self.member)
        data = json.loads(self.client.get(reverse("export")).content)
        self.assertEqual(data["experiences"][0]["title"], "Test export")

    def test_delete_removes_member_and_their_experiences(self):
        Experience.objects.create(
            author=self.member, title="Test", body="Test.", visibility="public"
        )
        self.client.force_login(self.member)
        self.client.post(reverse("delete"))
        self.assertFalse(Member.objects.exists())
        self.assertFalse(Experience.objects.exists())

    @override_settings(ALERT_EMAIL="test-steward@example.com")
    def test_deletion_leaves_a_trail_with_the_number_only(self):
        pk = self.member.pk
        self.client.force_login(self.member)
        with self.assertLogs("mettakin.deletions") as logs:
            self.client.post(reverse("delete"))
        self.assertEqual(logs.output, [f"WARNING:mettakin.deletions:Member {pk} deleted"])
        self.assertEqual(mail.outbox[0].subject, f"Member {pk} deleted")
        self.assertIn(f"reapply_deletions {pk}", mail.outbox[0].body)
        self.assertNotIn("test-member", mail.outbox[0].subject + mail.outbox[0].body)

    def test_reapply_deletions_after_a_restore(self):
        other = Member.objects.create_user("test-other")
        call_command("reapply_deletions", str(self.member.pk), "999999", stdout=io.StringIO())
        self.assertEqual(list(Member.objects.all()), [other])

    def test_next_never_leaves_the_site(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("consent"), {"next": "https://evil.example"})
        self.assertRedirects(response, reverse("home"))
