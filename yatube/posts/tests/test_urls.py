from django.contrib.auth import get_user_model
from django.test import override_settings
from http import HTTPStatus
from django.urls import reverse
from .MyTestCase import MyTestCase, TEMP_MEDIA_ROOT


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTest(MyTestCase):
    def test_common_url_exists_at_desired_location(self):
        """Проверка общедоступных адресов страниц страниц /, /group/<slug>/,
        /profile/<username>/, /post/<post_id>/."""
        pages_list_common = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})]
        responses = dict.fromkeys(
            [self.guest_client.get(page) for page in pages_list_common],
            HTTPStatus.OK)
        for response, code in responses.items():
            with self.subTest(field=response):
                self.assertEqual(response.status_code, code)

    def test_authorized_url_create_exists_at_desired_location(self):
        """Проверка доступности адреса страницы
        /create/ авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_author_url_edit_exists_at_desired_location(self):
        """Проверка доступности адреса страницы
         /posts/<post_id>/edit/ автору поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_url_follow_exists_at_desired_location(self):
        """Проверка доступности адреса страницы
        /follow/ авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_authorized_url_comment_redirect(self):
        """Проверка переадресации /posts/<post_id>/comment/
        при оставлении комментария на  posts/post_id/
        авторизованному пользователю."""
        response_comment_on_post_id = self.client_not_author.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response_comment_on_post_id,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))

    def test_for_un_existing_page(self):
        """Проверка недоступности и шаблона несуществующей страницы"""
        response = self.guest_client.get('/un_existing_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_url_redirect_create_and_edit(self):
        """Проверка переадресации неавтора поста
         со страницы редактирования поста
         /post/post_id/edit/ на posts/post_id/"""
        response_edit_on_post_id = self.client_not_author.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}), follow=True)
        self.assertRedirects(response_edit_on_post_id,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        PAGES_TEMPLATES_POSTS = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.post.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.post.author}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'}
        for reverse_name, template in PAGES_TEMPLATES_POSTS.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
