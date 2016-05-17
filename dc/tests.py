import datetime

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from .models import Node


class NodeTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='jacob', email='jacob@jacob.net', password='top_secret')
		
	def test_private_key_is_correctly_stored(self):
		node = Node(user=self.user)
		node.generate_key()
		print node.key.path
		self.assertEqual(node.key.name, 'key_store/{0}/{1}/key.pem'.format(self.user.id, node.uuid))
		
		
class SimpleTest(TestCase):
    def setUp(self):
		self.user = User.objects.create_user(username='jacob', email='jacob@jacob.net', password='top_secret')

    def test_secure_page(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/nodes/', follow=True)
        self.assertEqual(response.context['email'], 'temporary@gmail.com')