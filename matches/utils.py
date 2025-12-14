from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Like, Match

User = get_user_model()


def get_users_for_feed(user, limit=20):
    """
    Возвращает пользователей для ленты (кроме себя и тех, кому уже поставлен лайк)
    """
    # Пользователи, которым уже поставлен лайк
    liked_user_ids = Like.objects.filter(sender=user).values_list('receiver_id', flat=True)

    # Исключаем себя и пользователей, которым уже поставили лайк
    users = User.objects.exclude(id=user.id).exclude(id__in=liked_user_ids)

    # Базовые фильтры (можно расширить)
    users = users.filter(is_active=True)

    return users.order_by('?')[:limit]  # Случайный порядок


def calculate_compatibility_score(user1, user2):
    """
    Рассчитывает совместимость на основе технологий и других параметров
    """
    score = 0

    # Совпадение по роли
    if user1.role and user2.role and user1.role == user2.role:
        score += 30

    # Совпадение по уровню (близкие уровни)
    level_order = ['trainee', 'junior', 'middle', 'senior', 'lead', 'head', 'cto']
    if user1.level in level_order and user2.level in level_order:
        idx1 = level_order.index(user1.level)
        idx2 = level_order.index(user2.level)
        level_diff = abs(idx1 - idx2)
        if level_diff <= 1:  # Разница не более 1 уровня
            score += 20

    # Совпадение по технологиям
    if user1.technologies and user2.technologies:
        tech1 = set([t.strip().lower() for t in user1.technologies.split(',')])
        tech2 = set([t.strip().lower() for t in user2.technologies.split(',')])
        common_tech = tech1.intersection(tech2)
        if common_tech:
            score += len(common_tech) * 10

    # Совпадение по городу
    if user1.city and user2.city and user1.city.lower() == user2.city.lower():
        score += 15

    # Совпадение по формату работы
    if user1.work_mode and user2.work_mode and user1.work_mode == user2.work_mode:
        score += 10

    # Ограничиваем максимальный балл
    return min(score, 100)


def get_mutual_matches(user):
    """Возвращает взаимные совпадения пользователя"""
    matches = Match.objects.filter(
        Q(user1=user) | Q(user2=user),
        is_active=True
    ).select_related('user1', 'user2')

    match_users = []
    for match in matches:
        other_user = match.user2 if match.user1 == user else match.user1
        match_users.append({
            'user': other_user,
            'match': match,
            'match_date': match.created_at
        })

    return match_users