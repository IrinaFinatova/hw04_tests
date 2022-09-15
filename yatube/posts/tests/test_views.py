from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django import forms
from ..models import Post, Follow
from .MyTestCase import MyTestCase, NUMBER_OF_POSTS_PER_PAGE, TEMP_MEDIA_ROOT
from django.core.cache import cache

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(MyTestCase):
    def index_group_profile_follow_pages_show_correct_context(self):
        """Шаблон главной страницы, страницы group_list,
         страницы profile, страницы follow
         сформированы с правильным контекстом."""
        for page in self.pages_list:
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
        """ Пост принадлежит правильной группе."""
        self.assertTrue(Post.objects.filter(group=self.group.id).exists())
        self.assertFalse(Post.objects.filter(group=self.group_new.id).exists())

    def test_cache(self):
        cache_post = Post.objects.create(
            author=self.author, text='пост для кеша')
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(cache_post in response.context['page_obj'])
        cache_post.delete()
        self.assertIn(cache_post.text, response.content.decode())
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(cache_post.text, response.content.decode())

    def test_pagintor_index_group_list_profile_follow(self):
        """Тестируем пагинатор на страницах index,
         group_list, profile и follow."""
        Post.objects.bulk_create(Post(author=self.author,
                                      text=f'пост {i}',
                                      group=self.group,
                                      image=self.post.image)
                                 for i in range(12))
        self.follow = Follow.objects.create(user=self.user, author=self.author)
        for page in self.pages_list:
            with self.subTest(page=page):
                response_first = self.client_not_author.get(page)
                self.assertEqual(len(response_first.context['page_obj']),
                                 NUMBER_OF_POSTS_PER_PAGE)
                response_second = self.client_not_author.get(page + '?page=2')
                self.assertEqual(len(response_second.context['page_obj']), 3)
