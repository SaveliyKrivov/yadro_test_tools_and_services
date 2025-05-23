import sys
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """Загрузка 1000 профилей при запуске приложения."""
        if "test" not in sys.argv:
            post_migrate.connect(self.on_post_migrate, sender=self)

    def on_post_migrate(self, sender, **kwargs):
        try:
            from .models import Profile

            if Profile.objects.count() == 0:
                from .views import fetch_users, save_users_to_db

                print("Loading initial 1000 users from API...")
                users_data = fetch_users(1000)
                saved = save_users_to_db(users_data)
                print(f"Successfully loaded {saved} users")
        except Exception as e:
            print(f"Error during initial data loading: {e}")
