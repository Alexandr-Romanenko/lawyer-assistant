import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )

    class Meta:
        model = User
        fields = ('id', 'first_name', 'second_name', 'email', 'password', 'password2')

    def validate_name(self, value, field_name):
        if len(value) > 254:
            raise serializers.ValidationError({field_name: "The name must not exceed 254 characters."})
        if not re.match(r"^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ' -]+$", value):
            raise serializers.ValidationError({field_name: "The name may only contain letters, spaces, apostrophes, or hyphens."})

    def validate(self, data):
        first_name = data.get('first_name', '').strip()
        second_name = data.get('second_name', '').strip()
        password = data.get('password')
        password2 = data.get('password2')

        self.validate_name(first_name, 'first_name')
        self.validate_name(second_name, 'second_name')

        if password != password2:
            raise serializers.ValidationError({'password2': "Passwords do not match."})

        data['first_name'] = first_name
        data['second_name'] = second_name
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
