from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment, BlogPost, Blogger

class UserRegistrationForm(UserCreationForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Tell us about yourself (optional)"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'bio')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create associated Blogger profile
            Blogger.objects.create(
                user=user,
                bio=self.cleaned_data.get('bio', '')
            )
        return user

class BloggerProfileForm(forms.ModelForm):
    class Meta:
        model = Blogger
        fields = ['bio', 'profile_picture', 'twitter', 'facebook', 'instagram', 'linkedin', 'github', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write something about yourself (Markdown supported)'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/yourusername'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/yourusername'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/yourusername'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourusername'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        } 