from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.contrib.auth import login
from django.http import JsonResponse
from .models import BlogPost, Blogger, Comment
from .forms import CommentForm, BlogPostForm, UserRegistrationForm, BloggerProfileForm
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from datetime import datetime, timedelta
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Create your views here.
def home(request):
    """Home page view"""
    return render(request, 'core/home.html')

class RegisterView(FormView):
    """View for user registration"""
    form_class = UserRegistrationForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('blog-list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful! Welcome to the blog.')
        return super().form_valid(form)

class BloggerProfileView(DetailView):
    """View for displaying blogger profile"""
    model = User
    template_name = 'core/blogger_profile.html'
    context_object_name = 'blogger'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        blogger = user.blogger
        
        # Get user statistics
        context['total_posts'] = blogger.get_total_posts()
        context['total_comments'] = blogger.get_total_comments()
        context['followers_count'] = blogger.get_followers_count()
        context['following_count'] = blogger.get_following_count()
        
        # Check if current user is following this blogger
        if self.request.user.is_authenticated:
            try:
                context['is_following'] = self.request.user.blogger.is_following(blogger)
            except Blogger.DoesNotExist:
                context['is_following'] = False
        else:
            context['is_following'] = False
            
        return context

class BloggerProfileEditView(LoginRequiredMixin, UpdateView):
    """View for editing blogger profile"""
    model = Blogger
    form_class = BloggerProfileForm
    template_name = 'core/blogger_profile_edit.html'
    success_url = reverse_lazy('blogger-profile')

    def get_object(self):
        # Get or create the blogger profile
        blogger, created = Blogger.objects.get_or_create(user=self.request.user)
        return blogger

    def get_success_url(self):
        return reverse_lazy('blogger-profile', kwargs={'pk': self.request.user.id})

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

@login_required
def follow_blogger(request, pk):
    """Handle following/unfollowing a blogger"""
    blogger_to_follow = get_object_or_404(Blogger, user__id=pk)
    current_blogger, created = Blogger.objects.get_or_create(user=request.user)
    
    if current_blogger.following.filter(id=blogger_to_follow.id).exists():
        current_blogger.following.remove(blogger_to_follow)
        is_following = False
    else:
        current_blogger.following.add(blogger_to_follow)
        is_following = True
    
    return JsonResponse({
        'is_following': is_following,
        'followers_count': blogger_to_follow.followers.count()
    })

@login_required
def like_post(request, slug):
    """Handle liking/unliking a blog post"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    
    return JsonResponse({
        'likes_count': post.likes.count(),
        'is_liked': is_liked
    })

@login_required
def like_comment(request, pk):
    """Handle liking/unliking a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        is_liked = False
    else:
        comment.likes.add(request.user)
        is_liked = True
    
    return JsonResponse({
        'likes_count': comment.likes.count(),
        'is_liked': is_liked
    })

class BlogPostListView(ListView):
    """List view for all blog posts"""
    model = BlogPost
    template_name = 'core/blogpost_list.html'
    context_object_name = 'blogpost_list'
    paginate_by = 5

class BloggerListView(ListView):
    """View for displaying list of bloggers"""
    model = Blogger
    template_name = 'core/blogger_list.html'
    context_object_name = 'bloggers'
    paginate_by = 12
    
    def get_queryset(self):
        return Blogger.objects.annotate(
            post_count=Count('blogpost'),
            follower_count=Count('followers')
        ).order_by('-post_count')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_bloggers'] = Blogger.objects.count()
        context['total_posts'] = BlogPost.objects.count()
        return context

class BloggerDetailView(DetailView):
    """Detail view for a specific blogger"""
    model = Blogger
    template_name = 'core/blogger_detail.html'
    context_object_name = 'blogger'

