from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Board, Task
from .forms import *
from django.contrib import messages

# Create your views here.



@login_required
def kanban_landing(request):
    boards = Board.objects.filter(created_by=request.user)
    return render(request, 'kanban_landing.html', {'boards': boards})

# RETURNERA DEN FÖRSTA BOARDEN DU HITTAR ANNARS NONE
@login_required
def kanban_board(request, board_id):
    board = get_object_or_404(Board, id=board_id, created_by=request.user)
    tasks = board.tasks.all().order_by('-created_at') 
    boards = Board.objects.filter(created_by=request.user)
    return render(request, 'board.html', {
        'board': board,
        'tasks': tasks,
        'boards':boards,
    })



@login_required
def create_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.created_by = request.user  # HÄR KOPPLAR VI TILL INLOGGAD ANVÄNDARE
            board.save()
            return redirect('kanban_board',board_id= board.id)  # TA ANVÄNDAREN TILL KANBAN_BOARD SIDAN
    else:
        form = BoardForm()

    return render(request, 'create_board.html', {'form': form})



@login_required
def add_task(request, board_id):
    board = get_object_or_404(Board, id=board_id, created_by=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            task.board = board
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task added successfully')
            return redirect('kanban_board', board_id=board.id)
        
        
    else:
        form = TaskForm()

    return render(request, 'create_task.html', {'form': form, 'board': board})


@login_required
def go_to_existing_board(request):
     boards = Board.objects.filter(created_by=request.user)
     if boards.exists():
         return redirect('kanban_board', board_id = boards.first().id)
     return redirect('create_board')
     


def reorder_list(user):
    existing_tasks = Task.objects.filter(user=user)
    if not existing_tasks.exists():
        return

    number_of_tasks = existing_tasks.count()
    new_ordering = range(1, number_of_tasks + 1)

    for order, user_tasks in zip(new_ordering, existing_tasks):
        user_tasks.order = order
        user_tasks.save()

@login_required
@require_http_methods(["DELETE"])

def delete_task(request, task_id):

    Task.objects.get(id=task_id).delete()
    reorder_list(request.user)
    messages.info(request, "task removed !") 
    tasks = Task.objects.filter(user=request.user)
    return render(request, "partials/tasks_list.html", {"tasks": tasks})




def sort(request):
    task_ids_order = request.POST.getlist("task-order")

  
    for idx, task_id in enumerate(task_ids_order, start=1):
     user_tasks = Task.objects.get(id=task_id)
     user_tasks.order = idx
     user_tasks.save()
     

    return JsonResponse({"message": "Sorting updated!"})



# @login_required
# def update_task_status(request, task_id):
#     if request.method == "POST":
#         new_status = request.POST.get("status")
        
#         task = Task.objects.get(id=task_id)
#         task.status = new_status
#         task.save()
        
#         return JsonResponse({"success": True})

# def update_task_status(request, task_id):
#     if request.method == "POST":
#         new_status = request.POST.get("status")
        
#         task = Task.objects.get(id=task_id)
#         task.status = new_status
#         task.save()
        
#         return JsonResponse({"success": True})  

@login_required
def edit_board_name(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    new_name = request.POST.get('name')
    if new_name:
        board.name = new_name
        board.save()
        return render(request, 'partials/edit_board_name.html', {'board': board})


@login_required
def update_board_name(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    new_name = request.POST.get('name')

    if new_name:
        board.name = new_name
        board.save()


    return HttpResponse(
        f'<h1 hx-get="/boards/{board.id}/editName/" hx-swap="outerHTML" class="editable-board-title">{board.name}</h1>'
    )    






