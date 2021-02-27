#模拟客户端1

import socket
from client import client_window

client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
FILEPATH="E:/学习文件/大三上/计算机网络/实验/实验5/客户端1/"

if __name__ == '__main__':
    client_window(client1,host,FILEPATH)




