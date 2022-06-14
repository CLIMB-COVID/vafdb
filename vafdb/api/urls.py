from django.urls import path
from . import views

urlpatterns = [
    path('get/', views.get_metadata),
    path('add/', views.add_metadata)
]