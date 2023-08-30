from django.db import models
from django.contrib.auth.models import User  # If you want to associate PDFs with users

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)  # If you want to associate PDFs with users
    upload_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.title

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    timestamp = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    attachments = models.ManyToManyField(PDFDocument, blank=True)

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
