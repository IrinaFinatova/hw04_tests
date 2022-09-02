from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Творите', 'group': 'Выберите группу соратников'}
        help_texts = {'text': 'И Лев Толстой здесь был',
                      'group': 'Но можете не выбирать'}
