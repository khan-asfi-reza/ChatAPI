from django.urls import path

from Accounts import views

crudMethod = {'get': 'retrieve',
              'put': 'update',
              'post': 'create',
              'delete': 'destroy'}
clrMethod = {
    'get': 'list',
    'post': 'create',
    'put': 'update',
}

urlpatterns = [
    path('auth/', views.CreateTokenView.as_view(), name='token-auth'),
    path('auth/check-username/', views.UsernameAvailable.as_view(), name='username-available'),
    path('auth/check-email/', views.EmailAvailable.as_view(), name='phone-available'),
    path('profile/', views.ProfileCreateListUpdateView.as_view(clrMethod), name='profile-list-create'),
    path('profile/<username>/', views.ProfileRetrieveView.as_view({'get': 'retrieve'}), name='profile-rud'),
    path('', views.UserCRUDView.as_view(crudMethod), name='account'),

]
