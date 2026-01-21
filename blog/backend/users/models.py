from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    avatar = models.URLField(blank=True, null=True, verbose_name='头像')
    bio = models.CharField(max_length=200, blank=True, verbose_name='简介')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
