from django.test import TestCase

from users.models import AppUser
from team.models import Player


class PlayerTestCase(TestCase):
    def setUp(self):
        self.email = 'test@test.com'
        AppUser.objects.create_user(self.email)

    def test_player_created_on_appuser_create(self):
        player = Player.objects.get(nickname=self.email)
        print(player.user.password)
        assert player.user.email == self.email
