from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Post, Vote


class VotingApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="strong-pass-123")
        self.other_user = User.objects.create_user(
            username="bob", password="strong-pass-456"
        )
        self.post = Post.objects.create(
            title="Useful resource",
            url="https://example.com",
            poster=self.user,
        )

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_signup_returns_token(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "newuser", "password": "new-pass-123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_login_returns_existing_token(self):
        existing_token, _ = Token.objects.get_or_create(user=self.user)
        response = self.client.post(
            reverse("login"),
            {"username": "alice", "password": "strong-pass-123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], existing_token.key)

    def test_unauthenticated_user_cannot_create_post(self):
        response = self.client.post(
            reverse("post-list"),
            {"title": "No auth", "url": "https://example.com/denied"},
            format="json",
        )
        self.assertIn(
            response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}
        )

    def test_authenticated_user_can_create_post(self):
        self.authenticate(self.other_user)
        response = self.client.post(
            reverse("post-list"),
            {"title": "Created", "url": "https://example.com/created"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["poster"], "bob")

    def test_user_can_vote_once_only(self):
        self.authenticate(self.other_user)
        first_vote = self.client.post(reverse("post-vote", kwargs={"pk": self.post.pk}))
        self.assertEqual(first_vote.status_code, status.HTTP_201_CREATED)

        second_vote = self.client.post(reverse("post-vote", kwargs={"pk": self.post.pk}))
        self.assertEqual(second_vote.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.filter(post=self.post, voter=self.other_user).count(), 1)

    def test_vote_can_be_removed(self):
        Vote.objects.create(post=self.post, voter=self.other_user)
        self.authenticate(self.other_user)
        response = self.client.delete(reverse("post-vote", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Vote.objects.filter(post=self.post, voter=self.other_user).exists())

    def test_only_owner_can_delete_post(self):
        self.authenticate(self.other_user)
        response = self.client.delete(reverse("post-detail", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_list_contains_vote_count(self):
        Vote.objects.create(post=self.post, voter=self.other_user)
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["votes"], 1)
