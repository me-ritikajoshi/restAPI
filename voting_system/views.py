from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post, Vote
from .serializers import (
    LoginSerializer,
    PostSerializer,
    SignupSerializer,
    VoteSerializer,
)

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.select_related("poster").annotate(
        vote_count=Count("votes")
    ).order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)


class VoteCreate(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs["pk"])

    def perform_create(self, serializer):
        post = self.get_post()
        if Vote.objects.filter(voter=self.request.user, post=post).exists():
            raise ValidationError("You have already voted for this post.")
        try:
            with transaction.atomic():
                serializer.save(voter=self.request.user, post=post)
        except IntegrityError as exc:
            raise ValidationError("You have already voted for this post.") from exc

    def delete(self, request, *args, **kwargs):
        post = self.get_post()
        deleted, _ = Vote.objects.filter(
            voter=self.request.user, post=post
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError("You never voted for this post.")


class IsPostOwner(permissions.BasePermission):
    message = "You are not authorized to delete this post."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.poster_id == request.user.id


class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.select_related("poster").annotate(
        vote_count=Count("votes")
    ).order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPostOwner]


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.create_user(**serializer.validated_data)
        except IntegrityError as exc:
            raise ValidationError({"username": ["Username already exists."]}) from exc
        token = Token.objects.create(user=user)
        return Response({"token": str(token)}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            raise ValidationError({"detail": ["Username and password do not match."]})
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
