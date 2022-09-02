from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

PAGES_TEMPLATES_ABOUT = {reverse('about:author'): 'about/author.html',
                         reverse('about:tech'): 'about/tech.html'}


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        """Проверка доступности адреса страниц author/ и tech/."""
        responses = dict.fromkeys(
            [self.guest_client.get(page) for page in
             PAGES_TEMPLATES_ABOUT.keys()],
            HTTPStatus.OK.value)
        for response, expected_value in responses.items():
            with self.subTest(field=response):
                self.assertEqual(response.status_code, expected_value)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адресов author/ и tech/."""
        for reverse_name, template in PAGES_TEMPLATES_ABOUT.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
