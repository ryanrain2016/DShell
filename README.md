# DShell

通过Django 在web上实现xshell的功能。


# 使用

需安装requirements.txt中的包，部署参见chanels的文档。使用需执行python manage.py paramiko_proxy启动paramiko的代理。
所有信息通过websocket，并未加密。如需加密需使用https协议。用户需自行编写操作shell应用中Host模型中的记录的代码。
对应的webshell的url为 /webshell/(?P<id>\d+)/，id为Host模型中记录的主键。