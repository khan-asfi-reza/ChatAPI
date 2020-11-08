"""ChatAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_view
from ChatAPI import settings, views

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/account/', include('Accounts.urls')),
                  path('api/chat/', include('Chat.urls')),
                  path('signup/',views.SignupView.as_view(), name='signup'),
                  path('login/',auth_view.LoginView.as_view(template_name='login.html'), name='login'),
                  path('logout/', auth_view.LogoutView.as_view(template_name='logout.html'), name='logout'),
                  path('contact/', views.ContactView.as_view(), name='contact'),
                  path('<username>/', views.ChatView.as_view(), name='chat'),
                  path('', views.HomeView.as_view(), name='home'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,
                                                                                         document_root=settings.STATIC_ROOT)

admin.site.site_header = 'ChatAPI Admin'
admin.site.site_title = "ChatAPI"
admin.site.index_title = "ChatAPI"
admin.site.site_url = "chatapi"
