from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.views.generic import DetailView

from .form import UserRegistrationForm, UserEditForm, ProfileEditForm
from django.core.mail import send_mail
from django.urls import reverse_lazy
from .models import Profile, Contact


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')

class CustomLogoutView(LogoutView):
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        view = login_required(view,redirect_field_name=None)
        return view





def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html', {'new_user': new_user})
    elif request.method == 'GET':
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form': user_form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(reverse_lazy('dashboard'))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    next_url = request.POST.get('next', 'articles:article_list')
    if user_id and action and request.user.id != user_id:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
            elif action == 'unfollow':
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return redirect(next_url)
        except User.DoesNotExist:
            return redirect(next_url)
    return redirect(next_url)

class UserDetailView(DetailView):
    model = User
    template_name = 'account/user_detail.html'
    context_object_name = 'user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['followers_count'] = user.followers.count()
        context['following_count'] = user.following.count()
        return context

def followers_list(request, user_pk):
    user = User.objects.get(pk=user_pk)
    followers = user.followers.all()
    return render(request, 'htmx/followers_list.html', {'followers': followers})

def following_list(request, user_pk):
    user = User.objects.get(pk=user_pk)
    following = user.following.all()
    return render(request, 'htmx/following_list.html', {'following': following})