from django.urls import path
from . import views


urlpatterns = [
    path("generate/<code>/", views.GenerateView.as_view()),
    path("filter/<code>/", views.FilterView.as_view()),
    path("query/<code>/", views.QueryView.as_view()),
    path("delete/<code>/<sample_id>/", views.DeleteView.as_view()),
]
