import os

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from fileman.views import read_dir, get_full_path


USER = 'test'
ADMIN = 'admin'
PASSWORD = '123'
TEST_FILE = 'test.txt'


class FilemanTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username=ADMIN, password=PASSWORD)
        self.admin.is_staff = True
        self.admin.save()
        self.user = User.objects.create_user(
            username=USER, password=PASSWORD)

    # TODO
    # test rename
    # test delete

    def test_upload(self):
        url = reverse('admin:fileman_upload_upload')
        login_url = reverse('admin:login')
        c = Client()

        response = c.post(login_url, {'username': USER, 'password': PASSWORD})
        self.assertEqual(response.status_code, 200)

        with open(get_full_path(TEST_FILE)) as fp:
            response = c.post(url, {'upload': fp})
        # should be redirected to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.find(login_url) != -1, True)

        response = c.post(login_url, {'username': ADMIN, 'password': PASSWORD})

        with open(get_full_path(TEST_FILE)) as fp:
            response = c.post(url, {'upload': fp})
        self.assertEqual(response.status_code, 200)

    def test_file_listing(self):
        results = read_dir('')
        self.assertEqual(results['list'][0]['name'], TEST_FILE)
