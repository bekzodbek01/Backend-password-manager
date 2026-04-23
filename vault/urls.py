from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CredentialViewSet,
    RegisterView,
    LoginView,
    UnlockView,
    export_vault, ChangePasswordView, ChangeMasterPasswordView, ClearVaultView
)

router = DefaultRouter()
router.register("credentials", CredentialViewSet, basename="credentials")

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("unlock/", UnlockView.as_view()),
    path("export/", export_vault),
    path("", include(router.urls)),
    path("change-password/", ChangePasswordView.as_view()),
    path("change-master/", ChangeMasterPasswordView.as_view()),
    path("clear-vault/", ClearVaultView.as_view()),
]