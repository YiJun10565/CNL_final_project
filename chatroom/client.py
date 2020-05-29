import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.scrolledtext as tst
import tkinter.filedialog as fd
import threading
import time
import socket
import hashlib
import json
import ctypes
import inspect
import os

host = "127.0.0.1"  # The server's hostname or IP address
port = 9487          # The port used by the server



def rcv_pkt(sd):
    data = sd.recv(32)
    if len(data) == 0:
        return False

    read_len = int(data.decode(), 2)
    data_rcv = ''
    #time.sleep(0.01)
    #print(read_len)
    while len(data_rcv) < read_len:
        data_rcv += sd.recv(1024).decode()
    #print(data_rcv)
    return data_rcv

def build_connection(name, case):
    sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sd.settimeout(None)
    sd.connect((host, port))
# shake hands
    tmp = "{}\n{}".format(name, case)
    sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
    ack = sd.recv(1).decode()
    #print(ack)
    if ack == '1':
        return sd
    else:
        return None


class Application(object):
    def __init__(self, master):
        self.master = master
        self.App_frame = tk.Frame(master, bg = '#ffffff')
        self.App_frame.place(x = 0, y = 0, width = 800, height = 600)
        ####################################測試用資料庫(實測時必須刪除掉)##########################################                                  		
        self.users = dict({})
        #self.users = {'ko870903': {'state': 'offline'}, # password is ko880816
        #                'joe0123': {'state': 'offline'}, # password is 94879487
        #                'sam880222': {'state': 'offline'}} # password is password
        self.dataset = dict({})
        #self.dataset = {'ko870903': {'seen': 2, 'messages': [('ko870903', '2020-01-01 01:01', '哈囉'), ('ko870903', '2020-01-01 01:10', '你好帥')]}, 'joe0123': {'seen': 2, 'messages': [('joe0123', '2019-12-25 00:08', '聖誕節快樂'), ('ko870903', '2020-01-01 00:01', '新年快樂')]}, 'sam880222': {'seen': 1, 'messages': [('ko870903', '2020-01-03 03:08', '計網作業'), ('sam880222', '2020-01-10 19:20', '放寒假')]}}
		#########################################################################################################

        self.exit = True
        self.UserList(self.App_frame, 600, 0, 200, 600)
        self.HistoryMessage(self.App_frame, 0, 0, 600, 400) 
        self.DataSend(self.App_frame, 0, 400, 600, 160)
        self.Control(self.App_frame, self.users, 0, 550, 600, 50)

        self.my_state = 'offline'
        self.my_name = 'unknown'
        self.your_name = 'unknown'
        self.mes_load = False
        self.UserList_change = 0
        self.HistoryMessage_change = 0
        self.DataSend_change = 0
        self.Control_change = 0
        self.sd_threads = []
        master.protocol("WM_DELETE_WINDOW", self.Control_Quit)
        
        self.user_sd = build_connection(self.my_name, "in")
        thread = threading.Thread(target = self.Update)
        thread.setDaemon(True)
        thread.start()

    def UserList(self, frame, pos_x, pos_y, size_x, size_y):
        self.UserList_frame = tk.Frame(frame, bg = '#aacccc')
        self.UserList_frame.place(x = pos_x, y = pos_y, width = size_x, height = size_y)
        
        self.UserList_title_label = tk.Label(self.UserList_frame, text = '全部用戶', bg = '#aaccaa')
        self.UserList_title_label.place(x = 0, y = 0, width = size_x, height = 20)

    def HistoryMessage(self, frame, pos_x, pos_y, size_x, size_y):
        self.HistoryMessage_frame = tk.Frame(frame, bg = '#a0c7db')
        self.HistoryMessage_frame.place(x = pos_x, y = pos_y, width = size_x, height = size_y)

        self.HistoryMessage_title_label = tk.Label(self.HistoryMessage_frame, text = '過去訊息', bg = '#579ec1')
        self.HistoryMessage_title_label.place(x = 0, y = 0, width = size_x, height = 20)

        self.HistoryMessage_message = tst.ScrolledText(self.HistoryMessage_frame, bg = '#a0c7db')
        self.HistoryMessage_message.place(x = 0, y = 20, width = size_x, height = 380)
        self.HistoryMessage_message.config(state = 'disabled')

    def DataSend(self, frame, pos_x, pos_y, size_x, size_y):
        self.DataSend_frame = tk.Frame(frame, bg = '#f0f0f0')
        self.DataSend_frame.place(x = pos_x, y = pos_y, width = size_x, height = size_y)

        self.DataSend_title_label = tk.Label(self.DataSend_frame, text = '訊息輸入', bg = '#cccccc')
        self.DataSend_title_label.place(x = 0, y = 0, width = size_x, height = 20)

        self.DataSend_input = tst.ScrolledText(self.DataSend_frame)
        self.DataSend_input.place(x = 0, y = 20, width = size_x - 60, height = 80)

        self.DataSend_send_message_button = tk.Button(self.DataSend_frame, text = '送出訊息', bg = '#ffffff', command = self.send_message)
        self.DataSend_send_message_button.place(x = 540, y = 20, width = 60, height = 80)

        self.DataSend_recv_file = tk.Text(self.DataSend_frame, bg = '#dddddd')
        self.DataSend_recv_file.place(x = 300, y = 100, width = size_x - 360, height = 50)
        self.DataSend_recv_file.config(state = 'disabled')

        self.DataSend_recv_file_button = tk.Button(self.DataSend_frame, text = '下載檔案', bg = '#ffffff', command = self.recv_file)
        self.DataSend_recv_file_button.place(x = 540, y = 100, width = 60, height = 50)

        self.DataSend_send_file = tk.Text(self.DataSend_frame)
        self.DataSend_send_file.place(x = 0, y = 100, width = size_x - 360, height = 50)
        self.DataSend_send_file.config(state = 'disabled')

        self.DataSend_select_file_button = tk.Button(self.DataSend_frame, text = '選擇檔案', bg = '#ffffff', command = self.select_file)
        self.DataSend_select_file_button.place(x = 240, y = 100, width = 60, height = 25)

        self.DataSend_send_file_button = tk.Button(self.DataSend_frame, text = '上傳檔案', bg = '#ffffff', command = self.send_file)
        self.DataSend_send_file_button.place(x = 240, y = 125, width = 60, height = 25)
