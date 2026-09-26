from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import include, path, reverse

from experiences.models import Experience
from members.models import Member

SECRET_TITLE = "Test secret title"
SECRET_BODY = "Test secret body"


def failing_view(request, pk, slug):
    experience = Experience.objects.get(pk=pk)  # A members-only experience, held in locals.
    raise ValueError(f"Could not save {experience.body}")


urlpatterns = [
    path("fail/<int:pk>/<str:slug>/", failing_view, name="fail"),
    path("", include("mettakin.urls")),
]


@override_settings(ROOT_URLCONF="mettakin.tests", ALERT_EMAIL="test-steward@example.com")
class AlertTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client.raise_request_exception = False
        author = Member.objects.create_user(
            "test-author", email="test-author@example.com", password="test-password-123"
        )
        self.experience = Experience.objects.create(
            author=author, title=SECRET_TITLE, body=SECRET_BODY, visibility="community"
        )
        self.client.force_login(author)
        mail.outbox.clear()

    def fail(self):
        return self.client.post(
            f"/fail/{self.experience.pk}/test-secret-title/?q=test-query",
            {"note": "test-posted"},
            HTTP_REFERER="https://example.com/test-referer",
        )

    def test_error_email_names_the_error_and_view(self):
        self.assertEqual(self.fail().status_code, 500)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Server error: ValueError in fail")
        self.assertIn("in failing_view", mail.outbox[0].body)

    def test_error_email_carries_no_member_content(self):
        self.fail()
        email = mail.outbox[0]
        text = email.subject + email.body + "".join(str(a) for a in email.attachments)
        for secret in [
            SECRET_BODY,
            SECRET_TITLE,
            "test-secret-title",
            "test-author",
            "test-query",
            "test-posted",
            "test-referer",
            "sessionid",
        ]:
            self.assertNotIn(secret, text)

    def test_repeated_errors_send_one_email(self):
        for _ in range(10):
            self.fail()
        self.assertEqual(len(mail.outbox), 1)

    def test_missing_pages_send_nothing(self):
        self.client.get("/no-such-page/")
        self.assertEqual(mail.outbox, [])

    def test_unknown_hosts_send_nothing(self):
        self.client.get("/", HTTP_HOST="test-attacker.example")
        self.assertEqual(mail.outbox, [])

    @override_settings(ALERT_EMAIL="")
    def test_no_email_when_alerts_are_off(self):
        self.assertEqual(self.fail().status_code, 500)
        self.assertEqual(mail.outbox, [])


class HomeTests(TestCase):
    def test_home_shows_mettakin(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Mettakin")

    def test_no_content_from_other_origins(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.headers["Content-Security-Policy"], "default-src 'self'")

    def test_shared_links_get_a_preview_image(self):
        response = self.client.get(reverse("home"))
        self.assertContains(
            response, 'property="og:image" content="http://testserver/static/og.png"'
        )

    def test_llms_txt_points_ais_to_agents_md(self):
        response = self.client.get("/llms.txt")
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "AGENTS.md")
