from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Vote


class PostSerializer(serializers.ModelSerializer):
    poster = serializers.ReadOnlyField(source="poster.username")
    poster_id = serializers.ReadOnlyField(source="poster.id")
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "url", "poster", "poster_id", "created_at", "votes"]

    def get_votes(self, post):
        vote_count = getattr(post, "vote_count", None)
        if vote_count is not None:
            return vote_count
        return post.votes.count()


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id"]


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists.")
        return username


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
