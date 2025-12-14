from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from users.models import ITUser
from .models import Like, Match
from .utils import get_users_for_feed, calculate_compatibility_score, get_mutual_matches


@login_required
def user_feed(request):
    """Лента пользователей"""
    users = get_users_for_feed(request.user, limit=20)

    # Добавляем оценку совместимости для каждого пользователя
    users_with_score = []
    for user in users:
        score = calculate_compatibility_score(request.user, user)
        users_with_score.append({
            'user': user,
            'compatibility_score': score,
            'tech_list': user.get_technologies_list()[:5],  # Первые 5 технологий
        })

    context = {
        'users': users_with_score,
        'matches_count': Match.objects.filter(
            user1=request.user, is_active=True
        ).count() + Match.objects.filter(
            user2=request.user, is_active=True
        ).count()
    }

    return render(request, 'matches/feed.html', context)

import logging
logger = logging.getLogger(__name__)

@login_required
@require_POST
@csrf_exempt
def send_like(request, user_id):
    try:
        logger.info(f"User {request.user.id} sending like to user {user_id}")

        receiver = get_object_or_404(ITUser, id=user_id)

        # Проверяем не лайкаем ли мы себя
        if receiver == request.user:
            logger.warning(f"User {request.user.id} tried to like themselves")
            return JsonResponse({'error': 'Нельзя поставить лайк самому себе'}, status=400)

        # Проверяем не лайкали ли уже
        like_exists = Like.objects.filter(
            sender=request.user,
            receiver=receiver
        ).exists()

        if like_exists:
            logger.warning(f"User {request.user.id} already liked user {user_id}")
            return JsonResponse({'error': 'Вы уже поставили лайк этому пользователю'}, status=400)

        # Создаем лайк
        like = Like.objects.create(sender=request.user, receiver=receiver)
        logger.info(f"Like created: {like.id}")

        # Проверяем на взаимный лайк
        logger.info(f"Checking for mutual like with {receiver.id}")
        mutual_like_exists = Like.objects.filter(
            sender=receiver,
            receiver=request.user
        ).exists()

        response_data = {
            'success': True,
            'like_id': like.id,
            'has_match': mutual_like_exists,
        }

        if mutual_like_exists:
            logger.info(f"Mutual like found! Creating match...")
            # Создаем совпадение
            match, created = Match.objects.get_or_create(
                user1=min(request.user, receiver, key=lambda u: u.id),
                user2=max(request.user, receiver, key=lambda u: u.id),
                defaults={'is_active': True}
            )
            response_data['match_id'] = match.id
            response_data['match_message'] = 'Это взаимная симпатия!'
            logger.info(f"Match {'created' if created else 'exists'}: {match.id}")

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error in send_like: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Произошла ошибка: {str(e)}'}, status=500)


@login_required
@require_POST
@csrf_exempt
def send_dislike(request, user_id):
    """Отправка дизлайка (просто пропускаем пользователя)"""
    receiver = get_object_or_404(ITUser, id=user_id)

    # Для дизлайка просто отмечаем что видели пользователя
    # Можно сохранять в историю просмотров, но пока просто возвращаем успех
    return JsonResponse({'success': True})


@login_required
def matches_list(request):
    """Список взаимных совпадений"""
    mutual_matches = get_mutual_matches(request.user)

    context = {
        'matches': mutual_matches,
    }

    return render(request, 'matches/matches.html', context)


@login_required
def match_detail(request, match_id):
    """Детальная страница совпадения"""
    match = get_object_or_404(Match, id=match_id)

    # Проверяем что пользователь участник совпадения
    if request.user not in [match.user1, match.user2]:
        messages.error(request, 'У вас нет доступа к этому совпадению')
        return redirect('matches_list')

    other_user = match.user2 if match.user1 == request.user else match.user1

    context = {
        'match': match,
        'other_user': other_user,
        'compatibility_score': calculate_compatibility_score(request.user, other_user)
    }

    return render(request, 'matches/match_detail.html', context)


@login_required
def debug_info(request):
    """Страница для отладки - показывает текущие лайки и совпадения"""
    sent_likes = Like.objects.filter(sender=request.user).select_related('receiver')
    received_likes = Like.objects.filter(receiver=request.user).select_related('sender')

    matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2')

    context = {
        'sent_likes': sent_likes,
        'received_likes': received_likes,
        'matches': matches,
    }

    return render(request, 'matches/debug.html', context)