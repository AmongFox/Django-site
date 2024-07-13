from django.contrib.auth.models import Group, Permission, User
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=4)

        group, created = Group.objects.get_or_create(
            name="profile_manager",

        )

        permission_profile = Permission.objects.get(
            codename="view_profile",
        )
        permission_logentry = Permission.objects.get(
            codename="view_logentry",
        )

        # Разрешения группы
        group.permissions.add(permission_profile)

        # Разрешения пользователя
        user.user_permissions.add(permission_logentry)

        # Добавление пользователя в группу
        user.groups.add(group)

        user.save()
        group.save()
