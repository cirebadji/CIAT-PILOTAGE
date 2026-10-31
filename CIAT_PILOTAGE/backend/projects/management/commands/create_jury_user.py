import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Crée ou met à jour le compte utilisateur de démonstration du jury."

    def handle(self, *args, **options):
        username = os.getenv("CIAT_ADMIN_USERNAME", "jury").strip()
        password = os.getenv("CIAT_ADMIN_PASSWORD", "")
        email = os.getenv("CIAT_ADMIN_EMAIL", "").strip()
        if not username or not password:
            self.stdout.write("Compte jury non créé : CIAT_ADMIN_PASSWORD est absent.")
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        if email and user.email != email:
            user.email = email
        user.is_active = True
        # Le compte jury est un utilisateur applicatif, pas un superutilisateur Django.
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save()
        action = "créé" if created else "mis à jour"
        self.stdout.write(self.style.SUCCESS(f"Compte utilisateur du jury {action} : {username}"))
