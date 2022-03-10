#!/usr/bin/python
# author hyx
# 2022年03月07日
from socket import *
import struct
import os

class Client:
    def __init__(self,ip,port):
        self.client=None
        self.ip=ip
        self.port=port

    def tcp_connect(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect((self.ip,self.port))

    def send_train(self,send_bytes):
        train_head_bytes=struct.pack('I',len(send_bytes))
        self.client.send(train_head_bytes+send_bytes)

    def recv_train(self):
        train_head_bytes = self.client.recv(4)  # 接收文件长度
        train_head = struct.unpack('I', train_head_bytes)
        return self.client.recv(train_head[0])  # 接收文件

    def do_ls(self):    #ls命令
        '''
        列出当前路径下的所有文件
        '''
        #接收服务器发送来的文件信息
        data=self.recv_train().decode('utf8')
        print(data)

    def do_cd(self):    #cd命令
        '''
        切换当前工作目录
        :return:
        '''
        nowpath=self.recv_train().decode('utf8')
        print(nowpath)

    def do_pwd(self):   #pwd命令
        '''
        显示当前工作目录
        :return:
        '''
        data=self.recv_train().decode('utf8')
        print(data)

    def do_rm(self):    #rm命令
        '''
        删除指定文件
        :return:
        '''
        data = self.recv_train().decode('utf8')
        print(data)

    def do_gets(self,command):    #gets命令
        '''
        从服务器下载指定文件
        :return:
        '''
        data = self.recv_train().decode('utf8')
        if data=='1':
            print('ERROR: 文件不存在！')
        else:
            file_path=command.split()[1]
            print(file_path)
            # 在当前路径下创建一个文件并打开
            fd = open(file_path, 'wb')
            file_content=self.recv_train()
            fd.write(file_content)
            print('下载成功！')


    def do_puts(self,command):    #puts命令
        '''
        将指定文件上传至服务器
        :param command:
        :return:
        '''
        file_path = command.split()[1]
        flag = os.path.exists(file_path)  # 查看文件是否存在
        if flag == False:  # 文件不存在
            data = '1'
            self.send_train(data.encode('utf8'))
            print('文件不存在！')
        else:  # 文件存在
            data = '2'
            self.send_train(data.encode('utf8'))
            fd = open(file_path, 'rb')
            file_content = fd.read()
            self.send_train(file_content)
            result=self.recv_train().decode('utf8')
            print(result)

    def send_command(self):
        while True:
            command=input()     #输入选择指令
            # 调用函数将命令封装处理并发送
            self.send_train(command.encode('utf8'))
            if command[:2] == 'ls':  #前两个字符为ls
                self.do_ls()
            elif command[:2] == 'cd':
                self.do_cd()
            elif command[:3] == 'pwd':
                self.do_pwd()
            elif command[:2] == 'rm':
                self.do_rm()
            elif command[:4] == 'gets':
                self.do_gets(command)
            elif command[:4] == 'puts':
                self.do_puts(command)
            else:
                print('wrong command!')




if __name__ == '__main__':
    client=Client('192.168.40.1',6666)
    client.tcp_connect()
    client.send_command()