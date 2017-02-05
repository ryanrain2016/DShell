# DShell

通过Django在web上实现xshell的功能。


# 使用

需安装requirements.txt中的包其中pywin32为twisted在windows上的依赖，linux不必安装。部署参见channels的文档。使用需执行python manage.py paramiko_proxy启动paramiko的代理。所有信息通过websocket，并未加密。如需加密需使用https协议。用户需自行编写操作shell应用中Host模型中的记录的代码。webshell的url为 /webshell/(?P<id>\d+)/，id为Host模型中记录的主键。