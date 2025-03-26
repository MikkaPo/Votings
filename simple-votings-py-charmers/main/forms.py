from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Post, PostVariant, Comments
from django.contrib.auth.models import User
from .models import UserProfile

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_text']

class VoteVariantForm(forms.ModelForm):
    class Meta:
        model = PostVariant
        fields = ['variant_text']
        widgets = {
             'variant_text': forms.TextInput(attrs={'class': 'text-input'}),
        }
        
class CustomCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username',  'password1', 'password2'] 
        
    def __init__(self, * args, ** kwargs):
        super(CustomCreationForm, self).__init__( * args, ** kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = self.fields[fieldname].label

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment_text']
        comment_text = forms.CharField(widget=forms.TextInput)