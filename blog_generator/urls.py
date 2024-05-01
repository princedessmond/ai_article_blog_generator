from django.urls import path # type: ignore

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='login'),
    path('signup', views.user_signup, name='signup'),
    path('logout', views.user_logout, name='logout'),
    path('generate-blog', views.generate_blog, name='generate-blog'),
    path('blog_list', views.blog_list, name='blog_list'),
    path('blog_details/<int:pk>/', views.blog_details, name='blog_details'),
]