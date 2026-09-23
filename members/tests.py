import json

from django.core.exceptions import ValidationError
from django.test import TestCase
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

    def test_next_never_leaves_the_site(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("consent"), {"next": "https://evil.example"})
        self.assertRedirects(response, reverse("home"))
