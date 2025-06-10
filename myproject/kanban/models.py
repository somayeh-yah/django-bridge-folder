from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Board(models.Model):
    name = models.CharField(max_length=255, help_text= "Enter your project name...")
    members = models.ManyToManyField(User, related_name="board_members")
    description = models.TextField(blank=True, help_text= "Write a descripton...")
    color = models.CharField(max_length=7, default="#ffffff")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  

    def __str__(self):
        return self.name
    


class Column(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)  # FÖR SORTERING

    def __str__(self):
        return f"{self.title} ({self.status})"
    

class Task(models.Model):

    STATUS_colors = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('review', 'Review'),
        ('complete', 'Complete'),
    ]

    PRIORITY_CHOICES = [
        ('', '----------'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
      
    ]
    # HÄR KOPPLAR VI VARJE UPPGIFT TILL ETT BOARD
    board = models.ForeignKey(Board, on_delete= models.CASCADE, related_name="tasks", default=1)
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    completed = models.BooleanField(default=False)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, blank=True, related_name="column_tasks")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES,default='medium')

    def __str__(self):
        return self.title

