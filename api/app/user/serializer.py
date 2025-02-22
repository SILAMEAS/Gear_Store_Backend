from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from api.models import User

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "dob",
            "is_active",
            "profile_image",
            "role",
            "phone",
            "dob",
            "country",
            "city",
            "postal_code",
            "password"
        ]

    def validate(self, attrs):
        """Ensure password is required during creation but optional on update."""
        if not self.instance and "password" not in attrs:  # Creating a new user
            raise serializers.ValidationError({"password": ["This field is required."]})
        return attrs
    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        else:
            validated_data.pop("password", None)  # Remove password if not provided
        return super().update(instance, validated_data)


from django.contrib.auth import get_user_model

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password","is_staff","first_name","last_name","dob","phone","postal_code"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user