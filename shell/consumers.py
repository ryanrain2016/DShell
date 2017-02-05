import json
import os
import paramiko
import threading, time, re
from channels.sessions import channel_session,http_session
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from channels import Channel,Group
from . import models

def terminal2html(data):
    data = data.replace('\n','<br>').replace(' ','&nbsp;').replace('\033[K','').replace('\033[m','\033[0m')
    data = re.sub(r'(\033\[((\d{1,2};?)+)m)', deal_term, data)
    return data

def deal_term(term):
    colors = ['black','red','green','yellow','blue','purple','green','white']
    s = term.groups()[1]
    if s=='0':
        return '</font>'
    modes = s.split(';')
    style=''
    for mode in modes:
        mode = int(mode)
        if 30<=mode<=37:
            style+='color:%s;'%colors[mode-30]
        elif 40<=mode<=47:
            style+='background:%s;'%colors[mode-40]
    return '<font style="%s">'%style

def ws_paramiko_proxy_c(message):
    # print(dir(Group('paramiko')))
    Group('paramiko').add(message.reply_channel)
    message.reply_channel.send({'accept':True})
    

def ws_paramiko_proxy(message):
    text = message.content['text']
    msg = json.loads(text)
    key = msg['reply_channel']
    data = msg['data']
    Channel(key).send({'text':json.dumps(dict(
        html = '<span>%s</span>'%terminal2html(msg['data'])
    ))})

def ws_paramiko_proxy_d(message):
    Group('paramiko').discard(message.reply_channel)


@channel_session_user_from_http
def ws_webshell_c(message,id):
    user = message.user #可以通过此用户判断是否有权限操作该机器
    host = models.Host.objects.get(pk=id)
    if host:
        message.reply_channel.send({'accept':True})
    else:
        message.reply_channel.send({'accept':False})


@channel_session_user
def ws_webshell(message,id):
    content = json.loads(message.content['text'])
    msg = dict(cmd='stream',data=content['cmd'],id=id,reply_channel=message.reply_channel.name)
    Group('paramiko').send({'text':json.dumps(msg)})

@channel_session_user
def ws_webshell_d(message,id):
    msg = dict(cmd='discard',reply_channel=message.reply_channel.name)
    Group('paramiko').send({'text':json.dumps(msg)})