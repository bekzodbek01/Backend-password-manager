from rest_framework import serializers
from .models import Credential
from .utils.encryption import decrypt_password
from .models import User


from django.contrib.auth.hashers import make_password

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'master_password']

    def create(self, validated_data):
        master = validated_data.pop("master_password")

        user = User(
            username=validated_data["username"],
            master_password=make_password(master)  # 🔐 HASH
        )

        user.set_password(validated_data["password"])  # 🔐 HASH
        user.save()

        return user


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = "__all__"
        read_only_fields = ["user"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")
        master = request.query_params.get("master_password")

        if master:
            try:
                data["password"] = decrypt_password(master, instance.password)
            except:
                data["password"] = "❌ wrong master"

        return data