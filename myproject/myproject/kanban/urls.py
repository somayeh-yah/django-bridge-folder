from django.urls import path
from . import views

urlpatterns = [
    path('', views.kanban_landing, name='kanban_landing'),
    path('board/', views.go_to_existing_board, name='go_to_existing_board'),
    path("board/<int:board_id>", views.kanban_board, name= 'kanban_board'),
    path('create/', views.create_board, name='create_board'),
    path('board/<int:board_id>/add-task/', views.add_task, name='add_task'),
    
    
]

htmx_views = [
#  path('task_status/', views.update_task_status, name= ' update_task_status'),   
 path('<int:board_id>/edit-name/', views.edit_board_name, name='edit_board_name'),
 path('<int:board_id>/update_name/', views.update_board_name, name='update_name'),
  path("sort/", views.sort, name="sort"),
  path("delete/<int:task_id>/", views.delete_task, name="delete_task"),
]


urlpatterns += htmx_views
