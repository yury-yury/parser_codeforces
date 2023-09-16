from typing import List

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """
    The UserCreateSerializer class inherits from the ModelSerializer class from rest_framework.serializers.
    This is a class for convenient serialization and deserialization of objects of the User class when processing
    create new instance of User class.
    """
    id = serializers.IntegerField(required=False)
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        """
        The Meta class is an internal service class of the serializer,
        defines the necessary parameters for the serializer to function.
        """
        model = User
        fields: List[str] = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat']

    def validate(self, attrs) -> dict:
        """
        The validate function overrides the method of the parent class. Takes the values of the class instance
        attributes as parameters. Calls the parent method and adds password complexity checks in accordance with
        the specified validators and the coincidence of the received values 'password' and 'password_repeat',
        raises a ValidationError exception if there are differences. After comparison, deletes the key and the value
        of 'password_repeat'. Returns the date object.
        """
        data: dict = super().validate(attrs)
        validate_password(data['password'])
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError('The entered passwords must match')
        del data['password_repeat']
        return data

    def create(self, validated_data) -> User:
        """
        The create function overrides the method of the parent class. Takes validated_data values as parameters.
        Creates an instance of the User class, adds the value of the hashed password, and stores the object
        in the database. Returns the created object.
        """
        user: User = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    """
    The LoginSerializer class inherits from the ModelSerializer class from rest_framework.serializers.
    This is a class for convenient serialization and deserialization of objects of the User class when processing
    login instance of User class.
    """
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        """
        The Meta class is an internal service class of the serializer,
        defines the necessary parameters for the serializer to function.
        """
        model = User
        fields: str = '__all__'

    def create(self, validated_data) -> User:
        """
        The create function overrides the method of the parent class. Takes validated_data values as parameters.
        Authenticates an instance of the User class according to the values received, raises an AuthenticationFailed
        exception if there is no user information or incorrect data in the database. Returns the found object.
        """
        user = authenticate(username=validated_data['username'], password=validated_data['password'])
        if user is None:
            raise AuthenticationFailed
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    The UserSerializer class inherits from the ModelSerializer class from rest_framework.serializers.
    This is a class for convenient serialization and deserialization of objects of the User class.
    """
    class Meta:
        """
        The Meta class is an internal service class of the serializer,
        defines the necessary parameters for the serializer to function.
        """
        model = User
        fields: List[str] = ['id', 'username', 'first_name', 'last_name', 'email']


class UpdatePasswordSerializer(serializers.Serializer):
    """
    The UpdatePasswordSerializer class inherits from the ModelSerializer class from rest_framework.serializers.
    This is a class for convenient serialization and deserialization of objects of the User class when processing
    update password of instance of User class.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs: dict) -> dict:
        """
        The validate function overrides the method of the parent class. Accepts the attrs object as parameters.
        Checks the presence of user authentication and the correctness of the entered value 'old_password' in case
        of incorrect data raises a ValidationError exception. Returns the object received as a parameter.
        """
        user: User = attrs['user']
        if not user:
            raise NotAuthenticated
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'uncorrect password'})
        return attrs

    def create(self, validated_data) -> None:
        """
        The create function overrides the method of the parent class. Accepts the validated_data object as parameters.
        If the method is called, raises the NotImplementedError exception. The method is not used in this serializer.
        """
        raise NotImplementedError

    def update(self, instance: User, validated_data) -> User:
        """
        The update function overrides the method of the parent class. Accepts instance objects as parameters
        an instance of the User class and validated_data. If the method is called, it updates the value
        of the 'password' field and saving the updated instance in the database. Returns an updated instance
        of the User class.
        """
        instance.password = make_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance


