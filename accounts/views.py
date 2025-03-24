from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegistrationForm
from core.models import Blogger

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated Blogger profile
            Blogger.objects.create(
                user=user,
                bio=form.cleaned_data.get('bio', '')
            )
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to our blog!')
            return redirect('blog-home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
