from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from .form import UserRegistrationForm
from django.core.mail import send_mail
from django.urls import reverse_lazy

def test(request):
    send_mail(
        'Subject here',
        'test message.',
        'ctalavero12@gmail.com',
        ['ctalavero12@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse('test')

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

