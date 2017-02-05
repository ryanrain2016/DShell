from django.core.management.base import BaseCommand,CommandError 
from django.conf import settings
import websocket
import threading
import json
import time
import paramiko
from shell import models
import multiprocessing
import os

connected_channels={}
glock = threading.Lock()
ISALIVE = True
_select_thread = None

def getchannel(key,id):
    if key in connected_channels:
        channel = connected_channels[key][1]
    else:
        host = models.Host.objects.get(pk=id)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host.addr,host.port,host.username,host.password)
        channel = ssh.invoke_shell()
        channel.setblocking(0)
        glock.acquire()
        connected_channels[key] = [ssh,channel]
        glock.release()
    return channel

def reconnectChannel(key,id):
    glock.acquire()
    del connected_channels[key]
    glock.release()
    return getchannel(key,id)

def on_message(ws, message):
    global _select_thread
    if not _select_thread.is_alive():
        _select_thread = threading.Thread(target=select,args=(ws,))
        _select_thread.setDaemon(True)
        _select_thread.start()
    msg = json.loads(message)
    if msg['cmd']=='stream':
        data = msg['data']
        key = msg['reply_channel']
        id = msg['id']
        channel = getchannel(key,id)
        try:
            channel.send(data)
        except:
            channel = reconnectChannel(key,id)
            channel.send(data)
    elif msg['cmd']=='discard':
        glock.acquire()
        if msg['reply_channel'] in connected_channels:
            connected_channels[msg['reply_channel']][1].close()
            connected_channels[msg['reply_channel']][0].close()
            del connected_channels[msg['reply_channel']]
        glock.release()
    print(msg)

def on_error(ws, message):
    print(message,'error')

def on_close(ws):
    pass

def on_open(ws):
    global _select_thread
    print('conencted')
    if _select_thread is None:
        _select_thread = threading.Thread(target=select,args=(ws,))
        _select_thread.setDaemon(True)
        _select_thread.start()

def select(ws):
    while ISALIVE:
        glock.acquire()
        if not ISALIVE:
            glock.release()
            break
        for key in connected_channels:
            channel = connected_channels[key][1]
            if ISALIVE and channel.recv_ready():
                data = channel.recv(2048)
                data = str(data,'utf-8')
                try:
                    ws.send(json.dumps(dict(action='stream',reply_channel=key,data=data)))
                except websocket._exceptions.WebSocketConnectionClosedException:
                    glock.release()
                    print('ws disconnected error')
                    return
            elif not ISALIVE:
                return
        glock.release()
        time.sleep(0.01)
def worker(url):
    ws = websocket.WebSocketApp("ws://127.0.0.1/paramiko_proxy/",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


def main(url):
    while True:
        try:
            worker(url)
        except:
            pass
        time.sleep(5)
        glock.acquire()
        connected_channels={}
        glock.release()


class Command(BaseCommand):
    help = '开启paramiko代理,实现webshell'

    def handle(self,*args,**options):
        site = getattr(settings,'SITE','127.0.0.1')
        ws_protocol = getattr(settings,'WS_PROTOCOL','ws')
        url = '%s//%s/paramiko_proxy/'
        main(url)