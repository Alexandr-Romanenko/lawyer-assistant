from rest_framework import serializers 
from auth.models import User 


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')
    
        # Проверка на уникальность email
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': "Пользователь с таким email уже существует."
            })
    
        # Проверка совпадения паролей
        if password != password2:
            raise serializers.ValidationError({
                'password2': "Пароли не совпадают."
            })
    
        return data


    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
