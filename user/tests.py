from django.test import TestCase
from django.test import Client
from django.urls import reverse
from user.models import User


class loginTest(TestCase):

    def setUp(self):
        User.objects.create(id=20373615, password=20373615, security_issue="20373615", security_answer="20373615")

    def testCase1(self):
        client = Client()
        res = client.post(reverse('user:login'), {'id': 114514, 'password': 114514})
        res_data = res.json()
        self.assertEqual(res_data.get('errno'), 2003)

    def testCase2(self):
        client = Client()
        res = client.post(reverse('user:login'), {'id': 20373615, 'password': 1919810})
        res_data = res.json()
        self.assertEqual(res_data.get('errno'), 2002)


    def testCase3(self):
        client = Client()
        res = client.post(reverse('user:login'), {'id': 20373615, 'password': 20373615})
        res_data = res.json()
        self.assertEqual(res_data.get('errno'), 0)
