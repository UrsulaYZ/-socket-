#!/usr/bin/env Python
# coding=utf-8

#client功能实现模块（所有client共用）

import struct
import os
import json
import tkinter as tk
from tkinter import filedialog
import threading

global client
global host
global FILEPATH
fileSavePath="E:/学习文件/大三上/计算机网络/实验/实验5/服务端/"
count=3


def error_win():
    error = tk.Tk(className="Error!")
    e = tk.Label(error, text="出错了！")
    e.pack()
    error.mainloop()


def err_info(cou):
    l = tk.Label(mast, text="请求失败")
    l.grid(row=cou,column=3,sticky=tk.E, padx=10)


def success_win():
    success = tk.Tk(className="Success!")
    s = tk.Label(success, text="操作成功！")
    s.pack()
    success.mainloop()

def suc_info(cou):
    l = tk.Label(mast, text="请求成功")
    l.grid(row=cou,column=3,sticky=tk.E, padx=10)

def ope_info(cou, s):
    l = tk.Label(mast, text=s)
    l.grid(row=cou, column=0,sticky=tk.W, columnspan=3,padx=10)


def connec():
    if not entryport.get():
        return
    port=int(entryport.get())
    try:
        client.connect((host, port))
        label1['text']="客户端已连接  服务端端口"+str(port)
    except:
        error_win()
        label1['text']="客户端静默"
        return
    handle()

def begin():
    label1['text']="客户端正在连接……"
    s=threading.Thread(target=connec)
    s.start()

def getLocalFile():
    root=tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename()
    return file_path

def getFileName(l):
    fileName=l.get(l.curselection())
    file_name = fileName.split("/")[-1]
    l['state']=tk.DISABLED
    getfile(file_name)

def getSave(e1,save):
    global fileSavePath
    fileSavePath=e1.get()
    save.quit()

def getSavePath():
    global fileSavePath
    save=tk.Tk()
    l=tk.Label(save,text="文件上传")
    l.grid(row=0,column=0,padx=10)
    l1 = tk.Label(save, text="输入存储路径：")
    l1.grid(row=1,column=0,padx=10,sticky=tk.W)
    e1=tk.Entry(save)
    e1.insert(tk.END,fileSavePath)
    e1.grid(row=1,column=1,columnspan=2,padx=10,sticky=tk.W)
    b=tk.Button(save,text="提交",command=lambda :getSave(e1,save))
    b.grid(row=1,column=6,sticky=tk.E)
    save.mainloop()

def check(sig):
    global count
    if sig==0:
        select = "3"
        client.send(bytes(select, "utf-8"))
    count+=1
    completed = "1"
    try:
        data=client.recv(1024)
        directory = json.loads(data.decode('utf-8'))
    except:
        completed="0"
    # 向服务器发送信号，接收完毕

    client.send(bytes(completed, "utf-8"))
    if completed=="0":
        err_info(count)
        return

    l=tk.Label(mast,text="服务端目录：")
    l.grid(row=count,padx=10,sticky=tk.W)
    count+=1
    f=tk.Frame(mast,bg='white')
    f.grid(row=count,column=0,columnspan=10,ipadx=10,ipady=10)
    LB2 = tk.Listbox(mast)
    for item in directory:
        LB2.insert(tk.END,item)

    '''if sig==1:
                down=tk.Button(LB2,text="下载",command=lambda :getfile(directory[i]))

                down.grid(row=count,column=3,sticky=tk.E,padx=5)'''
    if sig==1:
        LB2.bind('<ButtonRelease-1>',lambda event:getFileName(l=LB2))
    LB2.grid(row=count, column=1, columnspan=9,pady=10)

def put():
    select="1"
    client.send(bytes(select, "utf-8"))

    filePath=getLocalFile()
    fileName = filePath.split("/")[-1]

    global count
    count += 1
    cou = count
    s = "上传文件" + filePath + "中"
    ope_info(cou, s)

    global fileSavePath
    fileSavePath="E:/学习文件/大三上/计算机网络/实验/实验5/服务端/"+fileName
    getSavePath()
    fileNameSave = fileSavePath.split("/")[-1]

    # 得到文件的大小
    if not filePath:
        filesize_bytes=0
        fileName=""
    else:
        filesize_bytes = os.path.getsize(filePath)
        fileName=fileNameSave
        # 创建复制文件
   # 创建字典用于报头
    dirc = {"fileName": fileName,
            "fileSize": filesize_bytes,
            "filePathSave":fileSavePath,}

    # 将字典转为JSON字符，再将字符串的长度打包
    head_infor = json.dumps(dirc)
    head_infor_len = struct.pack('i', len(head_infor))

    # 先发送报头长度，然后发送报头内容
    client.send(head_infor_len)
    client.send(head_infor.encode("utf-8"))

    if fileName=="":
        err_info(cou)
        return

    # 发送真实文件
    with open(filePath, 'rb') as f:
        data = f.read()
        client.sendall(data)
        f.close()

    # 服务器若接受完文件会发送信号，客户端接收
    completed = client.recv(1024).decode("utf-8")
    if completed == "1":
        suc_info(cou)
    else:
        error_win()
        err_info(cou)

