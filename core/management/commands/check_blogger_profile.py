from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Blogger

class Command(BaseCommand):
    help = 'Checks if a user has a Blogger profile'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'blogger'):
                self.stdout.write(self.style.SUCCESS(f'User {username} has a Blogger profile'))
                blogger = user.blogger
                self.stdout.write(f'Bio: {blogger.bio}')
                self.stdout.write(f'Profile Picture: {"Yes" if blogger.profile_picture else "No"}')
            else:
                self.stdout.write(self.style.ERROR(f'User {username} does NOT have a Blogger profile'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist')) 