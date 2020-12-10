from django.contrib import admin
from django import forms
from .models import Post, Category, Category2


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Category2)

class PostForm(forms.Form):
    category_data = Category.objects.all()
    category_choice = {}
    for category in category_data:
        category_choice[category] = category

    title = forms.CharField(max_length=50, label='タイトル')
    category = forms.ChoiceField(label='カテゴリ', widget=forms.Select, choices=list(category_choice.items())) # 追加
    content = forms.CharField(label='内容', widget=forms.Textarea())
    image = forms.ImageField(label='イメージ画像', required=False)
#
# Register your models here.
