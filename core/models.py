from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from markdown import markdown
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Create a tokenizer that only keeps alphanumeric characters
tokenizer = RegexpTokenizer(r'\w+')

# Create your models here.

class Blogger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, help_text="Enter your biographical information (Markdown supported)")
    profile_picture = models.ImageField(upload_to='blogger_pics/', null=True, blank=True)
    
    # Social media links
    twitter = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    instagram = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    
    # Following system
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    
    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('blogger-profile', args=[str(self.user.id)])
    
    def get_bio_as_markdown(self):
        return markdown(self.bio)
    
    def get_total_posts(self):
        return self.blogpost_set.count()
    
    def get_total_comments(self):
        return Comment.objects.filter(author=self.user).count()
    
    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.following.count()
    
    def is_following(self, blogger):
        return self.following.filter(id=blogger.id).exists()

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Blogger, on_delete=models.CASCADE)
    post_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    class Meta:
        ordering = ['-post_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Get the URL for this blog post, generating a slug if necessary"""
        if not self.slug:
            # Generate a slug if it doesn't exist
            self.slug = self.generate_slug()
            self.save(update_fields=['slug'])
        return reverse('blog-detail', kwargs={'slug': self.slug})
    
    def get_likes_count(self):
        return self.likes.count()
    
    def generate_tags(self):
        """Generate tags from title and content"""
        # Combine title and content
        text = f"{self.title} {self.content}".lower()
        
        # Tokenize and remove stopwords
        tokens = tokenizer.tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Get most common words as tags
        from collections import Counter
        common_words = Counter(tokens).most_common(5)
        tags = [word for word, count in common_words]
        
        return ','.join(tags)
    
    def generate_slug(self):
        """Generate a unique slug from the title"""
        from django.utils.text import slugify
        from django.db.models import Q
        
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        
        # Keep trying until we find a unique slug
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = self.generate_slug()
        
        # Generate tags if not provided
        if not self.tags:
            self.tags = self.generate_tags()
            
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=1000)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    
    class Meta:
        ordering = ['post_date']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    def get_likes_count(self):
        return self.likes.count()
