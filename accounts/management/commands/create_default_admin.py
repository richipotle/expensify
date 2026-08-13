"""
Comando de gestión que crea el usuario administrador por defecto.

Lee las credenciales desde variables de entorno (DJANGO_ADMIN_USERNAME,
DJANGO_ADMIN_EMAIL, DJANGO_ADMIN_PASSWORD) usando python-decouple, y crea
un superusuario con esas credenciales si aún no existe. Si el usuario ya
existe, no hace nada y solo informa al respecto (no lanza error).

Uso:
    python manage.py create_default_admin
"""

from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Crea el superusuario administrador por defecto a partir de las "
        "variables de entorno DJANGO_ADMIN_USERNAME, DJANGO_ADMIN_EMAIL "
        "y DJANGO_ADMIN_PASSWORD, si dicho usuario no existe todavía."
    )

    def handle(self, *args, **options):
        username = config('DJANGO_ADMIN_USERNAME', default='admin')
        email = config('DJANGO_ADMIN_EMAIL', default='admin@example.com')
        password = config('DJANGO_ADMIN_PASSWORD', default=None)

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"El usuario '{username}' ya existe. No se creó ningún "
                    "superusuario nuevo."
                )
            )
            return

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "No se definió DJANGO_ADMIN_PASSWORD en las variables de "
                    "entorno. No se puede crear el superusuario por defecto."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario '{username}' creado correctamente."
            )
        )