# TODO
    def user_recv(self):
        try:
            while not self.exit:
                if self.UserList_change == 0:
                    data_rcv = rcv_pkt(self.user_sd)
                    if data_rcv == False:
                       continue
                    '''pkt_len = int(self.user_sd.recv(32).decode(), 2)
                    data_rcv = ''
                    while len(data_rcv) < pkt_len:
                        data_rcv += self.user_sd.recv(1024).decode()'''
                    self.users = json.loads(data_rcv)
                    #print(self.users, flush=True)
                    #print(data_rcv)
                    self.UserList_change = 1
        except:
            #print("QQQQQ")
            exit()
        #print("QQQQQ")
                

# TODO
    def msg_recv(self):
        try:
            while not self.exit:
                if self.HistoryMessage_change == 0:
                    if self.mes_load:
                        data_rcv = rcv_pkt(self.mrcv_sd)
                        if data_rcv == False:
                            continue
                        tmp = data_rcv.split('\n')
                        whose = tmp[0]
                        if self.dataset.get(whose) == None:
                            self.dataset[whose] = dict({'seen': 0, 'messages': [], 'files':[]})
                        else:
                            self.dataset[whose]['messages'].append(json.loads('\n'.join(tmp[1:])))
                        self.mes_load = True
                        #print(self.dataset, flush=True)
                        self.HistoryMessage_change = 1
                        self.UserList_change = 1
                    else:
                        data_rcv = rcv_pkt(self.mrcv_sd)
                        #pkt_len = int(self.user_sd.recv(32), 2)
                        #self.dataset = self.mrcv_sd.recv(pkt_len).decode()
                        self.dataset = json.loads(data_rcv)
                        self.mes_load = True
                        #print(self.dataset, flush=True)
                        self.HistoryMessage_change = 1
                        self.UserList_change = 1
        except:
            #print("QQQQQ")
            exit()
        #print("QQQQQ")

# TODO
    def send_message(self):
        if (self.my_state == 'online' and self.your_name != 'unknown'):
            my_message = self.DataSend_input.get('1.0', 'end-1c')
            self.dataset[self.your_name]['seen'] += 1
            tmp = "{}\n{}".format(self.your_name, json.dumps(my_message))
            self.msnd_sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())

            self.DataSend_input.delete(0.0, tk.END)
        elif (self.my_state == 'offline'):
            tk.messagebox.showinfo(title = '建議', message = '請先登入你的帳戶')
        elif (self.your_name == 'unknown'):
            tk.messagebox.showinfo(title = '建議', message = '請選擇聊天的對象')


