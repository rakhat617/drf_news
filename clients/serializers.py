from rest_framework import serializers
from clients.models import ActivationCode
from django.contrib.auth import get_user_model

# Вот такой импорт более гибкий, ибо вдруг в будущем поменяется 
# наша моделька юзеров, которая типа дефолтная для аутентификации
# И в таком случае тут даже менять ничего не надо будет
# Хотя конечно в данном проекте это лишнее
Client = get_user_model()

# Самый простой модел сериалайзер 
# за исключением того, что мы переписываем метод create 
# потому что не зря же мы делали наш ClientManager ))
# Ну и если не переписать, то как минимум пароль не захешируется
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Client
        fields = ("email", "password")

    def create(self, validated_data):
        client = Client.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return client
    

# Здесь сериализатор для активации 
# с проверкой на имейл, и на сам, собственно, код 
# ну и на то активен ли уже пользователь
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
        
        if client.is_active:
            raise serializers.ValidationError({"email": "Аккаунт уже активирован"})

        try:
            activation = ActivationCode.objects.get(client=client, code=code)
        except ActivationCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Неверный код активации"})

        attrs["client"] = client
        attrs["activation"] = activation
        return attrs

    def save(self, **kwargs):
        client = self.validated_data["client"]
        activation = self.validated_data["activation"]

        client.is_active = True
        client.save()

        # Тут вот как раз я удаляю код активации из базы данных
        # ибо он уже не нужен по сути
        activation.delete()
        return client