from users.forms import CreationForm
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.form = CreationForm()

    def test_signup_form(self):
        """Форма signup создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Александр',
            'last_name': 'Дюма',
            'username': 'Atos',
            'email': 'duma@yandex.ru',
            'password1': 'Atos123456',
            'password2': 'Atos123456'}

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(first_name='Александр',
                                            last_name='Дюма',
                                            username='Atos',
                                            email='duma@yandex.ru'
                                            ).exists())
