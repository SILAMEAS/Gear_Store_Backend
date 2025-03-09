from django.contrib.auth import get_user_model

User = get_user_model()

email = "admin@gmail.com"
new_password = "admin"

try:
    user = User.objects.get(email=email,is_active=True)
    user.set_password(new_password)
    # Set role to admin
    user.role = "admin"  # Assuming "role" is a CharField or ChoiceField
    user.is_staff = True  # Allows access to Django Admin
    user.is_superuser = True  # Grants full admin privileges
    user.save()
    print(f"Password for superuser {email} has been reset successfully.")
except User.DoesNotExist:
    print(f"Superuser with email {email} does not exist.")


# python manage.py shell <reset_password.py