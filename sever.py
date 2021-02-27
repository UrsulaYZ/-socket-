#服务端模拟

import threading
import socket
import json
import os
import struct
import queue
import sys
import tkinter as tk

global serversocket

server_win = tk.Tk(className='Server')
FILEPATH = "E:/学习文件/大三上/计算机网络/实验/实验5/服务端/"
count=3

def on_click1():
    label1['text']="服务端正在监听……"
    s=threading.Thread(target=soc_init)
    s.start()

def on_click2():
    label1['text']="服务端静默中"
    stop_listen()

def error_win():
    error=tk.Tk(className="Error!")
    e=tk.Label(error,text="出错了！")
    e.pack()
    error.mainloop()

def err_info(cou):
    l=tk.Label(server_win,text="请求失败")
    l.grid(row=cou,column=1,padx=10)


def success_win():
    success=tk.Tk(className="Success!")
    s=tk.Label(success,text="操作成功！")
    s.pack()
    success.mainloop()

def suc_info(cou):
    l=tk.Label(server_win,text="请求成功")
    l.grid(row=cou,column=1,padx=10)

def ope_info(cou,s):
    l=tk.Label(server_win,text=s)
    l.grid(row=cou,column=0,padx=10)


class ThreadPoolManger:
    def __init__(self,thread_num):
        self.work_queue= queue.Queue()
        self.thread_num=thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self,thread_num):
        for i in range(thread_num):
            thread=ThreadManger(self.work_queue)
            thread.start()

    def add_job(self,func,*args):
        self.work_queue.put((func,args))

class ThreadManger(threading.Thread):
    def __init__(self,work_queue):
        threading.Thread.__init__(self)
        self.work_queue=work_queue
        self.daemon=True

    def run(self):
        while True:
            target,args=self.work_queue.get()
            target(*args)
            self.work_queue.task_done()

def get(client, index):
    global count
    count+=1
    cou=count
    s="用户"+str(index)+"请求上传文件"
    ope_info(cou,s)

    try:
        head_struct = client.recv(4)
    except:
        err_info(cou)
        return

    # 解析报头的长度
    head_len = struct.unpack('i', head_struct)[0]

    # 接收报头内容
    data = client.recv(head_len)

    # 解析报头的内容, 报头为一个字典其中包含上传文件的大小和文件名，
    head_dir = json.loads(data.decode("utf-8"))  # 将JSON字符串解码为python对象

    filesize_b = head_dir["fileSize"]
    fileName = head_dir["fileName"]
    filePathSave=head_dir["filePathSave"]

    if fileName=="":
        err_info(cou)
        return

    # 接收真实的文件内容
    recv_len = 0
    recv_mesg = b''

    # 在服务器文件夹中创建新文件
    fileInfor = filePathSave

    fsp = filePathSave[::-1].split('/', 1)[-1][::-1] + '/'

    isExists = os.path.exists(fsp)
    # 判断结果
    if not isExists:
        os.makedirs(fsp)
    f = open(fileInfor, "wb")
    completed = "1"
    # 开始接收用户上传的文件
    while recv_len < filesize_b:
        if filesize_b - recv_len > 1024:
            # 假设未上传的文件数据大于最大传输数据
            try:
                recv_mesg = client.recv(1024)
            except:
                err_info(cou)
                completed="0"
                break
            f.write(recv_mesg)
            recv_len += len(recv_mesg)
        else:
            # 需要传输的文件数据小于最大传输数据大小
            try:
                recv_mesg = client.recv(filesize_b - recv_len)
            except:
                err_info(cou)
                completed="0"
                break
            recv_len += len(recv_mesg)
            f.write(recv_mesg)
            f.close()
    # 向用户发送信号，文件已经上传完毕
    client.send(bytes(completed, "utf-8"))
    if completed=="1":
        suc_info(cou)

