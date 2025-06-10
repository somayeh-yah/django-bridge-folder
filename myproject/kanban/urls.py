from django.urls import path
from . import views 


urlpatterns = [
    path('', views.kanban_landing, name='kanban_landing'),
    path('board/', views.go_to_existing_board, name='go_to_existing_board'),
    path("board/<int:board_id>", views.kanban_board, name= 'kanban_board'),
    
]

htmx_views = [
 path('create/', views.create_board, name='create_board'),   
 path('board/<int:board_id>/column/add', views.add_column, name='add_column'),
 path('board/<int:board_id>/column/<int:column_id>/edit/', views.edit_column, name='edit_column'),
 path('board/<int:board_id>/column/<int:column_id>/delete/', views.delete_column, name='delete_column'),
 path('close-alert/', views.close_alert, name='close_alert'),
 path('kanban/board/<int:board_id>/invite/', views.invite_members, name='invite_members'),
 path('board/<int:board_id>/new/', views.add_task_form, name='add_task_form'),   
 path('<int:board_id>/edit-name/', views.edit_board_name, name='edit_board_name'),
 path('<int:board_id>/update_name/', views.update_board_name, name='update_name'),
 path("sort/", views.sort, name="sort"),
 path('update-task-status/', views.update_task_status, name='update_task_status'),
 path('board/<int:board_id>/content/', views.board_content_view,name='board_content_view' ),
 path("kanban/board/partial/", views.kanban_board_partial_view, name="kanban_board_partial_view"),
 path('board/<int:board_id>/sprint/', views.sprint_activity, name ='sprint_activity'),
 path("board/<int:board_id>/charts/", views.sprint_chart_image, name="sprint_chart_image"),
 path("board/<int:board_id>/task/<int:task_id>/delete/", views.delete_task, name="delete_task"),
path("board/<int:board_id>/task/<int:task_id>/edit/", views.edit_task_form, name="edit_task_form"),

]


urlpatterns += htmx_views
