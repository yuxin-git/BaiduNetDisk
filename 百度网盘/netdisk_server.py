#!/usr/bin/python
# author hyx
# 2022年03月07日
from socket import *
import struct
import os
class Server():
    def __init__(self,ip,port):
        self.s_listen:socket=None
        self.ip=ip
        self.port=port

    def tcp_init(self):
        self.s_listen = socket(AF_INET, SOCK_STREAM)
        addr = (self.ip, self.port)
        self.s_listen.bind(addr)
        self.s_listen.listen(128)

    def task(self):
        new_client,client_addr=self.s_listen.accept()
        user=User(new_client)
        user.deal_command()


class User():
    def __init__(self,new_client):
        self.new_client:socket=new_client
        self.user_name=None
        self.path=os.getcwd()   #调用getcwd获取当前路径

    def do_ls(self):    #ls命令
        '''
        列出当前路径下的所有文件并传输给客户端
        '''
        data=''
        #调用listdir获取当前路劲下的所有文件
        #stat获取文件相关信息
        for file in os.listdir(self.path):
            data += file + ' ' * 5 + 'size: ' + str(os.stat(file).st_size) + '\n'
        self.send_train(data.encode('utf8'))


    def do_cd(self,command):    #cd命令
        path=command.split()[1]     #获取路径
        os.chdir(path)  #改变当前工作路径为path
        self.path=os.getcwd()
        self.send_train(self.path.encode('utf8'))   #将当前路径传递给客户验证是否cd成功


    def do_pwd(self):   #pwd命令
        '''
        显示当前工作目录
        :return:
        '''
        self.send_train(self.path.encode('utf8'))

    def do_rm(self,command):    #rm命令
        '''
        删除指定文件
        :return:
        '''
        try:
            path = command.split()[1]
            os.remove(path)
        except FileNotFoundError:
            data='ERROR: 文件不存在！'
            self.send_train(data.encode('utf8'))
        else:
            data='删除成功！'
            self.send_train(data.encode('utf8'))

    def do_gets(self,command):    #gets命令
        '''
        将指定文件传输给客户
        :return:
        '''
        file_path = command.split()[1]
        flag=os.path.exists(file_path)  #查看文件是否存在
        if flag==False: #文件不存在
            data = '1'
            self.send_train(data.encode('utf8'))
        else:   #文件存在
            data='2'
            self.send_train(data.encode('utf8'))
            fd = open(file_path, 'rb')
            file_content = fd.read()
            self.send_train(file_content)


    def do_puts(self,command):    #puts命令
        data = self.recv_train().decode('utf8')
        if data == '1':
            print('ERROR: 文件不存在！')
        else:
            file_path = command.split()[1]
            # 在当前路径下创建一个文件并打开
            fd = open(file_path, 'wb')
            file_content = self.recv_train()
            fd.write(file_content)
            result='上传成功！'
            print(result)
            self.send_train(result.encode('utf8'))

    def deal_command(self):
        while True:
            #接收客户端传来的命令
            command=self.recv_train().decode('utf8')
            if command[:2] == 'ls':  # 前两个字符为ls
                self.do_ls()
            elif command[:2] == 'cd':
                self.do_cd(command)
            elif command[:3] == 'pwd':
                self.do_pwd()
            elif command[:2] == 'rm':
                self.do_rm(command)
            elif command[:4] == 'gets':
                self.do_gets(command)
            elif command[:4] == 'puts':
                self.do_puts(command)
            else:
                print('wrong command!')

    def send_train(self,send_bytes):
        train_head_bytes=struct.pack('I',len(send_bytes))
        self.new_client.send(train_head_bytes+send_bytes)

    def recv_train(self):
        train_head_bytes = self.new_client.recv(4)  # 接收文件名长度
        train_head = struct.unpack('I', train_head_bytes)
        return self.new_client.recv(train_head[0])  # 接收文件名


if __name__ == '__main__':
    myserver=Server('',6666)
    myserver.tcp_init()
    myserver.task()

