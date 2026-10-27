from django.urls import path, reverse_lazy
from . import views
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from .views import AnimalLoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('animals/', views.directory, name='directory'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('animals/add/', views.animal_create, name='animal_create'),
    path('animals/<int:pet_id>/', views.animal_detail, name='animal_detail'),
    path('animals/<int:pet_id>/apply/', views.adopt_apply, name='adopt_apply'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/manage/', views.manage_applications, name='manage_applications'),
    path('applications/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    path('animals/<int:pet_id>/edit/', views.animal_update, name='animal_update'),
    path('animals/<int:pet_id>/delete/', views.animal_delete, name='animal_delete'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('profile/', views.profile, name='profile'),
    path('accounts/signup/', views.sign_up, name='signup'),
    path(
        'accounts/login/',
        AnimalLoginView.as_view(),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'accounts/password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('password_change_done'),
        ),
        name='password_change',
    ),
    path(
        'accounts/password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
        name='password_change_done',
    ),
    path(
        'accounts/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/animals/', views.admin_manage_animals, name='admin_manage_animals'),
    path('admin-dashboard/animals/<int:pet_id>/status/', views.admin_update_animal_status, name='admin_update_animal_status'),
    path('pet_management/', RedirectView.as_view(pattern_name='directory', permanent=False), name='pet'),
    path('pet_management/<int:pet_id>/edit/', views.animal_update, name='pet_update'),
    path('pet_management/<int:pet_id>/delete/', views.animal_delete, name='pet_delete'),
]