from django.test import TestCase
from django.urls import reverse

from members.models import Member

from .models import Experience, Phenomenon, Resonance


def member(name="test-member", consent=True, **fields):
    created = Member.objects.create_user(name, password="test-password-123", **fields)
    if consent:
        created.give_consent()
    return created


def experience(author, visibility=Experience.Visibility.PUBLIC, **fields):
    fields.setdefault("title", "Test experience 1")
    fields.setdefault("body", "Test body.")
    return Experience.objects.create(author=author, visibility=visibility, **fields)


class VisibilityTests(TestCase):
    def setUp(self):
        self.author = member()
        self.public = experience(self.author, title="Test public")
        self.community = experience(
            self.author, Experience.Visibility.COMMUNITY, title="Test community"
        )

    def test_visitors_see_only_public_experiences(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Test public")
        self.assertNotContains(response, "Test community")
        detail = self.client.get(self.community.get_absolute_url())
        self.assertEqual(detail.status_code, 404)

    def test_members_see_community_experiences(self):
        self.client.force_login(member("reader"))
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Test community")

    def test_withdrawn_consent_hides_everything_the_author_wrote(self):
        self.author.withdraw_consent()
        self.client.force_login(member("reader"))
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Test public")
        self.assertNotContains(response, "Test community")

    def test_wrong_slug_redirects_to_the_right_address(self):
        url = reverse("experience", args=[self.public.pk, "old-title"])
        response = self.client.get(url)
        self.assertRedirects(response, self.public.get_absolute_url(), status_code=301)


class WriteTests(TestCase):
    def post(self, **fields):
        data = {"title": "Test title", "body": "Test body.", "visibility": "public"} | fields
        return self.client.post(reverse("write"), data)

    def test_visitors_are_asked_to_sign_in(self):
        response = self.client.get(reverse("write"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('write')}")

    def test_first_post_asks_for_consent_once(self):
        self.client.force_login(member(consent=False))
        response = self.client.get(reverse("write"))
        self.assertRedirects(response, f"{reverse('consent')}?next=%2Fwrite%2F")
        self.client.post(reverse("consent"), {"next": reverse("write")})
        self.assertEqual(self.client.get(reverse("write")).status_code, 200)

    def test_visibility_must_be_chosen(self):
        self.client.force_login(member())
        response = self.post(visibility="")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Experience.objects.exists())

    def test_tags_are_created_and_reused(self):
        self.client.force_login(member())
        self.post(practice_name="Vipassana", phenomena_names="Light, fear")
        self.post(phenomena_names="light")
        self.assertEqual(Phenomenon.objects.count(), 2)
        self.assertEqual(Phenomenon.objects.get(slug="light").experiences.count(), 2)

    def test_response_links_to_its_parent(self):
        author = member()
        parent = experience(author)
        self.client.force_login(author)
        self.client.post(
            reverse("respond", args=[parent.pk]),
            {"title": "Test answer", "body": "Test body.", "visibility": "public"},
        )
        self.assertEqual(parent.responses.get().title, "Test answer")


class ResonanceTests(TestCase):
    def test_resonating_twice_takes_it_back(self):
        shown = experience(member())
        self.client.force_login(member("reader"))
        url = reverse("resonate", args=[shown.pk])
        self.client.post(url)
        self.assertEqual(Resonance.objects.count(), 1)
        self.client.post(url)
        self.assertEqual(Resonance.objects.count(), 0)


class TagPageTests(TestCase):
    def test_tag_seen_only_in_community_posts_is_hidden_from_visitors(self):
        shown = experience(member(), Experience.Visibility.COMMUNITY)
        shown.phenomena.set(Phenomenon.from_names("Test phenomenon"))
        url = reverse("phenomenon", args=["test-phenomenon"])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertNotContains(self.client.get(reverse("home")), "Test phenomenon")
        self.client.force_login(member("reader"))
        self.assertContains(self.client.get(url), "Test phenomenon")
