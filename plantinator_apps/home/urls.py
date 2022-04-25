from django.urls import path
from plantinator_apps.home import views

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('post/ajax/SPA', views.post_SPA, name = "post_SPA"),
    path('get/ajax/SPA', views.post_SPA, name = "get_SPA"),
]