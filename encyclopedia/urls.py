from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.enter_page, name="wiki"),
    path("search", views.search, name="search"),
    path("create", views.create_page, name="create"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random", views.random, name="random")
]
