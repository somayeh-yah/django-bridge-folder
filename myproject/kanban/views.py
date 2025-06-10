from django.shortcuts import render, get_object_or_404,redirect
from django.http import Http404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.db.models import F , Max
from .models import Board, Task
from .forms import *
import json
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.timezone import now
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.dates import date2num
from matplotlib.patches import FancyBboxPatch
from io import BytesIO
import seaborn as sns
from django.db.models import Prefetch



@login_required
def kanban_landing(request):
    boards = Board.objects.filter(created_by=request.user)
    return render(request, 'kanban_landing.html', {'boards': boards})

# RETURNERA DEN FÖRSTA BOARDEN DU HITTAR ANNARS NONE
@login_required
def kanban_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.user != board.created_by and request.user not in board.members.all():
     raise Http404("Oops! It looks like the page you're trying to access doesn't exist.")
    
    created_boards = Board.objects.filter(created_by=request.user)
    columns = board.columns.prefetch_related("column_tasks").order_by("position")
    member_boards = Board.objects.filter(members=request.user)
    boards = (created_boards | member_boards).distinct()
    
  

    context = {
      'board': board,
      'boards':boards,
      'columns': columns,
      'hide_inner_sidebar':True,
      'show_inner_sidebar_icon':True,
     

    }

    return render(request, 'board.html', context)

