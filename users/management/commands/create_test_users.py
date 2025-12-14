from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовых IT-пользователей'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, default=10, help='Количество пользователей для создания')

    def handle(self, *args, **options):
        fake = Faker('ru_RU')
        count = options['count']

        roles = [choice[0] for choice in User._meta.get_field('role').choices]
        levels = [choice[0] for choice in User._meta.get_field('level').choices]
        work_modes = [choice[0] for choice in User._meta.get_field('work_mode').choices]

        tech_stacks = [
            'Python, Django, PostgreSQL, Docker',
            'JavaScript, React, Node.js, MongoDB',
            'Java, Spring, MySQL, AWS',
            'C#, .NET, SQL Server, Azure',
            'PHP, Laravel, MySQL, Linux',
            'Python, FastAPI, MongoDB, Docker',
            'TypeScript, Angular, Node.js, PostgreSQL',
            'Go, Gin, PostgreSQL, Kubernetes',
            'Swift, iOS, Firebase',
            'Kotlin, Android, Room, Jetpack'
        ]

        for i in range(count):
            username = fake.user_name()
            email = fake.email()

            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=random.choice(roles),
                level=random.choice(levels),
                bio=fake.text(max_nb_chars=200),
                city=fake.city(),
                technologies=random.choice(tech_stacks),
                github_profile=f'https://github.com/{username}',
                telegram=f'@{username}',
                looking_for=random.choice(['Проекты', 'Друзей', 'Ментора', 'Работу', 'Коллаборацию']),
                work_mode=random.choice(work_modes),
                experience_years=random.randint(0, 15)
            )

            self.stdout.write(
                self.style.SUCCESS(f'Создан пользователь: {user.username} ({user.get_role_display()})')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {count} тестовых пользователей!')
        )