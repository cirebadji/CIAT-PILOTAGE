from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from projects import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("projets/", include("projects.urls")),
    path("cohortes/", views.cohort_list, name="cohort_list"),
    path("analyses/", views.analytics_page, name="analytics"),
    path("assistant/", views.ai_assistant, name="ai_assistant"),
    path("rapports/excel/", views.export_excel, name="export_excel"),
    path("rapports/pdf/", views.export_pdf, name="export_pdf"),
]
