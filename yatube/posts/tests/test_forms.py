from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from ..forms import PostForm
from ..models import Post, Comment, Follow
from .MyTestCase import MyTestCase, TEMP_MEDIA_ROOT

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(MyTestCase):
    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        self.form = PostForm()
        posts_count = Post.objects.count()
        form_data = {
            'text': 'тестовый текст созданный',
            'group': self.group.id,
            'image': self.uploaded,
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
                                            group=self.group.id).exists())
        last = Post.objects.latest('pub_date')
        self.assertEqual(last.group, self.post.group)
        self.assertEqual(last.text, 'тестовый текст созданный')
        self.assertEqual(last.author, self.post.author)
        self.assertIsNotNone(last.image)

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

    def test_add_comment(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'текст комментария'}
        response = self.client_not_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='текст комментария').exists())
        last = Comment.objects.latest('created')
        self.assertEqual(last.text, 'текст комментария')
        self.assertEqual(last.author, self.comment.author)
        self.assertEqual(last.post, self.comment.post)

    def test_create_follower(self):
        """ Создается подписка в Follow """
        follow_count = Follow.objects.count()
        response = self.client_not_author.post(
            reverse('posts:profile_follow', kwargs={'username': self.author}),
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author).exists())
        last = Follow.objects.latest('id')
        self.assertEqual(last.user, self.user)
        self.assertEqual(last.author, self.author)

    def test_delete_follower(self):
        """ Удаляется  подписка из Follow """
        Follow.objects.create(user=self.user, author=self.author)
        follow_count = Follow.objects.count()
        response = self.client_not_author.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author}),
            follow=True)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.author}))
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(Follow.objects.filter(
            user=self.author, author=self.user).exists())
