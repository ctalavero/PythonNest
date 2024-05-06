from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
# Create your views here.
def test(request):
    return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')

class CustomLogoutView(LogoutView):
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view)
