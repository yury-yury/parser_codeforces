from typing import List
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


class VerificationView(GenericAPIView):
    """
    The VerificationView class inherits from the GenericAPIView class from the rest_framework.generics
    module and is a class-based view for processing requests with PATCH method at the address
    '/bot/verify'.
    """
    permission_classes: List[BasePermission] = [IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args, **kwargs) -> Response:
        """
        The patch function overrides the method of the parent class. Accepts the request object as parameters,
        as well as other positional and named arguments. Validates the data contained in the request object.
        Sets the current user as the value of the user field. Sends a message to the user about successful verification.
        Returns a Response object.
        """
        serializer: ModelSerializer = TgUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user: TgUser = serializer.save(user=request.user)

        TgClient().send_message(chat_id=tg_user.chat_id, text='Bot token verified')

        return Response(serializer.data)