# TODO
    def notice_file(self):
        try:
            while not self.exit:
                if self.HistoryMessage_change == 0 and self.DataSend_change == 0 and self.UserList_change == 0:
                    data_rcv = rcv_pkt(self.frcv_sd)
                    if data_rcv == False:
                        continue
                    tmp = data_rcv.split('\n')
                    #print(tmp)
                    whose = tmp[0]
                    if self.dataset.get(whose) == None:
                        self.dataset[whose] = dict({'seen': 0, 'messages': [], 'files':[]})
                    else:
                        self.dataset[whose]['messages'].append(json.loads(tmp[1]))
                        self.dataset[whose]['files'].append(json.loads(tmp[2]))
                    self.mes_load = True
                    #print(self.dataset, flush=True)
                    self.HistoryMessage_change = 1
                    self.DataSend_change = 1
                    self.UserList_change = 1
        except:
            #print("QQQQQ")
            exit()

# TODO
    def downloading_file(self, file_msg, dir_path):
        sd = build_connection(self.my_name, "f_down")
        tmp = "{}\n{}".format(file_msg[0], json.dumps(file_msg[1]))
        sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
        with open(os.path.join(dir_path, file_msg[1]), "wb") as f:
            data = sd.recv(1024)
            while len(data) > 0:
                f.write(data)
                data = sd.recv(1024)
        sd.shutdown(2)
        sd.close()
        print("download done!", flush=True)

    def downloading_files(self, Vars, num_file, dir_path):
        for i in range(num_file):
            if (Vars[i].get() == 1):
                thread = threading.Thread(target = self.downloading_file, args=(self.dataset[self.your_name]['files'][i], dir_path, ))
                thread.setDaemon(True)
                thread.start()

    def recv_file(self):
        if (self.my_state == 'offline' or self.your_name == 'unknown'):
            return

        dir_path = fd.askdirectory()
        window_recv_file = tk.Toplevel(self.master)
        window_recv_file.title('下載檔案')
        window_recv_file.geometry('300x500')

        self.recv_file_title_label = tk.Label(window_recv_file, text = '選擇要下載的檔案', bg = '#cccccc')
        self.recv_file_title_label.place(x = 0, y = 0, width = 300, height = 20)

        Vars = []
        num_file = min(20, len(self.dataset[self.your_name]['files']))
        for i in range(num_file):
            Vars.append(tk.IntVar()) 
            t = '(' + self.dataset[self.your_name]['files'][i][0] + ') ' + self.dataset[self.your_name]['files'][i][1] 
            c = tk.Checkbutton(window_recv_file, text = t, variable = Vars[i], onvalue = 1, offvalue = 0)
            c.place(x = 0, y = 20 + i * 20, width = 300, height = 20)

        downloading_button = tk.Button(window_recv_file, text = '下載', command = lambda: self.downloading_files(Vars, num_file, dir_path))
        downloading_button.place(x = 132, y = 20 + num_file * 20, width = 36, height = 25)

# TODO
    def uploading_file(self, filepath, filename):
        sd = build_connection(self.my_name, "f_up")
        tmp = "{}\n{}".format(self.your_name, json.dumps(filename))
        sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
        ack = sd.recv(1)
        with open(filepath, "rb") as f:
            data = f.read(1024)                       
            while len(data) > 0:
                sd.sendall(data)
                data = f.read(1024)
        sd.shutdown(1)
        self.dataset[self.your_name]['seen'] += 1
        ack = sd.recv(1).decode()
        if ack == '1':
            sd.shutdown(2)
            sd.close()
        #TODO else


    def select_file(self):
        self.files = fd.askopenfilenames()
        
        self.DataSend_send_file.config(state = 'normal')
        self.DataSend_send_file.delete(0.0, tk.END)
        for file_name in self.files:
            self.DataSend_send_file.insert(tk.INSERT, file_name + '\n')
        self.DataSend_send_file.see(tk.END)
        self.DataSend_send_file.config(state = 'disabled')
        #print(self.files, flush=True)


