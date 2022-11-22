from django.urls import path
from . import views


urlpatterns = [
    path("", views.CreateGetVAFView.as_view()),
    path("query/", views.QueryVAFView.as_view()),
]
