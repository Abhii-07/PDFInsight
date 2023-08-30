from django.urls import path
from . import views

urlpatterns = [
    path('process_pdfs/', views.process_pdfs, name='process_pdfs'),
    path('handle_user_input/', views.handle_user_input, name='handle_user_input'),
    # Add more URL patterns for additional views and endpoints as needed
]

