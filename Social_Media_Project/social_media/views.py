from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post,Comment
from .forms import PostForm
from django.db.models import Q

def home(request):
    print(request.META)
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})

@login_required
def profile_view(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')  # Redirect to homepage after posting
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if request.method == "POST":
        post.delete()
        return redirect('profile')

    return render(request, 'delete_post.html', {'post': post})
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # Unlike if already liked
    else:
        post.likes.add(request.user)  # Like if not liked
    return redirect('home')

@login_required
def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('comment')
        if text:
            Comment.objects.create(user=request.user, post=post, text=text)
    return redirect('home')

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == "POST":
        new_text = request.POST.get("comment_text")
        if new_text:
            comment.text = new_text
            comment.save()
        return redirect('home')
    
    return redirect('home')
@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()  # Get search query
    user_results = []  # List for users and their posts

    if query:
        # Find users matching the query
        users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))

        if users.exists():
            for user in users:
                # Fetch user's profile picture (handle missing profile)
                user_profile = getattr(user, "userprofile", None)
                profile_picture = user_profile.profile_picture.url if user_profile and user_profile.profile_picture else "/media/profile_images/default.jpg"

                # Fetch user posts
                posts = Post.objects.filter(user=user).order_by('-created_at')
                post_list = []
                for post in posts:
                    post_list.append({
                        "text": post.text,
                        "image": post.image.url if post.image else None,
                        "created_at": post.created_at,
                    })

                user_results.append({
                    "user": user,
                    "profile_picture": profile_picture,
                    "posts": post_list,
                })

        else:
            return render(request, "search_results.html", {"error": "No matching users found"})

    return render(request, "search_results.html", {"query": query, "user_results": user_results})