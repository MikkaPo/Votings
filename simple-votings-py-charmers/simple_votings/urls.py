from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from main.views import (
    create_post,
    registration,
    menu,
    user_profile,
    edit_profile,
    delete_avatar,
    posts_page
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Аутентификация
    path('register/', registration, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login/login_form.html', next_page='/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Посты
    path('post_creation/', create_post, name="create"),
    
    # Главная страница
    path('', menu, name="main"),
    
    # Профиль
    path('profile/<int:user_id>/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/delete/', delete_avatar, name="delete_avatar"),
    path('posts/<int:post_id>/', posts_page, name='posts_page'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Использование картинок в дебаге