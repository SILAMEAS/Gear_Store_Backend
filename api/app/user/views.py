from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from api.models import User
from api.app.user.serializer import UserSerializer

@extend_schema(tags=["User"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    # # GET
    def get_queryset(self):
        """Modify queryset based on action"""
        if self.action == "list":
            # If listing all users, return filtered queryset
            return User.objects.all()  # Example filter
        elif self.action == "retrieve" and self.request.user.is_superuser:
            # If retrieving a single user, return only that user
            return User.objects.filter(pk=self.kwargs["pk"])
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        """Customize list behavior"""
        if request.user.is_superuser:
            queryset = self.get_queryset()  # Admins see all active users
        elif request.user.is_staff:
            queryset = self.get_queryset()  # Admins see all active users
        else:
            queryset = self.get_queryset().filter(id=request.user.id)  # Regular users see only themselves
        serializer = self.get_serializer(queryset, many=True)
        if request.user.is_superuser:
            return Response(serializer.data)
        else:
            return Response(serializer.data[0])

    def retrieve(self, request, *args, **kwargs):
        """Customize retrieve behavior"""
        instance = self.get_object()
        if request.user.is_staff or instance == request.user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"detail": "Not allowed"}, status=403)

    @action(detail=False, methods=["get"])
    def info(self, request):
        """Returns details of the currently authenticated user."""
        user = request.user  # Get the logged-in user
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
        }
        return Response(user_data, status=status.HTTP_200_OK)