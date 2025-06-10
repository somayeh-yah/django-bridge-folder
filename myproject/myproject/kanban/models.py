from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Board(models.Model):
    name = models.CharField(max_length=255, help_text= "Enter your project name...")
    description = models.TextField(blank=True, help_text= "Write a descripton...")
    color = models.CharField(max_length=7, default="#ffffff")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  

    def __str__(self):
        return self.name
    

class Task(models.Model):

    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('review', 'Review'),
        ('complete', 'Complete'),
    ]
    # HÄR KOPPLAR VI VARJE UPPGIFT TILL ETT BOARD
    board = models.ForeignKey(Board, on_delete= models.CASCADE, related_name="tasks", default=1)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices= STATUS_CHOICES, default='backlog')

    def __str__(self):
        return self.title

