from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomLoginView, RegisterView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("home/", views.home, name="home"),
    path("login/", CustomLoginView.as_view(), name="login"), 
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("password_reset/", views.password_reset, name="password_reset"),
    path("password_reset_done", views.password_reset_done, name="password_reset_done"),
    path(
        "password_reset_email/", views.password_reset_email, name="password_reset_email"
    ),
    path(
        "password_reset_confirm",
        views.password_reset_confirm,
        name="password_reset_confirm", 
    ),
    path("register/", RegisterView.as_view(), name="register"),
    path("dashboard/student/", views.dashboard_student, name="dashboard_student"),
    path("dashboard_student/chat/", views.dashboard_chat, name="dashboard/student/chat"),
    path("dashboard_teacher/", views.dashboard_teacher, name="dashboard_teacher"),
    path("dashboard_admin/", views.dashboard_admin, name="dashboard_admin"),
    path("courses/", views.courses, name="courses"),
    path("features/", views.features, name="features"),
    path("success_stories/", views.success_stories, name="success_stories"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("support/", views.support, name="support"),
    path("pricing/", views.pricing, name="pricing"),
    path("contact/", views.contact, name="contact"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

htmx_views = [
    path("sidebar/", views.sidebar, name="sidebar"),
    path("check_role/", views.check_role, name="check_role"),
    path("check_username/", views.check_username, name="check_username"),
    path("chat/create/<int:user_id>/", views.create_direct_chat, name="create_direct_chat"),
    # path("chat/rooms/", views.start_chat, name="start_chat"),
    path("chat/<int:room_id>/", views.chat_room, name="chat_room"),
    path("chat/<int:room_id>/messages/", views.message_list, name="message_list"),
    path("chat/<int:room_id>/send/", views.send_message, name="send_message"),
    path("chat/<int:message_id>/message/", views.message_display, name="message_display"),
    path("chat/<int:message_id>/edit/", views.edit_message_form, name="edit_message_form"),
    path("chat/<int:message_id>/update/", views.update_message, name="update_message"),
    path("chat/<int:message_id>/delete/", views.delete_message, name= "delete_message"),
    
]


urlpatterns += htmx_views
