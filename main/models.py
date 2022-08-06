from django.db import models


# class User(models.Model):
#     '''用户表'''
#     username = models.CharField(max_length=128, unique=True)
#     password = models.CharField(max_length=256)
#     email = models.EmailField(unique=True)
#     created = models.DateTimeField(auto_now_add=True)
 
#     def __str__(self):
#         return self.username
 
#     class Meta:
#         ordering = ['email']
        # verbose_name = '用户'
        # verbose_name_plural = '用户'