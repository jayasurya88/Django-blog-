from django.contrib import admin
from .models import BlogPost, Comment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_date')
    list_filter = ('post_date', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'post_date')
    list_filter = ('post_date', 'author')
    search_fields = ('description',)
