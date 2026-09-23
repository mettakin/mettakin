from django.test import TestCase
from django.urls import reverse


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
