from rest_framework import generics
from .models import PDFDocument, Chat, Message, UserHistory
from .serializers import PDFDocumentSerializer, ChatSerializer, MessageSerializer, UserHistorySerializer
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework import status

class PDFDocumentListCreateView(generics.ListCreateAPIView):
    queryset = PDFDocument.objects.all()
    serializer_class = PDFDocumentSerializer


class PDFDocumentUploadView(generics.CreateAPIView):
    queryset = PDFDocument.objects.all()
    serializer_class = PDFDocumentSerializer
    parser_classes = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        file_serializer = PDFDocumentSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save(uploaded_by=request.user)  # Associate the uploader with the PDF
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        # You may want to customize the behavior here, e.g., associate the sender and chat
        serializer.save(sender=self.request.user)