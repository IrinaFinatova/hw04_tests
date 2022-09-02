from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Group, Post

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='hasnoname')
        cls.client_not_author = Client()
        cls.client_not_author.force_login(cls.user)
        cls.author = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(title='тестовая группа',
                                         slug='test_slag',
                                         description='Тестовое описание')
        cls.group_new = Group.objects.create(title='тестовая группа 2',
                                             slug='test_slag_two',
                                             description='Тестовое группы 2')
        cls.post = Post.objects.create(author=cls.author,
                                       text='тестовый пост достаточно длинный',
                                       group=cls.group)

    def index_post_detail_profile_pages_show_correct_context(self):
        """Шаблон главной страницы, страницы group_list и страницы profile
         сформированы с правильным контекстом."""
        pages_list = [reverse('posts:index'),
                      reverse('posts:group_list',
                              kwargs={'slug': self.post.group.slug}),
                      reverse('posts:profile',
                              kwargs={'username': self.post.author})]
        for page in pages_list:
            response = self.authorized_client.get(page)
            first_object = response.context['page_obj'][0]
            post_text_0 = first_object.text
            post_group_0 = first_object.group
            post_author_0 = first_object.author
            self.assertEqual(post_text_0, self.post.author)
            self.assertEqual(post_author_0, self.post.text)
            self.assertEqual(post_group_0, self.post.group)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_post_accessory_group(self):
        self.assertTrue(Post.objects.filter(group=self.group.id).exists())
        self.assertFalse(Post.objects.filter(group=self.group_new.id).exists())

    def test_pagintor_index_group_list_profile(self):
        """Тестируем пагинатор на страницах index, group_list и profile"""
        for i in range(12):
            Post.objects.create(author=self.author,
                                text=f'пост {i}',
                                group=self.group)
        pages_list = [reverse('posts:index'),
                      reverse('posts:group_list',
                              kwargs={'slug': self.group.slug}),
                      reverse('posts:profile',
                              kwargs={'username': self.author.username})]
        for page in pages_list:
            response = self.authorized_client.get(page)
            self.assertEqual(len(response.context['page_obj']), 10)
        for page in pages_list:
            response = self.authorized_client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
