# from django import forms
# from django.utils import timezone
# from django.contrib.auth import get_user_model
# from .models import Post, Comment

# User = get_user_model()


# class PostForm(forms.ModelForm):
#     class Meta:
#         # Указываем модель, на основе которой должна строиться форма.
#         model = Post
#         # Указываем, что надо отобразить все поля.
#         fields = ['title', 'text', 'pub_date', 'location', 'category',
#                   'is_published', 'image']
#         widgets = {
#             'pub_date': forms.DateTimeInput(attrs={
#                 'type': 'datetime-local',  # HTML5 input type
#                 'class': 'form-control'   # Дополнительные классы, если нужно
#             })
#         }

#     def clean_pub_date(self):
#         pub_date = self.cleaned_data['pub_date']
#         if pub_date:
#             # Ensure pub_date is timezone-aware
#             if not timezone.is_aware(pub_date):
#                 # Assume input is in the project's TIME_ZONE and make it aware
#                 pub_date = timezone.make_aware(
#                     pub_date, timezone=timezone.get_default_timezone())
#             return pub_date
#         return pub_date


# class CommentForm(forms.ModelForm):
#     class Meta:
#         # Указываем модель, на основе которой должна строиться форма.
#         model = Comment
#         # Указываем, что надо отобразить все поля.
#         fields = ['text']
from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category',
                  'is_published', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date and not timezone.is_aware(pub_date):
            pub_date = timezone.make_aware(
                pub_date, timezone.get_default_timezone())
        return pub_date


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
