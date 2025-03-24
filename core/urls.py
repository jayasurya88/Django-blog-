from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    BlogPostListView,
    BlogPostDetailView,
    BlogPostCreateView,
    BlogPostUpdateView,
    BlogPostDeleteView,
    CommentCreateView,
    like_post,
    like_comment,
    AdvancedSearchView,
    home,
    RegisterView,
    BloggerListView,
    BloggerProfileView,
    BloggerProfileEditView,
    follow_blogger,
)

urlpatterns = [
    path('', home, name='blog-home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('blog/', BlogPostListView.as_view(), name='blog-list'),
    path('blog/new/', BlogPostCreateView.as_view(), name='blog-create'),
    path('blog/<slug:slug>/', BlogPostDetailView.as_view(), name='blog-detail'),
    path('blog/<slug:slug>/edit/', BlogPostUpdateView.as_view(), name='blog-update'),
    path('blog/<slug:slug>/delete/', BlogPostDeleteView.as_view(), name='blog-delete'),
    path('blog/<slug:slug>/like/', like_post, name='like-post'),
    path('comment/<int:pk>/like/', like_comment, name='like-comment'),
    path('blog/<slug:slug>/comment/', CommentCreateView.as_view(), name='comment-create'),
    path('search/', AdvancedSearchView.as_view(), name='blog-search'),
    path('bloggers/', BloggerListView.as_view(), name='blogger-list'),
    path('blogger/<int:pk>/', BloggerProfileView.as_view(), name='blogger-profile'),
    path('blogger/edit/', BloggerProfileEditView.as_view(), name='blogger-profile-edit'),
    path('blogger/<int:pk>/follow/', follow_blogger, name='follow-blogger'),
]