def get():
    select="2"
    client.send(bytes(select, "utf-8"))

    check(1)


def getfile(fileName):
    global count
    client.send(bytes(fileName, "utf-8"))

    count+=1
    cou=count
    s="用户正在下载 "+fileName+" 文件中"
    ope_info(cou,s)

    # 接受并解析报头的长度，接受报头的内容
    head_struct = client.recv(4)
    head_len = struct.unpack('i', head_struct)[0]
    data = client.recv(head_len)

    # 解析报头字典
    head_dir = json.loads(data.decode('utf-8'))
    filesize_b = head_dir["fileSize"]
    filename = head_dir["fileName"]

    # 接受真实的文件内容
    recv_len = 0
    recv_mesg = b''

    global fileSavePath
    fileSavePath=FILEPATH+filename
    getSavePath()

    fsp = fileSavePath[::-1].split('/', 1)[-1][::-1] + '/'

    isExists = os.path.exists(fsp)

    # 判断结果
    if not isExists:
        os.makedirs(fsp)

    f = open("%s" % fileSavePath, "wb")
    completed="1"
    while recv_len < filesize_b:
        if filesize_b - recv_len > 1024:
            # 假设未上传的文件数据大于最大传输数据
            try:
                recv_mesg = client.recv(1024)
            except:
                err_info(cou)
                completed = "0"
                break
            f.write(recv_mesg)
            recv_len += len(recv_mesg)
        else:
            # 需要传输的文件数据小于最大传输数据大小
            try:
                recv_mesg = client.recv(filesize_b - recv_len)
            except:
                err_info(cou)
                completed = "0"
                break
            recv_len += len(recv_mesg)
            f.write(recv_mesg)
            f.close()

    # 向服务器发送信号，文件已经上传完毕
    client.send(bytes(completed, "utf-8"))
    if completed=="1":
        suc_info(cou)
    else:
        err_info(cou)


def handle():
    global mast
    mast = tk.Tk(className="客户端")
    l = tk.Label(mast, text="客户端服务")
    l.grid(row=0, padx=10, sticky=tk.W)
    b1 = tk.Button(mast, text="上传文件", command=put)
    b1.grid(row=1, column=0, padx=10,pady=5,sticky=tk.W)
    b2 = tk.Button(mast, text="下载文件", command=get)
    b2.grid(row=1, column=1, padx=10,pady=5,sticky=tk.W)
    b3 = tk.Button(mast, text="查看目录", command=lambda:check(0))
    b3.grid(row=1, column=2, padx=10,pady=5,sticky=tk.W)
    b4 = tk.Button(mast, text="退出系统", command=mast.quit)
    b4.grid(row=1, column=3, padx=10,pady=5,sticky=tk.W)
    l1=tk.Label(mast,text="响应流程")
    l1.grid(row=2,column=0,columnspan=5,padx=10,pady=10,sticky=tk.W)
    mast.mainloop()

def client_close():
    select="0"
    client.send(bytes(select, "utf-8"))
    client.close()
    client_win.quit()

def client_window(c,h,f):
    global client
    client=c
    global host
    host=h
    global FILEPATH
    FILEPATH=f

    global client_win
    client_win = tk.Tk(className='Client')
    global label1
    label1 = tk.Label(client_win, text='客户端静默')
    label1.grid(row=0, columnspan=3, sticky=tk.W)
    global label2
    label2 = tk.Label(client_win, text="服务器端口：")
    label2.grid(row=1, column=0, sticky=tk.W)
    global entryport
    entryport = tk.Entry(client_win)
    entryport.grid(row=1, column=1,columnspan=3, padx=5, pady=10)
    global button
    button = tk.Button(client_win, text="连接", command=begin)
    button.grid(row=2,column=1,padx=10,pady=5)
    global quitcon
    quitcon=tk.Button(client_win, text="停止", command=client_close)
    quitcon.grid(row=2, column=2, padx=10, pady=5)

    client_win.mainloop()



