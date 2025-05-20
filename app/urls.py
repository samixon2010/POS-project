from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    RegisterUser, LoginUser,
    ProductCreateView, UpdateDelateProductView,
    TranssactionView, UpdateDeleteTransactionView,
    ProductLogListView,
)


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    # Authenticatons
    path('register/', RegisterUser.as_view()),
    path('login/', LoginUser.as_view()),
    # Crud methods on products
    path('products/', ProductCreateView.as_view()),
    path('products/<int:pk>/', UpdateDelateProductView.as_view()),
    # Crud methods on transaction
    path('transactions/', TranssactionView.as_view()),
    path('transactions/<int:pk>/', UpdateDeleteTransactionView.as_view()),
    # Logs
    path('logs/', ProductLogListView.as_view()),

    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]