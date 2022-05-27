from django.urls import path
from plantinator_apps.home import views

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('bridge_script_webapp/', views.bridge_script_webapp, name='bridge_script_webapp'),
    path('dashboardadmin/', views.dashboard_admin, name='dashboard_admin'),
    path('post/ajax/SPA', views.post_SPA, name = "post_SPA"),
    path('get/ajax/SPA', views.post_SPA, name = "get_SPA"),
]