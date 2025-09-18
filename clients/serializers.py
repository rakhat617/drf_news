from rest_framework import serializers
from clients.models import ActivationCode
from django.contrib.auth import get_user_model

Client = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Client
        fields = ("email", "password")

    def create(self, validated_data):
        client = Client.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False  # активируем только после подтверждения
        )
        return client
    


class ActivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=64)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        try:
            client = Client.objects.get(email=email)
        except Client.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь не найден"})

        try:
            activation = ActivationCode.objects.get(client=client, code=code)
        except ActivationCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Неверный код активации"})

        if client.is_active:
            raise serializers.ValidationError({"email": "Аккаунт уже активирован"})

        attrs["client"] = client
        attrs["activation"] = activation
        return attrs

    def save(self, **kwargs):
        client = self.validated_data["client"]
        activation = self.validated_data["activation"]

        client.is_active = True
        client.save()

        # Можно удалить код после активации
        activation.delete()
        return client