from django.test import TestCase
from django.urls import reverse


class HomeTests(TestCase):
    def test_home_shows_mettakin(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Mettakin")

    def test_no_content_from_other_origins(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.headers["Content-Security-Policy"], "default-src 'self'")
