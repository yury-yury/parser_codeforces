from django.db import models
from django.utils.crypto import get_random_string

from users.models import User


class TgUser(models.Model):
    """
    The TgUser class inherits from the parent Model class from the django.db.models module. Defines fields
    and basic methods for working with database records from the 'tg_user' table.
    """
    chat_id = models.BigIntegerField(primary_key=True, editable=False, verbose_name='Чат ID')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    user_ud = models.BigIntegerField(null=True, blank=True, default=None)
    username = models.CharField(max_length=150, verbose_name='tg username', null=True, blank=True, default=None)
    verification_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        """
        The __str__ function overrides the method of the parent class. Does not accept other parameters except
        for the instance itself. Returns a human-readable representation of a class instance as a string.
        """
        return f'{self.__class__.__name__} {self.chat_id}'

    def update_verification_code(self) -> None:
        """
        The update_verification_code function defines a class method. Does not accept other parameters except
        for the instance itself. Calls the verification code generation method, writes the value to the corresponding
        field, and updates the database instance.
        """
        self.verification_code = self.generate_verification_code()
        self.save(update_fields=['verification_code'])

    @property
    def is_verified(self) -> bool:
        """
        The is_verified function defines the property method of the class. Does not accept other parameters except
        for the instance itself. Performs verification of the user's verification. If the telegram user is verified,
        it returns True, otherwise False.
        """
        return bool(self.user)

    @staticmethod
    def generate_verification_code() -> str:
        """
        The generate_verification_code function defines a static method of the class. Does not accept any parameters.
        Generates verification code using the get_random_string function from the django.utils.crypto module.
        Returns the generated code as a string.
        """
        return get_random_string(20)

