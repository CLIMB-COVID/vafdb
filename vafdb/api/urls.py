from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.create),
    # path("update/", views.update),
    path("get/central_sample_id/<central_sample_id>/", views.get_central_sample_id),
    path("get/run_name/<run_name>/", views.get_run_name),
    path("get/published_name/<published_name>/", views.get_published_name),
    path("get/position/<position>/", views.get_position),
    path("delete/<published_name>/", views.delete),
]
