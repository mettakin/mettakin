from django.test import TestCase
from django.urls import reverse

from experiences.tests import member

from .models import Idea, Vote


class IdeaTests(TestCase):
    def test_proposing_needs_an_account_and_counts_your_vote(self):
        self.assertEqual(self.client.get(reverse("propose")).status_code, 302)
        self.client.force_login(member())
        self.client.post(reverse("propose"), {"title": "Test idea", "body": "Test body."})
        self.assertEqual(Vote.objects.get().idea.title, "Test idea")

    def test_most_wanted_ideas_come_first(self):
        author = member()
        quiet = Idea.objects.create(author=author, title="Test quiet", body="Test.")
        wanted = Idea.objects.create(author=author, title="Test wanted", body="Test.")
        Vote.objects.create(member=author, idea=wanted)
        self.assertEqual(list(Idea.objects.ranked()), [wanted, quiet])

    def test_voting_twice_takes_it_back(self):
        shown = Idea.objects.create(author=member(), title="Test", body="Test.")
        self.client.force_login(member("voter"))
        url = reverse("vote", args=[shown.pk])
        self.client.post(url)
        self.assertEqual(shown.votes.count(), 1)
        self.client.post(url)
        self.assertEqual(shown.votes.count(), 0)

    def test_visitors_read_but_members_talk(self):
        shown = Idea.objects.create(author=member(), title="Test", body="Test.")
        response = self.client.post(shown.get_absolute_url(), {"body": "Test comment."})
        self.assertRedirects(response, f"{reverse('login')}?next={shown.get_absolute_url()}")
        self.client.force_login(member("talker"))
        self.client.post(shown.get_absolute_url(), {"body": "Test comment."})
        self.assertContains(self.client.get(shown.get_absolute_url()), "Test comment.")
