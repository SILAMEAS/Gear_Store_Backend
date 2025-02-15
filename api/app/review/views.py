from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from api.app.review.serializer import ReviewSerializer
from api.models import Review
from api.pagination import CustomPagination


@extend_schema(tags=["Review"])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