class BlogPostDetailView(DetailView):
    """Detail view for a specific blog post"""
    model = BlogPost
    template_name = 'core/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except BlogPost.DoesNotExist:
            messages.error(self.request, 'The blog post you are looking for does not exist.')
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return redirect('blog-list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        post = self.get_object()
        
        # Get similar posts based on content similarity
        similar_posts = BlogPost.objects.exclude(id=post.id).filter(
            Q(title__icontains=post.title.split()[0]) |  # Match first word of title
            Q(content__icontains=post.title.split()[0])  # Match first word in content
        ).distinct()[:3]
        
        # Get popular posts based on likes
        popular_posts = BlogPost.objects.exclude(id=post.id).annotate(
            like_count=Count('likes')
        ).order_by('-like_count')[:3]
        
        context['similar_posts'] = similar_posts
        context['popular_posts'] = popular_posts
        return context

class BlogPostCreateView(LoginRequiredMixin, CreateView):
    """View for creating new blog posts"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'core/blogpost_form.html'
    success_url = reverse_lazy('blog-list')

    def form_valid(self, form):
        # Create Blogger profile if it doesn't exist
        blogger, created = Blogger.objects.get_or_create(
            user=self.request.user,
            defaults={'bio': ''}
        )
        form.instance.author = blogger
        messages.success(self.request, 'Blog post created successfully!')
        return super().form_valid(form)

class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating blog posts"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'core/blogpost_form.html'
    
    def get_success_url(self):
        return reverse('blog-detail', kwargs={'slug': self.object.slug})
    
    def get_queryset(self):
        # Only allow users to edit their own posts
        return super().get_queryset().filter(author=self.request.user.blogger)
    
    def form_valid(self, form):
        messages.success(self.request, 'Blog post updated successfully!')
        return super().form_valid(form)

class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting blog posts"""
    model = BlogPost
    success_url = reverse_lazy('blog-list')
    template_name = 'core/blogpost_confirm_delete.html'
    
    def get_queryset(self):
        # Only allow users to delete their own posts
        return super().get_queryset().filter(author=self.request.user.blogger)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Blog post deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CommentCreateView(LoginRequiredMixin, CreateView):
    """View for creating new comments"""
    model = Comment
    form_class = CommentForm
    template_name = 'core/comment_form.html'

    def get_success_url(self):
        return reverse_lazy('blog-detail', kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(BlogPost, slug=self.kwargs['slug'])
        response = super().form_valid(form)
        
        print("Request headers:", self.request.headers)
        print("Request method:", self.request.method)
        print("Is AJAX:", self.request.headers.get('X-Requested-With') == 'XMLHttpRequest')
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get profile picture URL safely
            profile_picture_url = None
            try:
                if hasattr(self.object.author, 'blogger') and self.object.author.blogger.profile_picture:
                    profile_picture_url = self.object.author.blogger.profile_picture.url
            except Exception as e:
                print("Error getting profile picture:", e)
                pass

            data = {
                'id': self.object.id,
                'description': self.object.description,
                'author': {
                    'id': self.object.author.id,
                    'username': self.object.author.username,
                    'profile_picture': profile_picture_url
                },
                'post_date': self.object.post_date.strftime('%B %d, %Y'),
                'success': True
            }
            print("Returning JSON response:", data)
            return JsonResponse(data)
        
        messages.success(self.request, 'Comment added successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogpost'] = get_object_or_404(BlogPost, slug=self.kwargs['slug'])
        return context

class AdvancedSearchView(ListView):
    """Advanced search view with full-text search capabilities"""
    model = BlogPost
    template_name = 'core/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return BlogPost.objects.none()

        # Download required NLTK data
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        # Simple tokenization by splitting on whitespace
        tokens = query.lower().split()
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Create search vectors for title and content
        title_vector = SearchVector('title', weight='A')
        content_vector = SearchVector('content', weight='B')
        search_vector = title_vector + content_vector
        
        # Create search query from tokens
        search_query = SearchQuery(' '.join(tokens))
        
        # Perform the search with ranking
        queryset = BlogPost.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.1).order_by('-rank')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

