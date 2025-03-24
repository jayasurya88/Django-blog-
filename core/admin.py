from django.contrib import admin
from .models import BlogPost, Comment, Blogger

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_date', 'get_likes_count', 'get_comments_count')
    list_filter = ('post_date', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'post_date'
    ordering = ('-post_date',)

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Likes'

    def get_comments_count(self, obj):
        return obj.comments.count()
    get_comments_count.short_description = 'Comments'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'post_date', 'get_likes_count')
    list_filter = ('post_date', 'author', 'post')
    search_fields = ('description', 'author__username', 'post__title')
    date_hierarchy = 'post_date'
    ordering = ('-post_date',)

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Likes'

@admin.register(Blogger)
class BloggerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_posts_count', 'get_followers_count', 'get_following_count')
    search_fields = ('user__username', 'bio')
    list_filter = ('user__date_joined',)

    def get_posts_count(self, obj):
        return obj.blogpost_set.count()
    get_posts_count.short_description = 'Posts'

    def get_followers_count(self, obj):
        return obj.followers.count()
    get_followers_count.short_description = 'Followers'

    def get_following_count(self, obj):
        return obj.following.count()
    get_following_count.short_description = 'Following'
