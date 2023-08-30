from django.urls import path
from .views import PDFDocumentListCreateView,PDFDocumentUploadView,MessageCreateView

urlpatterns = [
    path('pdfs/', PDFDocumentListCreateView.as_view(), name='pdf-list-create'),
    path('pdfs/upload/', PDFDocumentUploadView.as_view(), name='pdf-upload'),
    path('messages/create/', MessageCreateView.as_view(), name='message-create'),
    # Define URLs for Chat, Message, and UserHistory views
]
