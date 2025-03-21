from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.app.review.serializer import ReviewSerializer
from api.app.setting.models import Settings
from rest_framework import status

from api.app.setting.serializer import SettingSerializer


@extend_schema(tags=["Settings"])
class SettingsViewSet(viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingSerializer

    def list(self, request, *args, **kwargs):
        """Override list to return a single object instead of a list"""
        instance = Settings.objects.first()  # Get the first object
        print(instance)
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)  # Return a single object
        return Response({"detail": "No settings found"}, status=status.HTTP_404_NOT_FOUND)

