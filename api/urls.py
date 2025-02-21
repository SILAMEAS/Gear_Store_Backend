from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.app.product.views import ProductViewSet
from api.app.user.views import UserViewSet, SignupView
from api.app.wishlist.views import WishlistViewSet
from api.app.order.views import OrderViewSet,OrderItemViewSet
from api.app.category.views import CategoryViewSet
from api.app.cart.views import CartViewSet
from api.app.payment.views import PaymentViewSet
from api.app.review.views import ReviewViewSet
from api.app.shipping.views import ShippingAddressViewSet
from api.app.dashboard.views import DashboardSummaryView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema
# Router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'cart', CartViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'shipping-addresses', ShippingAddressViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'wishlist', WishlistViewSet)

# URL Patterns
urlpatterns = [
    # Dashboard Summary
    path("api/admin/dashboard", DashboardSummaryView.as_view()),
    path("signup/", SignupView.as_view(), name="signup"),
    # Url
    path('api/', include(router.urls)),
    # Auth
    path('api/token/',
         extend_schema(tags=["Auth"])(TokenObtainPairView).as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/',
         extend_schema(tags=["Auth"])(TokenRefreshView).as_view(),
         name='token_refresh'),
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)