@login_required
def add_column(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    get_column_id = request.GET.get("column_id")
    ref_column = None
    set_position = None

    if get_column_id:
        ref_column = get_object_or_404(Column, id=get_column_id, board=board)
        set_position = ref_column.position

    if request.method == 'POST':
        form = AddColumnForm(request.POST)
        if form.is_valid():
            column = form.save(commit=False)
            column.board = board
            column.status = slugify(column.title)

            if set_position is not None:
                Column.objects.filter(board=board, position__gte=set_position).update(position=F('position') + 1)
                column.position = set_position
            else:
                max_pos = board.columns.aggregate(max_pos=Max('position'))['max_pos'] or 0
                column.position = max_pos + 1

            column.save()

           
            return redirect('kanban_board', board_id=board.id)

    else:
        form = AddColumnForm()

    return render(request, 'partials/add_column_form.html', {
        'form': form,
        'board': board
    })


@login_required
def edit_column(request, board_id, column_id):
    board = get_object_or_404(Board, id=board_id)
    column = get_object_or_404(Column, id=column_id, board=board_id)

    if request.user != board.created_by and request.user not in board.members.all():
        raise Http404("Oops! It looks like the page you're trying to access doesn't exist.")

    if request.method == "POST":
        form = AddColumnForm(request.POST, instance=column)
        if form.is_valid():
            form.save()
            return redirect('kanban_board', board_id=board.id)
    else:
        form = AddColumnForm(instance=column)

    return render(request, "partials/edit_column_form.html", {"form": form, "board": board, "column": column})

@login_required
def delete_column(request, board_id, column_id):
    column = get_object_or_404(Column, id=column_id, board_id=board_id)

    if request.method == 'POST':
        if request.user != column.board.created_by and request.user not in column.board.members.all():
            raise Http404("Oops! It looks like the page you're trying to access doesn't exist.")
        
        column.delete()

        board = get_object_or_404(Board, id=board_id)
        columns = board.columns.prefetch_related("column_tasks").order_by("position")
        board_content = render_to_string("partials/board_content.html", {
            "columns": columns,
            "board": board,
           
        }, request=request)

        return HttpResponse(board_content)

    return HttpResponse(status=405)

@login_required
def board_content_view(request, board_id):
 board = get_object_or_404(Board, id=board_id)
 if request.user != board.created_by and not board.members.filter(id=request.user.id).exists():
    raise Http404("Oops! It looks like the page you're trying to access doesn't exist.")
   
 columns = board.columns.prefetch_related(Prefetch("column_tasks",queryset=Task.objects.order_by('order'))).order_by("position")
 context = {
        "board": board,
        "columns": columns,
        "hide_inner_sidebar": True,
        "show_inner_sidebar_icon": True,
    }
 return render(request, 'partials/board_content.html', context)

def close_alert(request):
    list(request._messages)
    return HttpResponse("")

@login_required
def create_board(request):
    form = BoardForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        board = form.save(commit=False)
        board.created_by = request.user  # HÄR KOPPLAR VI TILL INLOGGAD ANVÄNDARE
        board.save()
        #OM SKAPAREN AV BOARD INTE FINNS MED I BOARD, LÄGG TILL DE 
        if not board.created_by in board.members.all():
            messages.success(request, "Your Board has been successfully created.")
            board.members.add(request.user)
        
        # HÄR SKAPAR VI DEFAULT KOLUMNER
        default_columns =["Backlog","To do", "Done"]  
        for index, title in enumerate(default_columns):
            Column.objects.create(
                board=board,
                title=title,
                status=slugify(title),
                position=index
            )

        messages.success(request, "Your board has been successfully created")
        return redirect("kanban_board", board_id= board.id)  
    else:
        messages.error(request, "Something went wrong") 

    return render(request, 'partials/create_board.html', {'form': form})


@login_required
def kanban_board_partial_view(request):
    board_id = request.POST.get("board_id")
    board = get_object_or_404(Board, id=board_id)

    if request.user != board.created_by and not board.members.filter(id=request.user.id).exists():
        return 404("this page does not exist. ")

    columns = board.columns.prefetch_related("column_tasks").order_by("position")
    return render(request, "partials/board_content.html", {
        "board": board,
        "columns": columns
    })

@login_required
def invite_members(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    form = InviteMemberForm(request.POST or None, board=board)
   
    if request.method == 'POST' and form.is_valid():
        user_to_add = form.cleaned_data['user']
        board.members.add(user_to_add)
        messages.success(request, f"{user_to_add.username} has been invited.")
        return redirect('kanban_board', board_id=board.id)
    
    return render(request, 'partials/invite_members_form.html', {'form': form, 'board': board})

from django.shortcuts import redirect

@login_required
def add_task_form(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if request.user != board.created_by and request.user not in board.members.all():
        messages.error(request, "You do not have permission to add information to this board.")
        return redirect('kanban_landing')

    form = TaskForm(request.POST or None, user=request.user, board=board)

    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.board = board
        task.created_by = request.user

        backlog_column = board.columns.filter(status__iexact="backlog").first()
        if not backlog_column:
            messages.error(request, "There is no 'Backlog' column on this board.")
            return redirect("kanban_board", board_id=board.id)

        task.column = backlog_column
        task.save()

        messages.success(request, f"Task '{task.title}' was successfully created!")

        
        return redirect("kanban_board", board_id=board.id)

  
    return render(request, "partials/add_task_form.html", {"form": form, "board": board})


    
@login_required
def go_to_existing_board(request):
     boards = Board.objects.filter(created_by=request.user)
     if boards.exists():
        latest_active_board= boards.first()
        return redirect('kanban_board', board_id = latest_active_board.id)
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

@require_POST
def update_task_status(request):
    task_id = request.POST.get("task_id")
    new_column_status = request.POST.get("new_column_status")

    if task_id and new_column_status:
        task = Task.objects.get(id=task_id)
        column = Column.objects.get(id=new_column_status)
        task.column = column
        task.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)



@login_required
def delete_task(request, board_id ,task_id):
    task = get_object_or_404(Task, id=task_id, board_id=board_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, f"Task '{task.title}' was successfully deleted!")
        # HÄMTA UPPGIFTER EFTER RADERING
        column = task.column
        tasks = column.column_tasks.order_by("position")
       

        return render(request, "partials/column_tasks.html", {
            "column": column,
            "tasks": tasks
        })

    return HttpResponse(status=405)


@login_required
def edit_task_form(request, board_id, task_id):
    task = get_object_or_404(Task, id =task_id, board_id=board_id)
    board = task.board

    if request.user != board.created_by and not board.members.filter(id=request.user.id).exists():
        raise ("Oops!It looks like the page you're trying to access doesn't exist.")

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('kanban_board', board_id=board.id)
    else:
        form = TaskForm(instance=task)

    return render(request, "partials/edit_task_page.html", {
        "form": form,
        "board": board,
        "task": task,
    })

@require_POST
def sort(request):
    task_id = request.POST.get("task_id")
    new_column_status = request.POST.get("new_column_status")

    if not task_id or not new_column_status:
        return JsonResponse({"error": "Missing data"}, status=400)

    try:
        task = get_object_or_404(Task, id=task_id)
        task.column_id = new_column_status
        task.save()

        return JsonResponse({"message": "Task updated"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





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



# ------- CHARTs  -----------#

STATUS_COLORS = {
        'todo': "#61d761",
        'inprogress': "#a445d1",
        'review': "#5f0834",
        'complete': "#ecb7f5",
        'backlog': '#8d8d8d',
        'done': "#ecb7f5",
        'backlog': '#8d8d8d',
        'blocked': "#ff4d4d", 
        'planned': "#4dabff",
    }


@login_required
def sprint_activity(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    return render(request, "partials/sprint_activity.html", {"board": board})

# KONVERTERAR DATA
def add_gantt_data(df):
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["deadline"] = pd.to_datetime(df["deadline"])
    df["deadline"] = df["deadline"].fillna(df["created_at"] + pd.Timedelta(days=5))
    df["start"] = df["created_at"].apply(date2num)
    df["end"] = df["deadline"].apply(date2num)
    df["duration"] = df["end"] - df["start"]
    return df



def draw_gantt_grid(ax, y_positions, x_start, x_end, step=1):
# VERTIKALA LINJER (TIDS-LINJER)
 for x in np.arange(x_start, x_end + 1, step):
        ax.axvline(x, color="#e0e0e0", linestyle="--", linewidth=0.5, zorder=0)
# HORISONTELLA LINJER
 for y in y_positions:
        ax.axhline(y, color="#f0f0f0", linestyle="--", linewidth=0.5, zorder=0)  


def render_text_chart(message):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    ax.text(0.5, 0.5, message,
            ha='center', va='center',
            fontsize=16, color='gray',
            transform=ax.transAxes)
    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type='image/png')  



@login_required
def sprint_chart_image(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if not board.members.filter(id=request.user.id).exists() and board.created_by != request.user:
        raise Http404("Oops! It looks like the page you're trying to access doesn't exist.")

    # HÄMTA ENDAST TASKS SOM TILLHÖR ETT BOARD OCH TASKS SOM FINNS
    tasks_qs = Task.objects.filter(board=board, column__isnull=False)

    df = pd.DataFrame([
        {
            "title": t.title,
            "status": t.column.title.lower().replace(" ", ""),
            "created_at": t.created_at,
            "deadline": t.deadline,
            "assigned_to": t.assigned_to.username if t.assigned_to else "Unassigned"
        }
        for t in tasks_qs
    ])

    if df.empty:
        return render_text_chart("No tasks available for this board.")

    df = add_gantt_data(df)

    today = now().replace(hour=0, minute=0, second=0, microsecond=0)
    sprint_start = date2num(today - pd.Timedelta(days=7))
    sprint_end = date2num(today + pd.Timedelta(days=14))

    if df["end"].max() < sprint_start:
        return render_text_chart("Sprint is finished. Please create a new one.")

    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # --- GANTT DIAGRAM ---
    y_pos = np.arange(len(df)) * 1.5
    bar_height = 0.4
    draw_gantt_grid(ax1, y_pos, sprint_start, sprint_end)

    for i, row in df.iterrows():
        x = row["start"]
        y = y_pos[i] - bar_height / 2
        rect = FancyBboxPatch(
            (x, y), row["duration"], bar_height,
            boxstyle="round,pad=0.2,rounding_size=0.15",
            facecolor=STATUS_COLORS.get(row["status"], "#cccccc"),
            edgecolor='none', zorder=1
        )
        ax1.add_patch(rect)
        deadline_text = row["deadline"].strftime("%b %d") if pd.notnull(row["deadline"]) else "No deadline"
        ax1.text(row["end"] + 0.2, y_pos[i], deadline_text, va='center')

    ax1.set_xlim(sprint_start, sprint_end)
    ax1.set_ylim(-1, y_pos[-1] + 1)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df["title"])
    ax1.set_title("Gantt Chart")
    ax1.axvline(x=date2num(today), color="#2f6a71", linestyle="--", linewidth=1)
    ax1.text(date2num(today), max(y_pos) - 1, "Today", color="#464B4B", fontsize=16, weight="bold")
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

    # --- PIE DIAGRAM ---
    counts = df["status"].value_counts().sort_index()
    pie_labels = counts.index.tolist()
    pie_sizes = counts.tolist()

    if not pie_sizes:
        return render_text_chart("No status data to display.")

    ax2.pie(
        pie_sizes,
        labels=[label.capitalize() for label in pie_labels],
        autopct=lambda pct: f"{int(round(pct * sum(pie_sizes) / 100))} tasks\n{int(round(pct))}%",
        startangle=90,
        colors=[STATUS_COLORS.get(label, "#cccccc") for label in pie_labels],
        textprops={'fontsize': 12, 'color': 'black', 'weight': 'bold'},
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
    )
    ax2.set_title("Task by Status")

    # RETURNERA SOM PNG FORMAT
    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type='image/png')