# TODO
    def send_file(self):
        if (self.my_state == 'online' and self.your_name != 'unknown'):
            self.DataSend_send_file.config(state = 'normal')
            self.DataSend_send_file.delete(0.0, tk.END)
            self.DataSend_send_file.see(tk.END)
            self.DataSend_send_file.config(state = 'disabled')

            for filepath in self.files:
                #print(filepath, flush=True)
                thread = threading.Thread(target = self.uploading_file, args=(filepath, filepath.split('/')[-1], ))
                thread.setDaemon(True)
                thread.start()



    def Control(self, frame, users, pos_x, pos_y, size_x, size_y):
        self.Control_frame = tk.Frame(frame, bg = '#f0f0f0')
        self.Control_frame.place(x = pos_x, y = pos_y, width = size_x, height = size_y)

        #self.Control_quit_button = tk.Button(self.Control_frame, text = '離開', bg = '#ffffff', command = self.Control_Quit)
        #self.Control_quit_button.place(x = 546, y = 12, width = 36, height = 25)

        self.Control_login_button = tk.Button(self.Control_frame, text = '登入', bg = '#ffffff', command = self.Control_Login)
        self.Control_login_button.place(x = 20, y = 12, width = 36, height = 25)
        
        self.Control_sign_up_button = tk.Button(self.Control_frame, text = '註冊', bg = '#ffffff', command = self.Control_SignUp)
        self.Control_sign_up_button.place(x = 76, y = 12, width = 36, height = 25)


# TODO
    def Control_Quit(self):
        #if self.exit == True:
        #    if hasattr(self, "user_sd"):
        #        self.user_sd.shutdown(2)
        #        self.user_sd.close()
        #    exit(0)
        self.exit = True
        if len(self.sd_threads) != 0:
            tmp = []
            for whose in self.dataset:
                tmp.append([whose, self.dataset[whose]['seen']])
            #print(tmp)
            tmp = json.dumps(tmp)
            self.user_sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
            self.sd_threads[0].join()

        if hasattr(self, "user_sd"):
            self.user_sd.shutdown(2)
            self.user_sd.close()
            del self.user_sd
        
        if hasattr(self, "mrcv_sd"):
            self.mrcv_sd.shutdown(2)
            self.mrcv_sd.close()
            del self.mrcv_sd
        
        if hasattr(self, "msnd_sd"):
            self.msnd_sd.shutdown(2)
            self.msnd_sd.close()
            del self.msnd_sd
        
        if hasattr(self, "frcv_sd"):
            self.frcv_sd.shutdown(2)
            self.frcv_sd.close()
            del self.frcv_sd
        
        #print("EEEEEEE", flush=True)

        exit(0)

# TODO
    def Control_CheckLogin(self, window, name, pswd):
        c_name = name.get()
        c_pswd = pswd.get()
        m = hashlib.md5()
        m.update(c_pswd.encode("utf-8"))
        result = ''
        
        if self.my_state == 'online':
            result = '已登入請關閉視窗'
        elif c_name == '':
            result = '請輸入你的帳號'
        elif c_pswd == '':
            result = '請輸入你的密碼'
        else:
            tmp = "{}\n{}".format(c_name, str(m.hexdigest()))
            self.user_sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
            ans = self.user_sd.recv(1).decode()
            if ans == "u":
                result = '不存在此用戶   '
            elif ans == "p":
                result = '密碼輸入錯誤   '
            else:
                result = '您已成功登入   '
                self.my_name = c_name
                self.my_state = 'online'
                self.master.title('BoTalk(' + self.my_name + ')')
                self.Control_change = 1
                
                self.exit = False
                thread = threading.Thread(target = self.user_recv)
                self.sd_threads.append(thread)
                thread.setDaemon(True)
                thread.start()

                self.mrcv_sd = build_connection(self.my_name, "mrcv")
                thread = threading.Thread(target = self.msg_recv)
                self.sd_threads.append(thread)
                thread.setDaemon(True)
                thread.start()

                self.msnd_sd = build_connection(self.my_name, "msnd")

                self.frcv_sd = build_connection(self.my_name, "frcv")
                thread = threading.Thread(target = self.notice_file)
                self.sd_threads.append(thread)
                thread.setDaemon(True)
                thread.start()


        result_label = tk.Label(window, text = result)
        result_label.place(x = 60, y = 110)

    def Control_Login(self):
        window_Login = tk.Toplevel(self.master)
        window_Login.title('Login')
        window_Login.geometry('240x160')

        title_label = tk.Label(window_Login, text = '請輸入你的帳號和密碼')
        title_label.place(x = 20, y = 20)
        name_label = tk.Label(window_Login, text = '帳號：')
        name_label.place(x = 20, y = 50)
        name = tk.StringVar()
        name_entry = tk.Entry(window_Login, show = None, textvariable = name)
        name_entry.place(x = 60, y = 50)
        pswd_label = tk.Label(window_Login, text = '密碼：')
        pswd_label.place(x = 20, y = 80)
        pswd = tk.StringVar()
        pswd_entry = tk.Entry(window_Login, show = '*', textvariable = pswd)
        pswd_entry.place(x = 60, y = 80)
        
        button = tk.Button(window_Login, text = '登入', bg = '#ffffff', command = lambda: self.Control_CheckLogin(window_Login, name, pswd))
        button.place(x = 20, y = 110)

