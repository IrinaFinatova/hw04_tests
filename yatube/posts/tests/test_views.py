from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from ..models import Group, Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif')
        cls.post = Post.objects.create(author=cls.author,
                                       text='тестовый пост достаточно длинный',
                                       group=cls.group,
                                       image=cls.uploaded)

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def index_post_detail_profile_pages_show_correct_context(self):
        """Шаблон главной страницы, страницы group_list и страницы profile
         сформированы с правильным контекстом."""
        pages_list = [reverse('posts:index'),
                      reverse('posts:group_list',
                              kwargs={'slug': self.post.group.slug}),
                      reverse('posts:profile',
                              kwargs={'username': self.post.author})]
        for page in pages_list:
            first_obj = self.authorized_client.get(page).context['page_obj'][0]
            self.assertEqual(first_obj.author, self.post.author)
            self.assertEqual(first_obj.text, self.post.text)
            self.assertEqual(first_obj.group, self.post.group)
            self.assertEqual(first_obj.image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': self.post.id}))
                    ).context.get('post')
        self.assertEqual(response.group, self.post.group)
        self.assertEqual(response.text, self.post.text)
        self.assertEqual(response.author, self.post.author)
        self.assertEqual(response.image, self.post.image)

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
        Post.objects.bulk_create(Post(author=self.author,
                                      text=f'пост {i}',
                                      group=self.group) for i in range(12))
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
