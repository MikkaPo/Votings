from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, PostVariant, Votes, Comments
from .forms import PostForm, VoteVariantForm
from django import forms
from django.http.request import HttpRequest
from .forms import CustomCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import ProfileEditForm, CommentForm
from .models import Comments
from django.db.models import Exists, OuterRef, Count, Sum
import os
import shutil   
from django.conf import settings
from .log import logging


@login_required
def create_post(requests: HttpRequest):
    context: dict = {}
    Voting_factory = forms.formset_factory(VoteVariantForm, extra=0)
    
    if requests.method == 'POST':
        
        post_form = PostForm(requests.POST, prefix='post')
        voting_forms = Voting_factory(requests.POST, prefix='vote_variants')
        
        if post_form.is_valid() and voting_forms.is_valid():
            post = post_form.save(commit=False)
            post.creator = requests.user
            post.save()

            logging.info(f"Post created: id {post.id}; created by {requests.user.username}")  

            for variant_form in voting_forms:
                variant = variant_form.save(commit=False)
                if variant.variant_text:
                    variant.creator = requests.user
                    variant.post = post
                    variant.save()

            logging.info(f"Vote variants created for post {post.id} by {requests.user.username}")  

            return redirect(to='/')

    else:
        post_form = PostForm(prefix='post')
        voting_forms = Voting_factory(prefix='vote_variants')

    context['post_form'] = post_form       
    context['voting_forms'] = voting_forms       

    return render(request=requests, template_name='create/post_creator.html', context=context)


def registration(request: HttpRequest):
    if request.method == 'POST':
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            form.save()
            logging.info(f"New user registered: {request.POST.get('username')}") 
            return redirect(to='/') 
    else:
        form = CustomCreationForm()
    
    context = {'form': form}
    return render(request, 'registr/registr_form.html', context) 


def menu(request: HttpRequest):
    if request.method == 'POST':
        if 'comments' in request.POST:
            return redirect(f'posts/{request.POST.get("comments")}')
        if not request.user.is_authenticated:
            return redirect('accounts/login/')
        if 'delete' in request.POST:
            id = request.POST.get('delete')
            try:
                post = Post.objects.get(id=id, creator=request.user)
                post.delete()
                logging.info(f"Post deleted: id {post.id}; by {request.user.username}")  
            except:
                pass

        vote_variant_id = request.POST.get('variant_id')
        if vote_variant_id and vote_variant_id.isdigit(): 
          try:
            variant = PostVariant.objects.get(id=int(vote_variant_id))
            if not Votes.objects.filter(post_variant=variant, creator=request.user).exists():
                Votes.objects.create(post_variant=variant, creator=request.user)
                logging.info(f"Vote recorded for variant {variant.id} in post {post.id} by {request.user.username}")  
          except PostVariant.DoesNotExist:
              pass 
    
    posts_query = Post.objects.order_by('-creation_dt').annotate(
        voted=Exists(
            Votes.objects.filter(
                post_variant__post=OuterRef('pk'),
                creator=request.user if request.user.is_authenticated else None
            )
        )
    ).select_related('creator').prefetch_related('postvariant_set')

    posts_data = []
    for post in posts_query:
        variants = post.postvariant_set.all().annotate(
            votes_count=Count('votes')
        )
        total_votes = variants.aggregate(total=Sum('votes_count'))['total'] or 0 
        
        variants_data = []
        for variant in variants:
            percentage = (variant.votes_count / total_votes * 100) if total_votes else 0
            variants_data.append({
                'variant': variant,
                'percentage': f"{percentage:.2f}", 
            })
        
        posts_data.append({
            "post": post,
            "user": post.creator,
            "variants": variants_data,
            "voted": post.voted if request.user.is_authenticated else False,
        })

    context = {
        "posts_data": posts_data,
    }

    return render(request, 'menu/menu.html', context)


def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    is_current_user = (request.user.id == user_id)
    context = {
        "user": user,
        "is_current_user": is_current_user
    }
    return render(request, 'profile/profile.html', context)


@login_required
def edit_profile(request: HttpRequest):
    profile, created = UserProfile.objects.get_or_create(user=request.user)  

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)  
        if form.is_valid():
            user_folder = os.path.join(settings.MEDIA_ROOT, f"avatars/user_{request.user.id}") 
            if os.path.exists(user_folder):  
                shutil.rmtree(user_folder)  
            form.save()
            logging.info(f"Profile updated for user {request.user.username}")  
            return redirect('user_profile', user_id=request.user.id) 
    else:
        form = ProfileEditForm(instance=profile)

    context = {"form": form, "user": request.user}
    return render(request, 'profile/edit_profile.html', context)


def delete_avatar(request: HttpRequest):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    user_folder = os.path.join(settings.MEDIA_ROOT, f"avatars/user_{request.user.id}")  
    if os.path.exists(user_folder):  
        shutil.rmtree(user_folder)  

    if request.method == 'POST':
        profile.avatar = os.path.join(settings.MEDIA_ROOT, f"avatars/default.png")  
    profile.save()

    logging.info(f"Avatar deleted for user {request.user.username}")  

    return redirect('user_profile', user_id=request.user.id)


def posts_page(request: HttpRequest, post_id):
    comment_form = CommentForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts/login/')

        if 'delete' in request.POST:
            id = request.POST.get('delete')
            try:
                comment = Comments.objects.get(id=id, creator=request.user)
                comment.delete()
                logging.info(f"Comment deleted: comm id {comment.id} in post {post.id} by {request.user.username}")  
            except:
                pass

        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = Post.objects.get(id=post_id)
                comment.creator = request.user
                comment.save()
                logging.info(f"Comment added for post {post_id} by {request.user.username}")  

        else:
            vote_variant_id = request.POST.get('variant_id')
            if vote_variant_id:
                variant = PostVariant.objects.get(id=int(vote_variant_id))
                if not any(Votes.objects.filter(post_variant=variant, creator=request.user)):
                    Votes.objects.create(post_variant=variant, creator=request.user)
                    logging.info(f"Vote recorded for variant {variant.id} in post {post.id} by {request.user.username}")  

    post = get_object_or_404(Post, id=post_id)
    variants = post.postvariant_set.all().annotate(
        votes_count=Count('votes')
    )
    total_votes = variants.aggregate(total=Sum('votes_count'))['total'] or 0
    variants_data = []
    for variant in variants:
        percentage = (variant.votes_count / total_votes * 100) if total_votes else 0
        variants_data.append({
            'variant': variant,
            'percentage': f"{percentage:.2f}",  # Форматируем до 2 знаков после запятой
        })
    comments = Comments.objects.filter(post=post)
    context = {
        'post': post,
        'variants_data': variants_data,
        'voted': any(Votes.objects.filter(post_variant=variant, creator=request.user) for variant in variants if request.user.is_authenticated),
        'comments': comments, 
        'comment_form': comment_form,
    }

    return render(request, 'post/post_detail.html', context)
