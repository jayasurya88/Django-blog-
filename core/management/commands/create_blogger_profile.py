from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Blogger

class Command(BaseCommand):
    help = 'Creates a Blogger profile for an existing user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            if not hasattr(user, 'blogger'):
                Blogger.objects.create(
                    user=user,
                    bio=''
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created Blogger profile for {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already has a Blogger profile'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist')) 