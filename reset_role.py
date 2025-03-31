import os
import django

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gear_store.settings")

# Initialize Django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = "admin@gmail.com"
new_password = "admin"

try:
    user = User.objects.get(email=email, is_active=True)
    # Set role to admin
    user.role = "admin"  # Ensure your User model has this field
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"{email}: role has been reset successfully.")
except User.DoesNotExist:
    print(f"Superuser with email {email} does not exist.")
