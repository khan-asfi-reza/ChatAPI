from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, View, FormView
from rest_framework.authtoken.models import Token

from Accounts.form import UserAdminCreationForm, LoginForm

User = get_user_model()


class CustomMixin(TemplateView, LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        token, created = Token.objects.get_or_create(user=self.request.user)
        context = super().get_context_data(**kwargs)
        context['token'] = token.key
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        return super(CustomMixin, self).dispatch(request, *args, **kwargs)


class HomeView(CustomMixin):
    template_name = 'home.html'
    login_url = 'login'


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = UserAdminCreationForm
    success_url = '/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ChatView(CustomMixin):
    template_name = 'chat.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        token, created = Token.objects.get_or_create(user=self.request.user)
        context = super().get_context_data(**kwargs)
        context['token'] = token.key
        context['username'] = kwargs.get('username')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            user = User.objects.get(username=kwargs.get('username'))
        except User.DoesNotExist:
            return redirect('home')
        return super(CustomMixin, self).dispatch(request, *args, **kwargs)


class ContactView(TemplateView):
    template_name = 'contact.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().exclude(username=self.request.user.username)
        return context
