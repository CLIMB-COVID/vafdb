from django.urls import path
from . import views


urlpatterns = [
    path("", views.CreateGetView.as_view()),
    path("query/", views.QueryView.as_view()),
    path("<sample_id>/", views.DeleteView.as_view()),
]
