from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from .form import UserRegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

def test(request):
    return render(request, 'registration/login.html')

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


            return render(request, 'account/register_done.html', {'new_user': new_user})
    elif request.method == 'GET':
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form': user_form})

