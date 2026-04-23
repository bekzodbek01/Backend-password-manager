from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, CredentialSerializer
from .models import Credential
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .utils.security import verify_master
from .utils.encryption import encrypt_password

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password

# 🔐 EXPORT (SAFE VERSION)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_vault(request):
    data = Credential.objects.filter(user=request.user).values(
        "id",
        "service_name",
        "username",
        "url",
        "notes",
        "created_at"
    )
    return JsonResponse(list(data), safe=False)


# 🔐 UNLOCK
class UnlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        master = request.data.get("master_password")

        if not master:
            return Response({"error": "Master password required"}, status=400)

        if verify_master(request.user, master):
            return Response({"status": "ok"})

        return Response({"error": "Wrong master password"}, status=400)


# 🧾 REGISTER
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "registered"}, status=201)

        return Response(serializer.errors, status=400)


# 🔑 LOGIN
class LoginView(APIView):
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password")
        )

        if not user:
            return Response({"error": "Invalid login"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


# 🔐 VAULT CRUD
class CredentialViewSet(ModelViewSet):
    serializer_class = CredentialSerializer
    permission_classes = [IsAuthenticated]

    # 🔍 SEARCH + USER FILTER
    def get_queryset(self):
        qs = Credential.objects.filter(user=self.request.user)

        search = self.request.query_params.get("search")

        if search:
            qs = qs.filter(
                service_name__icontains=search
            ) | qs.filter(
                username__icontains=search
            )

        return qs

    # ➕ CREATE (ENCRYPT PASSWORD)
    def perform_create(self, serializer):
        master = self.request.data.get("master_password")

        if not verify_master(self.request.user, master):
            raise ValidationError({"error": "Wrong master password"})

        password = self.request.data.get("password")

        if not password:
            raise ValidationError({"error": "Password required"})

        encrypted = encrypt_password(master, password)

        serializer.save(
            user=self.request.user,
            password=encrypted
        )

    # ✏️ UPDATE (ENCRYPT AGAIN)
    def perform_update(self, serializer):
        master = self.request.data.get("master_password")

        if not verify_master(self.request.user, master):
            raise ValidationError({"error": "Wrong master password"})

        password = self.request.data.get("password")

        if password:
            encrypted = encrypt_password(master, password)
            serializer.save(password=encrypted)
        else:
            serializer.save()

    # ❌ DELETE
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        obj.delete()
        return Response({"msg": "deleted"})



# 🔑 PASSWORD CHANGE
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        user = request.user

        if not user.check_password(old_password):
            return Response({"error": "Wrong password"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"msg": "Password updated"})


# 🔐 MASTER PASSWORD CHANGE
class ChangeMasterPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_master = request.data.get("old_master")
        new_master = request.data.get("new_master")

        user = request.user

        if not verify_master(user, old_master):
            return Response({"error": "Wrong master password"}, status=400)

        user.master_password = make_password(new_master)
        user.save()

        return Response({"msg": "Master password updated"})


# 💀 DANGER ZONE — CLEAR VAULT
class ClearVaultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.credentials.all().delete()
        return Response({"msg": "Vault cleared"})