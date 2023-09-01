from django.urls import path
# from .views import PDFDocumentListCreateView,PDFDocumentUploadView,MessageCreateView,
from .views import upload_pdf_view,chat_view,semantic_search_view

urlpatterns = [
    # path('pdfs/', PDFDocumentListCreateView.as_view(), name='pdf-list-create'),
    # path('pdfs/upload/', PDFDocumentUploadView.as_view(), name='pdf-upload'),
    # path('messages/create/', MessageCreateView.as_view(), name='message-create'),
    
    # Define URLs for Chat, Message, and UserHistory views
    path('api/upload-pdf/', upload_pdf_view.as_view(), name='upload_pdf'),
    path('api/chat/', chat_view.as_view(), name='chat'),
    path('api/semantic-search/', semantic_search_view.as_view(), name='semantic_search'),
]