# TODO
    def Control_CheckSignUp(self, window, name, pswd):
        c_name = name.get()
        c_pswd = pswd.get()
        result = ''
        m = hashlib.md5()
        m.update(c_pswd.encode("utf-8"))
        result = ''
        if len(c_name) < 6:
            result = '請註冊6個字以上的帳號'
        elif len(c_pswd) < 6:
            result = '請註冊6個字以上的密碼'
        else:
            sd = build_connection(self.my_name, "up")
            tmp = "{}\n{}".format(c_name, str(m.hexdigest()))
            sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
            ans = sd.recv(1).decode()
            if ans == "u":
                result = '此用戶已存在                   '
            else:
                result = '您已成功註冊                   '
            sd.shutdown(0)
            sd.close()

        result_label = tk.Label(window, text = result)
        result_label.place(x = 60, y = 110)

    def Control_SignUp(self):
        window_sign_up = tk.Toplevel(self.master)
        window_sign_up.title('Sign Up')
        window_sign_up.geometry('240x160')

        title_label = tk.Label(window_sign_up, text = '請註冊你的帳號和密碼')
        title_label.place(x = 20, y = 20)
        name_label = tk.Label(window_sign_up, text = '帳號：')
        name_label.place(x = 20, y = 50)
        name = tk.StringVar()
        name_entry = tk.Entry(window_sign_up, show = None, textvariable = name)
        name_entry.place(x = 60, y = 50)
        pswd_label = tk.Label(window_sign_up, text = '密碼：')
        pswd_label.place(x = 20, y = 80)
        pswd = tk.StringVar()
        pswd_entry = tk.Entry(window_sign_up, show = '*', textvariable = pswd)
        pswd_entry.place(x = 60, y = 80)

        button = tk.Button(window_sign_up, text = '註冊', bg = '#ffffff', command = lambda: self.Control_CheckSignUp(window_sign_up, name, pswd))
        button.place(x = 20, y = 110)

    def Update(self):
        while True:
            ####################################測試用程式碼(實測時必須刪除掉)##########################################
            if (self.UserList_change == 1 and self.mes_load):
                if (self.my_state == 'online' and self.my_name != 'unknown'):
                    count = 0
                    for user in self.users:
                        if user == self.your_name:
                            color = '#fdaa60'
                        else:
                            color = '#aacccc'
                        unseen = len(self.dataset[user]['messages']) - self.dataset[user]['seen']
                        if unseen > 0:
                            unseen = '(' + str(unseen) + ')'
                        else:
                            unseen = ''
                        if (self.users[user] == 'online'): #fdaa60
                            user_button = tk.Button(self.UserList_frame, text = user + unseen, bg = color, command = lambda name = user: self.talk(name))
                            user_button.place(x = 0, y = 20 + 20 * count, width = 200, height = 20)
                        elif (self.users[user] == 'offline'):
                            user_button = tk.Button(self.UserList_frame, text = user + unseen, bg = color, fg = '#666666', command = lambda name = user: self.talk(name))
                            user_button.place(x = 0, y = 20 + 20 * count, width = 200, height = 20)
                        count += 1
                else:
                    hidden = tk.Label(self.UserList_frame, text = '', bg = '#aacccc')
                    hidden.place(x = 0, y = 20, width = 200, height = 580)
                self.UserList_change = 0

            if (self.HistoryMessage_change == 1 and self.mes_load):
                if (self.my_state == 'online' and self.my_name != 'unknown' and self.your_name != 'unknown'):
                    self.HistoryMessage_message.config(state = 'normal')
                    self.HistoryMessage_message.delete(0.0, tk.END)
                    count = 0
                    for line in self.dataset[self.your_name]['messages']:
                        if (count == self.dataset[self.your_name]['seen']):
                            self.HistoryMessage_message.insert(tk.INSERT, '=========>以下為未讀訊息<=========\n')
                        self.HistoryMessage_message.insert(tk.INSERT, line[0] + ' (' + line[1] + ')\n' + line[2] + '\n')
                        count += 1 
                    self.HistoryMessage_message.see(tk.END)
                    self.dataset[self.your_name]['seen'] = count
                    self.HistoryMessage_message.config(state = 'disabled')
                else:
                    self.HistoryMessage_message.config(state = 'normal')
                    self.HistoryMessage_message.delete(0.0, tk.END)
                    self.HistoryMessage_message.config(state = 'disabled')
                self.HistoryMessage_change = 0
            #########################################################################################################
            if (self.DataSend_change == 1):
                self.DataSend_recv_file.config(state = 'normal')
                self.DataSend_recv_file.delete(0.0, tk.END)
                #print(len(self.dataset[self.your_name]['files']))
                for file_name in self.dataset[self.your_name]['files']:
                    self.DataSend_recv_file.insert(tk.INSERT, '(' + file_name[0] + ') ' + file_name[1] + '\n')
                self.DataSend_recv_file.see(tk.END)
                self.DataSend_recv_file.config(state = 'disabled')

                self.DataSend_change = 0

            if (self.Control_change == 1):
                self.Control_logout_button = tk.Button(self.Control_frame, text = '登出', bg = '#ffffff', command = self.Control_Logout)
                self.Control_logout_button.place(x = 20, y = 12, width = 36, height = 25)
                self.Control_change = 0

            time.sleep(0.01)

    def talk(self, name):
        if (self.my_state == 'online'):
            self.your_name = name
            self.HistoryMessage_change = 1
            time.sleep(0.01)
            self.UserList_change = 1
            self.DataSend_change = 1

    def Control_Logout(self):
        self.my_state = 'offline'
        self.my_name = 'unknown'
        self.your_name = 'unknown'        
        self.UserList_change = 0
        self.HistoryMessage_change = 0
        self.DataSend_change = 0
        hidden = tk.Label(self.UserList_frame, text = '', bg = '#aacccc')
        hidden.place(x = 0, y = 20, width = 200, height = 580)
        self.HistoryMessage_message.config(state = 'normal')
        self.HistoryMessage_message.delete(0.0, tk.END)
        self.HistoryMessage_message.config(state = 'disabled')
        self.Control_login_button = tk.Button(self.Control_frame, text = '登入', bg = '#ffffff', command = self.Control_Login)
        self.Control_login_button.place(x = 20, y = 12, width = 36, height = 25)
        self.master.title('BoTalk')
        
        self.exit = True
        if len(self.sd_threads) != 0:
            tmp = []
            for whose in self.dataset:
                tmp.append([whose, self.dataset[whose]['seen']])
            #print(tmp)
            tmp = json.dumps(tmp)
            self.user_sd.sendall(('{0:032b}'.format(len(tmp.encode())) + tmp).encode())
            self.sd_threads[0].join()
        
        if hasattr(self, "user_sd"):
            self.user_sd.shutdown(2)
            self.user_sd.close()
            del self.user_sd
        
        if hasattr(self, "mrcv_sd"):
            self.mrcv_sd.shutdown(2)
            self.mrcv_sd.close()
            del self.mrcv_sd
        
        if hasattr(self, "msnd_sd"):
            self.msnd_sd.shutdown(2)
            self.msnd_sd.close()
            del self.msnd_sd
        
        if hasattr(self, "frcv_sd"):
            self.frcv_sd.shutdown(2)
            self.frcv_sd.close()
            del self.frcv_sd

        self.sd_threads = []
        self.mes_load = False
        self.users = dict({})
        self.dataset = dict({})
        time.sleep(0.5)
        self.user_sd = build_connection(self.my_name, "in")
        
        #print("OOOOOOO", flush=True)


# main 
if __name__ == '__main__':
    window = tk.Tk()
    window.title('BoTalk')
    window.geometry('800x600')
    app = Application(master = window)
    window.mainloop()
