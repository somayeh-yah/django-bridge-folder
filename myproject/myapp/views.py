from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from .forms import RegisterForm
from django.http.response import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import ChatRoom, ChatMessage 
from kanban.models import Board

# Create your views here.


User = get_user_model()


def landing_page(request):
    return render(request, "landing_page.html")


def home(request):
    return render(request, "home.html")


# Login View (Django har redan en inbyggd LoginView)
class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.PARTICIPANT:
                return reverse_lazy("dashboard_student")
            elif user.role == User.TEACHER:
                return reverse_lazy("dashboard_teacher")
            elif user.role == User.ADMIN:
                return reverse_lazy("dashboard_admin")
        return reverse_lazy("landing_page")


def password_reset(request):
    return render(request, "password_reset.html")


def password_reset_done(request):
    return render(request, "password_reset_done.html")


def password_reset_email(request):
    return render(request, "password_reset_email.html")


def password_reset_confirm(request):
    return render(request, "password_reset_confirm.html")


# Register View
class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = RegisterForm
    # success_url = reverse_lazy("landing_page")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # Loggar in användaren direkt efter registrering
        print(
            f"User {user.username} is logged in: {self.request.user.is_authenticated}"
        )

        # här skickar vi en anpassad meddelande baserat på roll

        if user.role == User.PARTICIPANT:
            messages.success(
                self.request,
                f"Welcome {user.username}! You are logged in as a student.",
            )
        elif user.role == User.TEACHER:
            messages.success(
                self.request,
                f"welcome {user.username}! You are logged in as a teacher.",
            )
        elif user.role == User.ADMIN:
            messages.success(
                self.request,
                f"Welcome {user.username}! You are logged in as a admin.",
            )
        else:
            messages.info(self.request, f"Welcome {user.username}!")

        return super().form_valid(form)

    # här navigerar vi användaren till rätt endpoint/vy baserat på hens roll
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:

            if user.role == User.PARTICIPANT:
                return reverse_lazy("dashboard_student")
            elif user.role == User.TEACHER:
                return reverse_lazy("dashboard_teacher")
            elif user.role == User.ADMIN:
                return reverse_lazy("dashboard_admin")
        return reverse_lazy("landing_page")


@login_required
def check_role(request):
    user = request.user
    if user.role == "participant":
        redirect_url = reverse_lazy("dashboard_student")
    elif user.role == "teacher":
        redirect_url = reverse_lazy("dashboard_teacher")
    elif user.role == "admin":
        redirect_url = reverse_lazy("dashboard_admin")
    else:
        redirect_url = reverse_lazy("landing_page")

    return JsonResponse(
        {
            "username": user.username,
            "role": user.role,
            "redirect_url": str(redirect_url),
        }
    )


def check_username(request):
    username = request.POST.get("username", "").strip()
    if not username:
        return HttpResponse("<div class='error'>Username is required</div>")

    if User.objects.filter(username=username).exists():
        return HttpResponse(
            "<div id='username-error'class='error' '>this username already exists</div>"
        )
    else:
        return HttpResponse(
            "<div id='username-error' class='success'>This username are available</div>"
        )


def sidebar(request):
    return render(request, "partials/sidebar.html")


@login_required
def dashboard_student(request):
    boards = Board.objects.all() 
    return render(request, 'dashboard_student.html', {'boards': boards})



@login_required
def dashboard_teacher(request):
    return render(request, "partials/dashboard_teacher.html")



@login_required
def dashboard_admin(request):
    return render(request, "partials/dashboard_admin.html")


@login_required
def dashboard_chat(request):
    user = request.user
    rooms = ChatRoom.objects.filter(participants= user)
    group_chats = rooms.filter(is_group_chat = True)
    single_chats = rooms.filter(is_group_chat = False)

     
    single_chats_with_other_user = []
    for chat in single_chats:
        other_user = chat.participants.exclude(id=user.id).first()
        single_chats_with_other_user.append({
            "chat": chat,
            "other_user": other_user
        })

      # HÄMTA SENASTE RUM SOM SKAPADES 
    room = rooms.order_by('-messages__timestamp', '-created_at').first()
    messages = room.messages.all() if room else []

 

    return render(request, "chat.html", {
        "room": room,
        "rooms": rooms,
        "messages": messages,
        "group_chats": group_chats,
        "single_chats_with_other_user": single_chats_with_other_user
       
    })


@login_required
def create_direct_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # KONTROLLERAR OM RUM FINNS 
    room = ChatRoom.objects.filter(participants=request.user, is_group_chat=False).filter(participants=other_user).first()

    if not room:
        # SKAPA ETT NYY RUM OM RUM INTE FINNS
        room = ChatRoom.objects.create(is_group_chat=False)
        room.participants.add(request.user, other_user)

    messages = room.messages.all()

    return render(request, "partials/chat_room_content.html", {"room": room, "messages": messages})



# @login_required
# def start_chat(request):
#     users = User.objects.exclude(id=request.user.id)  # Alla andra användare
#     return render(request,  "partials/start_chat_modal.html", {"users": users})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in room.participants.all():
        return HttpResponse("Unauthorized", status=401)

    messages = room.messages.all()
    return render(request, "partials/chat_room_content.html", {
        "room": room,
        "messages": messages
    })



@login_required
def message_list(request, room_id):
    room = get_object_or_404(ChatRoom, id= room_id)
    return render(request, "partials/message_list.html", {
    "messages": room.messages.select_related("sender").all(),
    "user": request.user
})

@login_required
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    message = request.POST.get("message")

    if message:
        ChatMessage.objects.create(
            room=room,
            sender=request.user,
            content= message
        )

        messages = room.messages.select_related("sender").all()[:30]

   
    return render(request, "partials/message_list.html", {"messages" : messages})

@login_required
def message_display(request,message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    return render(request, "partials/message_display.html", {"message" : message})


@login_required
def edit_message_form(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id, sender=request.user)
    return render(request, "partials/edit_message_form.html", {"message": message})

@login_required
def update_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id, sender= request.user)
    edited_message = request.POST.get("content")
    
    if edited_message:
        message.content = edited_message
        message.edited = True
        message.save()

        return render(request, "partials/message_display.html", {
        "message": message,
        "user": request.user 
        })
  

def delete_message(request, message_id):
     message = get_object_or_404(ChatMessage, id=message_id, sender= request.user)
     

     if request.method == "POST":
        message.delete_message = True
        message.save()
     
        return render(request, "partials/delete_message.html", {"message": message})
  

def courses(request):
    return render(request, "courses.html")


def features(request):
    return render(request, "features.html")


def success_stories(request):
    return render(request, "success_stories.html")


def about(request):
    return render(request, "about.html")


def faq(request):
    return render(request, "faq.html")


def support(request):
    return render(request, "support.html")


def pricing(request):
    return render(request, "pricing.html")


def contact(request):
    return render(request, "contact.html")


