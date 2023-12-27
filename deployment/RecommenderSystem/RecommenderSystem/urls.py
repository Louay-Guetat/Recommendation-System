from django.contrib import admin
from django.urls import path
from mainApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('generate/', views.generate, name='generate_response'),
    path('figures/', views.generate_graphs, name='generate_response'),
]
