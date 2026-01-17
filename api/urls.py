from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.user_views import RegisterView, UserProfileView, CustomTokenObtainPairView
from api.views.category_views import CategoryViewSet, CategoryTreeView
from api.views.product_views import ProductViewSet
from api.views.order_views import OrderViewSet
from api.views.payment_views import InitiatePaymentView, ConfirmPaymentView, StripeWebhookView, PaymentViewSet
from api.views.ssl_views import SSLPaymentCallbackView
from api.views.stripe_checkout_views import StripeSuccessView, StripeCancelView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # Payments 
    path('payments/initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('payments/confirm/', ConfirmPaymentView.as_view(), name='payment-confirm'),
    path('payments/webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payments/ssl/callback/', SSLPaymentCallbackView.as_view(), name='ssl-callback'),
    path('payments/stripe/success/', StripeSuccessView.as_view(), name='stripe-success'),
    path('payments/stripe/cancel/', StripeCancelView.as_view(), name='stripe-cancel'),

    # Core
    path('', include(router.urls)),
    path('category-tree/', CategoryTreeView.as_view(), name='category-tree'),
    
    # Docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
