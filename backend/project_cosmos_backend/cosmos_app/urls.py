from django.urls import path
from .views import upload_pdf_view, chat_view, semantic_search_view

urlpatterns = [
    path('api/upload-pdf/', upload_pdf_view.as_view(), name='upload_pdf'),
    path('api/chat/', chat_view.as_view(), name='chat'),
    path('api/semantic-search/', semantic_search_view.as_view(), name='semantic_search'),
]
