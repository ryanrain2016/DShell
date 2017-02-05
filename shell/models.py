from django.db import models

# Create your models here.

class Host(models.Model):
    name = models.CharField(max_length=32,verbose_name='名称')
    addr = models.CharField(max_length=128,verbose_name='地址')
    port = models.IntegerField(verbose_name='SSH端口')
    username = models.CharField(max_length=32,default='root',verbose_name='主机用户名')
    password = models.CharField(max_length=64,verbose_name='密码')
