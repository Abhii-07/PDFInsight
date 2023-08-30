# cosmos_app/serializers.py

from rest_framework import serializers
from .models import User, Chat, Message, PDFDocument, UserHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'join_date')

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class PDFDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = '__all__'

class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = '__all__'
