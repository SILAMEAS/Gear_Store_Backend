from django.contrib.auth import get_user_model

User = get_user_model()

email = "sila.meas@allweb.com.kh"
new_password = "test123"

try:
    user = User.objects.get(email=email,is_active=True)
    user.set_password(new_password)
    user.save()
    print(f"Password for superuser {email} has been reset successfully.")
except User.DoesNotExist:
    print(f"Superuser with email {email} does not exist.")


# python manage.py shell <reset_password.py