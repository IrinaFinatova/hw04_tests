from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class PostURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='hasnoname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_signup_exists_at_desired_location(self):
        """Проверка доступности неавторизованному
         пользователю страницы регистрации /auth/signup
          и выхода из системы logged_out"""
        responses = dict.fromkeys([self.guest_client.get
                                   (reverse('users:login')),
                                   self.guest_client.get
                                   (reverse('users:signup')),
                                   self.authorized_client.get
                                   (reverse('users:logout'))],
                                  HTTPStatus.OK)
        for response, code in responses.items():
            with self.subTest(field=response):
                self.assertEqual(response.status_code, code)

    def test_url_password_change_and_reset_exists_at_desired_location(self):
        """Проверка доступности авторизованному пользователю
         страницы login,
         страницы смены пароля /auth/password_change/,
         страницы восстановления пароль /auth/password_reset/"""
        responses = dict.fromkeys(
            [self.authorized_client.get(reverse('users:login')),
             self.authorized_client.get(reverse('users:password_reset')),
             self.authorized_client.get
             (reverse('users:password_change'))],
            HTTPStatus.OK)
        for response, code in responses.items():
            with self.subTest(field=response):
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:logout'):
                'users/logged_out.html'}
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
