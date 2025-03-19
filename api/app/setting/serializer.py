from rest_framework import serializers
from api.models import Settings

# Review Serializer
class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = "__all__"