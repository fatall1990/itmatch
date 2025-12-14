from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Like(models.Model):
    """Модель для лайков между пользователями"""
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_likes',
        verbose_name='Отправитель'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_likes',
        verbose_name='Получатель'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ['sender', 'receiver']  # Один лайк от пользователя к пользователю
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"

    def clean(self):
        # Нельзя лайкнуть самого себя
        if self.sender == self.receiver:
            raise ValidationError('Нельзя поставить лайк самому себе')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Match(models.Model):
    """Модель для совпадений (взаимных лайков)"""
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_user1',
        verbose_name='Пользователь 1'
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_user2',
        verbose_name='Пользователь 2'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    class Meta:
        verbose_name = 'Совпадение'
        verbose_name_plural = 'Совпадения'
        unique_together = ['user1', 'user2']
        ordering = ['-created_at']

    def __str__(self):
        return f"Match: {self.user1.username} ↔ {self.user2.username}"

    def save(self, *args, **kwargs):
        # Убедимся что user1.id < user2.id для уникальности
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    @classmethod
    def create_match_if_mutual(cls, like):
        """Создает совпадение если есть взаимный лайк"""
        try:
            # Проверяем есть ли обратный лайк
            mutual_like_exists = Like.objects.filter(
                sender=like.receiver,
                receiver=like.sender
            ).exists()

            if mutual_like_exists:
                # Определяем порядок пользователей (user1.id < user2.id)
                user1, user2 = sorted([like.sender, like.receiver], key=lambda u: u.id)

                # Создаем или получаем существующее совпадение
                match, created = cls.objects.get_or_create(
                    user1=user1,
                    user2=user2,
                    defaults={'is_active': True}
                )
                return match, created
            return None, False
        except Exception as e:
            print(f"Error in create_match_if_mutual: {e}")
            return None, False