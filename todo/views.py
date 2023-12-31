from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from .models import Post, Hotel, Review, Comment, Reaction
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse


# Renders the homepage
def get_index(request):
    return render(request, 'todo/index.html')

# Renders the contact page
def contact_view(request):
    return render(request, 'todo/contact.html')

# Handles user sign-in     
def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('post_list')  
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'todo/signIn.html')

# Handles user registration
def sign_up_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'todo/signIn.html', {'form': form})

# Lists posts in a paginated view
class PostList(generic.ListView):
    model = Post
    template_name = "todo/posts.html"  
    paginate_by = 4
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get page number for posts
        post_page = self.request.GET.get('post_page', 1)

        # Paginate the posts
        posts = Post.objects.annotate(
            num_thumbs_up=Count('reactions', filter=Q(reactions__is_thumb_up=True)),
            num_thumbs_down=Count('reactions', filter=Q(reactions__is_thumb_up=False))
        ).order_by('-post_date')
        post_paginator = Paginator(posts, self.paginate_by)
        context['post_list'] = post_paginator.get_page(post_page)

        # Get page number for reviews
        review_page = self.request.GET.get('review_page', 1)

        # Paginate the reviews
        reviews = Review.objects.all().order_by("-review_date")
        review_paginator = Paginator(reviews, self.paginate_by)
        context['reviews'] = review_paginator.get_page(review_page)

        context['hotels'] = Hotel.objects.all()
        context['comments'] = Comment.objects.all()
        context['reactions'] = Reaction.objects.all()

        return context

# Handles addition of a new post
@login_required
def add_post(request):
    if request.method == 'POST':
        # Retrieve form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        hotel_id = request.POST.get('hotel')
        image = request.FILES.get('image')

        # Validation (you can add more complex validation as needed)
        if not title or not content or not hotel_id:
            messages.error(request, "Please fill in all required fields.")
            return redirect('post_list')

        # Create a new Post instance
        post = Post(
            title=title,
            content=content,
            user=request.user,
            hotel_id=hotel_id,  # Assuming hotel_id is the primary key of a hotel
            image=image  # Handle image file upload
        )

        # Save the new post
        post.save()
        messages.success(request, 'Your post has been successfully added!')
        return redirect('post_list')

    # Context for GET request
    context = {
        'hotels': Hotel.objects.all()
    }
    return render(request, 'todo/posts.html', context)

# Handles addition of a comment to a post
@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_content = request.POST.get('comment')
        if comment_content:
            Comment.objects.create(user=request.user, post=post, content=comment_content)
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect('post_list')

# Handles addition of a new review
@login_required
def add_review(request):
    if request.method == "POST":
        # Retrieve form data
        hotel_id = request.POST.get('hotel')
        room_type = request.POST.get('room_type')
        duration = request.POST.get('duration')
        spa = request.POST.get('spa') == '1'  # Convert to boolean
        breakfast = request.POST.get('breakfast') == '1'  # Convert to boolean
        content = request.POST.get('content')

        # Validation
        if not hotel_id or not room_type or not duration or not content:
            messages.error(request, "Please fill in all required fields.")
            return redirect('post_list')

        # Create a new Review instance
        review = Review(
            user=request.user,
            hotel_id=hotel_id,
            room_type=room_type,
            duration=duration,
            spa=spa,
            breakfast=breakfast,
            content=content
        )
        # Context for GET request
        context = {
            'hotels': Hotel.objects.all(),
            'post_list': Post.objects.all().order_by("-post_date"),
            'reviews': Review.objects.all().order_by("-review_date"),
        }

        # Save the new review
        review.save()
        messages.success(request, 'Your review has been successfully added!')
        return redirect('post_list')

    # Redirect to the post list page if the method is not POST
    return render(request, 'todo/posts.html', context)

# Handles deletion of a post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:  # Check if the logged-in user is the post creator
        post.delete()
        messages.success(request, 'Post deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this post.')
    return redirect('post_list')

# Handles deletion of a review
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user == request.user:
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('post_list')  # Redirect to the review list page
    else:
        messages.error(request, 'You do not have permission to delete this review.')
        return redirect('post_list')  # Redirect to the review list page

# Handles deletion of a comment
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this comment.')
    return redirect('post_list')  # Redirects to the post list without any arguments

# Handles post reactions (thumbsup/thumbsdown)
class PostReaction(View):
    
    def post(self, request, post_id, reaction_type, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        user_reaction, created = Reaction.objects.get_or_create(post=post, user=request.user)

        # If the reaction is not new
        if not created:
            # If the current reaction is the same as the existing one, remove it
            if (reaction_type == 'up' and user_reaction.is_thumb_up) or (reaction_type == 'down' and not user_reaction.is_thumb_up):
                user_reaction.delete()
            else:
                # Toggle between thumbs up and thumbs down based on the reaction_type
                user_reaction.is_thumb_up = (reaction_type == 'up')
                user_reaction.save()
        else:
            # Set the reaction type on a new reaction
            user_reaction.is_thumb_up = (reaction_type == 'up')
            user_reaction.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('post_list')))
