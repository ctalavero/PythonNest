from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.views.generic import DetailView, FormView
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Group
from .form import UserRegistrationForm, UserEditForm, ProfileEditForm, AccessRequestForm
from django.core.mail import send_mail
from django.urls import reverse_lazy
from .models import Profile, Contact


@login_required
def dashboard(request):
    permissions = False
    if request.user.is_superuser:
        permissions = True
    else:
        group_names = request.user.groups.filter(name__in=['Articles Admins', 'Course Admins']).values_list('name', flat=True)
        if len(group_names) == len(Group.objects.values_list('name', flat=True)) :
            permissions = True

    return render(request, 'account/dashboard.html', {'permissions': permissions})

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
        if not hasattr(request.user, 'profile'):
            Profile.objects.create(user=request.user)
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

class AccessRequestView(LoginRequiredMixin, FormView):
    template_name = 'account/request_access.html'
    form_class = AccessRequestForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        if user.date_joined < timezone.now() - timedelta(weeks=3): # user joined more than 3 weeks ago or 2 days ago for testing
            access_types = form.cleaned_data.get('access_types')
            group_names = {
                'article': 'Articles Admins',
                'course': 'Course Admins'
            }
            for access_type in access_types:
                group_name = group_names.get(access_type)
                if group_name:
                    group, created = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)
            user.is_staff = True
            user.save()
            return redirect('access_granted')
        else:
            return redirect('access_denied')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))