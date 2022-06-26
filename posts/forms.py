from django import forms
from django.forms import ModelForm, Textarea
from posts.models import Post, Comment
from posts.models import Group


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        help_texts = {
            'group': 'Если укажешь группу, мы будем благодарны',
            'text': 'Напишите пост',
            'image': 'якартинко'
            }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': Textarea(attrs={'cols': 80, 'rows': 5})}
