from django.db import models
from users.models import ITUser
# Create your models here.


class Like(models.Model):
    sender = models.ForeignKey(ITUser, on_delete=models.CASCADE, related_name='sent_likes')
    receiver = models.ForeignKey(ITUser, on_delete=models.CASCADE, related_name='received_likes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['sender', 'receiver']


class Match(models.Model):
    user1 = models.ForeignKey(ITUser, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(ITUser, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"Match between {self.user1.username} and {self.user2.username}"