from django.db import models
from django.contrib.auth.models import User  # Assuming you use Django's built-in User model

class User(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Chat(models.Model):
    participants = models.ManyToManyField(User)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.pk}"


def custom_default_logic():
    try:
        default_chat = Chat.objects.first()
    except Chat.DoesNotExist:
        default_chat = None  # Handle the case when there are no chats in the database
    return default_chat

# Your Message model
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, default=custom_default_logic)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachments = models.FileField(upload_to='message_attachments/', blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender.username}"

class PdfDocument(models.Model):
    title = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    embedding = models.TextField()

    def __str__(self):
        return self.title
