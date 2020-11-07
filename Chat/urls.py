from django.urls import path
from Chat import views

urlpatterns = [
    path('inbox/', views.InboxListView.as_view({'get': 'list'})),
    path('inbox/<user>', views.UserInboxView.as_view({'get': 'retrieve'})),
    path('messages/<user>', views.InboxMessageView.as_view({'get': 'list'})),
    path('inbox/delete/<username>', views.InboxDeleteView.as_view({"delete": 'destroy'}))
]
