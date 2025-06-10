from django.contrib import admin
from .models import Board,Task, Column
# Register your models here.

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name',)

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'board', 'position')
    list_filter = ('status', 'board')
    search_fields = ('title',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'column', 'assigned_to', 'priority', 'deadline', 'completed')
    list_filter = ('board', 'column', 'priority', 'completed')
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'
