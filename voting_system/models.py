from django.db import models
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField()
    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return self.title


class Vote(models.Model):
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["voter", "post"], name="unique_vote_per_user_per_post"
            )
        ]
        indexes = [models.Index(fields=["post", "voter"])]
