from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from PIL import Image
import os


class User(AbstractUser):
    ADMIN = "admin"
    TEACHER = "teacher"
    PARTICIPANT = "participant"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (TEACHER, "Teacher"),
        (PARTICIPANT, "Participant"),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PARTICIPANT)

    def __str__(self):
        return f"{self.username} ({self.role})"


class ChatRoom(models.Model):
    name = models.CharField(max_length=128, unique=True, null=True, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chatrooms")
    users_online = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='online_in_groups', blank=True)
    is_group_chat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or f"ChatRoom #{self.id}"

    def last_message(self):
        return self.messages.order_by('-timestamp').first()

    # def is_direct_message(self):
    #     return not self.is_group_chat and self.participants.count() == 2


def user_directory_path(instance, filename):
    # BESTÄMMER VAR FILEN SKA SPARAS
    return f"files/{instance.sender.username}/{filename}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.CharField(max_length=300 , blank=True)
    file = models.FileField(upload_to= user_directory_path, blank=True, null=True)
    edited = models.BooleanField(default=False)
    delete_message = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
     if self.delete_message:
        return f"{self.sender.username} - (Deleted Message)"
     if self.content:
        return f"{self.sender.username}: {self.content[:30]}..."
     if self.file:
        return f"{self.sender.username}: Uploaded File ({self.filename})"
     return f"{self.sender.username}: (Empty Message)"
         
    
    class Meta:
        ordering = ['timestamp']

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
    

    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False


