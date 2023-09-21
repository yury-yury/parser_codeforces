from dataclasses import field
from typing import Callable, Dict, Any, List

from django.core.management import BaseCommand
from django.db.models import Count
from marshmallow_dataclass import dataclass

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message, GetUpdatesResponse

from codeforces_data.models import Task, Category


@dataclass
class FSMData:
    """
    The FSMData dataclass is designed to validate incoming data and store the current state of the user dialog
    and the telegram bot.
    """
    next_handler: Callable
    data: Dict[str, Any] = field(default_factory=dict)


class Command(BaseCommand):
    """
    The Command class inherits from the base Command class from the django.core.management module. Designed
    to determine the functionality when working with a telegram bot.
    """
    help = 'The runbot command is designed to run the application with a telegram bot.'

    def __init__(self, *args, **kwargs) -> None:
        """
        The __init__ function is a method called when creating an instance of the Command class. Accepts
        any positional and named arguments. Makes a call to the base class method of the same name and supplements
        it with the creation of additional arguments.
        """
        super().__init__(*args, **kwargs)
        self.tg_client: TgClient = TgClient()
        self.client: Dict[int, FSMData] = {}

    def handle(self, *args, **options) -> None:
        """
        The handle function defines a class method to be called when entering a command. It contains the main
        functionality for organizing interaction with a telegram bot.
        """
        offset: int = 0
        self.stdout.write(self.style.SUCCESS('Bot started'))

        while True:
            res: GetUpdatesResponse = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset: int = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, message: Message) -> None:
        """
        The handle_message function defines a class method for processing an incoming message. Takes as an argument
        an object of the Message class. Checks user authentication and, depending on the result, calls the appropriate
        methods of the class.
        """
        tg_user, _ = TgUser.objects.get_or_create(chat_id=message.chat.id)

        if tg_user.is_verified:
            self.handle_authorized_user(tg_user, message)
        else:
            self.handle_unauthorized_user(tg_user, message)

    def handle_unauthorized_user(self, tg_user: TgUser, message: Message) -> None:
        """
        The handle_unauthorized_user function defines a class method for working with an unauthenticated user.
        Accept objects of the TgUser and Message classes as arguments. Sends a welcome message to the user, calls
        the method of adding the verification code to the field of the current user and sends the verification code.
        """
        self.tg_client.send_message(chat_id=message.chat.id, text='Hello')
        tg_user.update_verification_code()
        self.tg_client.send_message(chat_id=message.chat.id, text=f'You verification code: {tg_user.verification_code}')

    def handle_authorized_user(self, tg_user: TgUser, message: Message) -> None:
        """
        The handle_authorized_user function defines a class method for working with an authenticated user. Accept
        objects of the TgUser and Message classes as arguments. Checks the text of the received user message,
        if the text starts with "/" and is contained in the list of valid commands, calls the appropriate method,
        if the command is not included in the list, sends the message to the user. If the text is not a command,
        the client writes the text in the argument field.
        """
        if message.text and message.text.startswith('/'):
            if message.text == '/tasks':
                self.handle_tasks_command(tg_user=tg_user, message=message)

            elif message.text == '/cancel':
                self.client.pop(tg_user.chat_id, None)
                self.tg_client.send_message(chat_id=tg_user.chat_id, text='Canceled')

            else:
                self.tg_client.send_message(chat_id=message.chat.id, text='Command not found')

        elif tg_user.chat_id in self.client:
            client = self.client[tg_user.chat_id]
            client.next_handler(tg_user=tg_user, message=message, **client.data)

    def handle_tasks_command(self, tg_user: TgUser, message: Message) -> None:
        """
        The handle_goals_command function defines a class method for handling the '/goals' command. Accept objects
        of the TgUser and Message classes as arguments. Requests all the goals contained in the boards where
        the current user is a participant, and sends them a message in the appropriate format. If there are no goals,
        sends a message about it.
        """
        difficulties: List[int] = Task.objects.values_list('difficulty', flat=True).distinct()

        if not difficulties:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text='There are no tasks in the database.')
            return

        text: str = ('Select the required difficulty of tasks from the list:\n' +
                     '\n'.join(f'{str(i+1)}) {str(difficulty)}' for i, difficulty in enumerate(difficulties)))

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=text)
        self.client[tg_user.chat_id] = FSMData(None)
        self.client[tg_user.chat_id].next_handler = self.get_difficulty
        self.client[tg_user.chat_id].data = {'dif_list': difficulties}

    def get_difficulty(self, tg_user: TgUser, message: Message, **kwargs):
        if message.text and message.text.isdigit() and 0 < int(message.text) <= len(
                self.client[tg_user.chat_id].data['dif_list']):
            difficulty = self.client[tg_user.chat_id].data['dif_list'][int(message.text) - 1]

            self.tg_client.send_message(chat_id=tg_user.chat_id, text=f'The task difficulty is set to {difficulty}.')
            self.client[tg_user.chat_id].next_handler = self.get_category
            # self.client[tg_user.chat_id].data.pop('dif_list')
            self.client[tg_user.chat_id].data['difficulty'] = difficulty

        else:
            self.tg_client.send_message(chat_id=tg_user.chat_id,
                                        text='An incorrect problem difficulty number was entered. Try again.')
            return

        categories: List[Category] = Category.objects.all()

        if not categories:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text='There are no categories in the database.')
            return

        text: str = ('Select the required category of tasks from the list:\n' +
                     '\n'.join(f'{category.id}) {category.name}' for category in categories))

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=text)
        self.client[tg_user.chat_id].next_handler = self.get_category

    def get_category(self, tg_user: TgUser, message: Message, **kwargs):
        if message.text:
            try:
                category = Category.objects.get(pk=int(message.text))
            except Category.DoesNotExsist:
                self.tg_client.send_message(chat_id=tg_user.chat_id, text='Category not found')
            else:
                tasks = Task.objects.annotate(num_cat=Count('categories')).filter(num_cat=1)
                tasks = tasks.filter(categories__id=message.text, difficulty=kwargs['difficulty'])[:10]

                if tasks:
                    text = (f"The database contains the following problems with difficulty " +
                            f"{kwargs['difficulty']} and the topic {category.name}:\n" +
                            '\n'.join(f'№{task.number}) {task.name} number of solutions {task.solution}' for task in tasks))
                    self.tg_client.send_message(chat_id=tg_user.chat_id, text=text)
                    self.client.pop(tg_user.chat_id, None)

                else:
                    self.tg_client.send_message(chat_id=tg_user.chat_id,
                                                text='There are no tasks in the database. Try again')
                    self.handle_tasks_command(tg_user=tg_user, message=message)
