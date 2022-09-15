from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.core.cache import cache

NUMBER_OF_POSTS_PER_PAGE = 10
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class MyTestCase(TestCase):
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
        cls.comment = Comment.objects.create(author=cls.user,
                                             post=cls.post,
                                             text='текстовый комментарий')

        cls.pages_list = [reverse('posts:index'),
                          reverse('posts:group_list',
                                  kwargs={'slug': cls.group.slug}),
                          reverse('posts:profile',
                                  kwargs={'username': cls.author}),
                          reverse('posts:follow_index')]

    def setUp(self):
        self.uploaded.seek(0)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
