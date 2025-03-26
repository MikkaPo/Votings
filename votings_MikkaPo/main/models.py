from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# Create your models here

def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{"user_avatar.jpg"}' #Создаем путь для папки для хранения аватарки юзера
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile") #Соединяем User и его аватрку в БД
    avatar = models.ImageField(upload_to=user_avatar_path, default='avatars/default.png') #загружем аватар в папку по этому пути

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(to=User, on_delete=models.CASCADE)
    post_text = models.TextField()
    creation_dt = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(to=User, on_delete=models.CASCADE)
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PostVariant(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    variant_text = models.TextField()


class Votes(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(to=User, on_delete=models.CASCADE)
    post_variant = models.ForeignKey(to=PostVariant, on_delete=models.CASCADE)