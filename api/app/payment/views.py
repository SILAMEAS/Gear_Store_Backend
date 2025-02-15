
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from api.app.payment.serializer import PaymentSerializer
from api.models import Payment
from api.pagination import CustomPagination


@extend_schema(tags=["Payment"])
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    # GET
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
