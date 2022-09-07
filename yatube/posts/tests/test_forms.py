from posts.forms import PostForm
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(title='тестовая группа',
                                         slug='test_slag',
                                         description='Тестовое описание')
        cls.post = Post.objects.create(author=cls.author,
                                       text='тестовый текст',
                                       group=cls.group)
        cls.group_new = Group.objects.create(title='тестовая группа 2',
                                             slug='test_slag_two',
                                             description='Тестовое группы 2')
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'тестовый текст созданный',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='тестовый текст созданный',
                                            group=self.group.id,
                                            image='posts/small.gif').exists())
        last = Post.objects.latest('pub_date')
        self.assertEqual(last.group, self.post.group)
        self.assertEqual(last.text, 'тестовый текст созданный')
        self.assertEqual(last.author, self.post.author)

    def test_edit_post(self):
        """Форма загружает пост с номером id и позволяет его редактировать"""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                                kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post').text, self.post.text)
        form_data = {
            'text': 'тестовый текст новый',
            'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertTrue(Post.objects.filter(text='тестовый текст новый',
                                            group=self.group.id).exists())
        editable = Post.objects.get(id=self.post.id)
        self.assertEqual(editable.group, self.group)
        self.assertEqual(editable.text, 'тестовый текст новый')
        self.assertEqual(editable.author, self.post.author)
        self.assertFalse(Post.objects.filter(group=self.group_new.id).exists())
