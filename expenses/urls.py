
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),

    path('add/', views.add_expense, name='add_expense'),
    path('update/<int:pk>/', views.update_expense, name='update_expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('export/', views.export_csv, name='export_csv'),

]



