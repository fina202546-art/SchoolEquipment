from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact_view, name='contact'),
    path('rules/', views.rules_view, name='rules'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('delete/<int:pk>/', views.delete_equipment, name='delete_equipment'),
    path('register/security/', views.security_question_view, name='security_question'),
    path('approve/<int:pk>/', views.approve_request, name='approve_request'),
    path('reject/<int:pk>/', views.reject_request, name='reject_request'),
    path('borrow/<int:pk>/', views.borrow_item, name='borrow_item'),
    path('history/', views.borrow_history, name='borrow_history'),
    path('return/<int:pk>/', views.return_item, name='return_item'),
]