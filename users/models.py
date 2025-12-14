from django.contrib.auth.models import AbstractUser
from django.db import models


class ITUser(AbstractUser):

        # Добавляем IT-специфичные поля
        ROLE_CHOICES = [
            ('frontend', 'Frontend Developer'),
            ('backend', 'Backend Developer'),
            ('fullstack', 'Fullstack Developer'),
            ('mobile', 'Mobile Developer'),
            ('devops', 'DevOps Engineer'),
            ('data', 'Data Scientist/Analyst'),
            ('qa', 'QA Engineer'),
            ('designer', 'UX/UI Designer'),
            ('pm', 'Product Manager'),
            ('other', 'Другое'),
        ]

        LEVEL_CHOICES = [
            ('trainee', 'Стажер'),
            ('junior', 'Junior'),
            ('middle', 'Middle'),
            ('senior', 'Senior'),
            ('lead', 'Team Lead'),
            ('head', 'Head of'),
            ('cto', 'CTO'),
        ]

        role = models.CharField(
            max_length=20,
            choices=ROLE_CHOICES,
            blank=True,
            verbose_name='Роль'
        )

        level = models.CharField(
            max_length=10,
            choices=LEVEL_CHOICES,
            blank=True,
            verbose_name='Уровень'
        )

        bio = models.TextField(
            blank=True,
            verbose_name='О себе',
            help_text='Расскажите о своем опыте, проектах, интересах'
        )

        city = models.CharField(
            max_length=100,
            blank=True,
            verbose_name='Город'
        )

        # IT-специфичные поля
        technologies = models.TextField(
            blank=True,
            verbose_name='Технологии',
            help_text='Перечислите технологии, с которыми работаете (через запятую)'
        )

        github_profile = models.URLField(
            blank=True,
            verbose_name='GitHub профиль'
        )

        telegram = models.CharField(
            max_length=100,
            blank=True,
            verbose_name='Telegram'
        )

        looking_for = models.CharField(
            max_length=100,
            blank=True,
            verbose_name='Ищу',
            help_text='Что вы ищете на платформе? (друзей, проекты, работу и т.д.)'
        )

        work_mode = models.CharField(
            max_length=20,
            choices=[
                ('remote', 'Удалённо'),
                ('office', 'Офис'),
                ('hybrid', 'Гибрид'),
                ('any', 'Не важно'),
            ],
            blank=True,
            verbose_name='Формат работы'
        )

        experience_years = models.PositiveIntegerField(
            default=0,
            verbose_name='Опыт работы (лет)'
        )

        avatar = models.ImageField(
            upload_to='avatars/',
            blank=True,
            null=True,
            verbose_name='Аватар'
        )

        class Meta:
            verbose_name = 'IT пользователь'
            verbose_name_plural = 'IT пользователи'

        def __str__(self):
            role_display = self.get_role_display() if self.role else 'Пользователь'
            return f"{self.username} ({role_display})"

        def get_technologies_list(self):
            """Возвращает список технологий"""
            if self.technologies:
                return [tech.strip() for tech in self.technologies.split(',')]
            return []