def put(client,index):
    global count
    check(client,index)
    count+=1
    cou=count
    s="用户"+str(index)+"请求下载文件"
    ope_info(cou,s)
    fileName = client.recv(1024).decode("utf-8")
    if not fileName:
        error_win()
        err_info(cou)
        return
    fileInfor = FILEPATH + fileName

    # 默认文件存在，得到文件的大小
    filesize_bytes = os.path.getsize(fileInfor)

    # 创建报头字典
    filename = fileName.split("\\")[-1]
    dirc = {"fileName": filename,
            "fileSize": filesize_bytes}

    # 将字典转换为JSON字符串利于传输，再将字符串的长度打包
    head_infor = json.dumps(dirc)
    head_infor_len = struct.pack('i', len(head_infor))

    # 先发送报头长度，然后发送报头内容
    client.send(head_infor_len)
    client.send(head_infor.encode("utf-8"))

    if getattr(client, '_closed'):
        err_info(cou)
        return

    # 开始发送真实文件
    with open(fileInfor, 'rb') as f:
        data = f.read()
        client.sendall(data)
        f.close()

    # 如果客户端下载完文件则接受到用户发送的信号
    completed = client.recv(1024).decode("utf-8")
    if completed == "1":
        suc_info(cou)
    else:
        error_win()
        err_info(cou)

def dirct(path,list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path,file)
        if os.path.isdir(file_path):
            dirct(file_path,list_name)
        else:
            file_name = file_path.split("/")[-1]
            list_name.append(file_name)

def check(client,index):
    global count
    count+=1
    cou=count
    s="用户"+str(index)+"请求查看目录"
    ope_info(cou,s)
    direc=[]
    dirct(FILEPATH,direc)

    lis=json.dumps(direc)
    client.send(lis.encode("utf-8"))
    # 如果客户端接收成功，则接受到用户发送的信号
    completed = client.recv(1024).decode("utf-8")
    if completed == "1":
        suc_info(cou)
    else:
        error_win()
        err_info(cou)


def child_connection(index,sock,connection):
    '''try:'''
    global count
    count += 1
    cou=count
    s = "用户" + str(index) + "正在连接"
    ope_info(cou, s)
    while True:
        try:
            select = connection.recv(1024).decode("utf-8")
            suc_info(cou)
        except Exception:
            count += 1
            s1 = "用户" + str(index) + "已断开.   sock:" + str(sock)
            ope_info(cou, s1)
            break

        if select == "1":
            get(connection, index)
        elif select == "2":
            put(connection, index)
        elif select == "3":
            check(connection, index)
        elif select == "0":
            count += 1
            s = "用户" + str(index) + "关闭连接"
            ope_info(count, s)
            break
        else:
            error_win()
            break
    '''except socket.timeout:
        count+=1
        s="用户"+str(index)+"超时退出"
        ope_info(count,s)'''

    connection.close()


def soc_init():
    global serversocket
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        error_win()
        global count
        count+=1
        cou=count
        s="创建socket失败"
        ope_info(cou,s)
        sys.exit()
    host = socket.gethostname()  # 获取本地主机名
    port = 9999
    # 绑定端口号
    serversocket.bind((host, port))
    # 设置最大连接数
    serversocket.listen(5)
    thread_pool = ThreadPoolManger(4)
    index=0
    while True:
        try:
            connection, address = serversocket.accept()
            thread_pool.add_job(child_connection, *(index, serversocket, connection))
            # t=threading.Thread(target=child_connection,args=(index,serversocket,connection))
            # t.start()
            index += 1

            if index > 10:
                break
        except:
            break
    serversocket.close()

def stop_listen():
    try:
        serversocket.close()
    except:
        return


global label1
label1 = tk.Label(server_win, text='服务端静默')
label1.grid(row=0,columnspan=3,sticky=tk.W)
global button
button = tk.Button(server_win, text='监听',command=on_click1)
global squit
squit=tk.Button(server_win,text="停止监听",command=on_click2)
global rootquit
rootquit=tk.Button(server_win,text="关闭服务端",command=server_win.quit)
label2=tk.Label(server_win,text='用户请求：')
button.grid(row=1,column=0,padx=20,sticky=tk.W)
squit.grid(row=1,column=1,padx=20,pady=20,sticky=tk.W)
rootquit.grid(row=1,column=2,padx=20,sticky=tk.W)
label2.grid(row=2,column=0,sticky=tk.W)



if __name__ == '__main__':
    server_win.mainloop()






