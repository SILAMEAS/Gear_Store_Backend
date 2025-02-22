from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from api.models import User
from api.app.user.serializer import UserSerializer
from api.pagination import CustomPagination


@extend_schema(tags=["User"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
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
            # Apply pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)  # Uses CustomPagination
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

        # Construct the full URL for profile_image
        profile_image_url = None
        if user.profile_image:
            profile_image_url = request.build_absolute_uri(user.profile_image.url)

        # Format DOB as a string if it exists
        dob = user.dob.strftime('%d-%m-%Y') if user.dob else ""
        # Build the response dictionary with (pin) suffix
        user_data = {
            "id": str(user.id),  # Convert UUID to string for JSON serialization
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "profile_image": profile_image_url,
            "role": user.role,
            "phone": user.phone or "",
            "DOB": dob,
            "country": user.country or "",
            "City": user.city or "",
            "Postal_Code": user.postal_code or ""
        }
        return Response(user_data, status=status.HTTP_200_OK)
    @action(detail=False, methods=["get"])
    def staffs(self, request):
        """Customize list behavior with pagination and filter only superusers"""
        queryset = self.get_queryset().filter(is_staff=True)  # Filter only superusers

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # Uses CustomPagination

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # Fallback if pagination is disabled
    @action(detail=False, methods=["get"])
    def customers(self, request):
        """Customize list behavior with pagination and filter only superusers"""
        queryset = self.get_queryset().filter(is_active=True,is_superuser=False,is_staff=False)  # Filter only superusers

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # Uses CustomPagination

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # Fallback if pagination is disabled


from rest_framework import status, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.app.user.serializer import SignupSerializer

@extend_schema(tags=["Authentication"])
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)