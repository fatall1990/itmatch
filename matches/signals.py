from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Match


@receiver(post_save, sender=Like)
def check_for_match(sender, instance, created, **kwargs):
    """Проверяет и создает совпадение при взаимном лайке"""
    if created:
        try:
            # Проверяем есть ли обратный лайк
            mutual_like_exists = Like.objects.filter(
                sender=instance.receiver,
                receiver=instance.sender
            ).exists()

            if mutual_like_exists:
                # Определяем порядок пользователей
                user1, user2 = sorted([instance.sender, instance.receiver], key=lambda u: u.id)

                # Создаем или получаем существующее совпадение
                Match.objects.get_or_create(
                    user1=user1,
                    user2=user2,
                    defaults={'is_active': True}
                )
        except Exception as e:
            print(f"Error in check_for_match signal: {e}")