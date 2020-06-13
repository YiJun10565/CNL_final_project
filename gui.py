import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.scrolledtext as tst
import tkinter.filedialog as fd
from PIL import ImageTk, Image
#import recorder
import threading
#import pyaudio
import wave
import argparse
import client
import re

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('300x500')
        self.title('CNL Walkie-Talkie')
        self.resizable(0, 0)
        self._frame = None
        self.switch_frame(StartPage)

        # socket init
        self.client = client.build_connection(args)
        send_data = "New"
        send_raw_data = send_data.encode('utf-8')
        self.client.connect.sendall(send_raw_data)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        # GUI is master
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.bg_color = 'DeepSkyBlue2'
        self.master.configure(bg = self.bg_color)
        self.configure(bg = self.bg_color)  

        tk.Label(self, bg = self.bg_color).grid(row = 0, column = 0, columnspan=4, rowspan = 1, pady = 2)
        tk.Label(self, text="CNL", font=('Helvetica', 42, "bold"), bg = self.bg_color).grid(row = 1, column = 0, columnspan=4, rowspan = 2)
        tk.Label(self, text="Walkie-Talkie", font=('Helvetica', 24, "bold"), bg = self.bg_color).grid(row = 4, columnspan=4, rowspan = 2) 
        tk.Label(self, bg = self.bg_color).grid(row = 6, column = 0, columnspan=4, rowspan = 1, pady = 0)       

        # username
        self.username = tk.StringVar()
        tk.Label(self, text="--- Username ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 8, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.username).grid(row = 10, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 11, column = 0, columnspan=4, rowspan = 2)

        # password
        self.password = tk.StringVar()
        tk.Label(self, text="--- Password ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 12, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.password).grid(row = 14, columnspan=4, pady = 5)


        tk.Label(self, bg = self.bg_color).grid(row = 15, column = 0, columnspan=4, rowspan = 1, pady = 5)

        # login
        tk.Button(self, text="Login", font=('Helvetica', 12, "bold"), width = 16, command=self.login).grid(row = 16, column = 0, columnspan=4, pady = 10)

        # reigster
        tk.Button(self, text="Register", font=('Helvetica', 12, "bold"), width = 16, command=lambda: master.switch_frame(RegisterPage)).grid(row = 17, column = 0, columnspan=4, pady = 5)

    def login(self):
        usrname = self.username.get()
        passwd = self.password.get()
        print("self.username.get():", usrname)
        print("self.password.get():", passwd)
        if(not re.match("^[A-Za-z0-9_]+$", usrname) or not re.match("^[A-Za-z0-9_]+$", passwd)):
            popup = tk.Tk()
            popup.wm_title("Error")
            label = ttk.Label(popup, text="Username or Password contains invalid characters.\n         (letters, numbers and underscores only.)", font=('Helvetica'))
            label.pack(side="top", fill="x", pady=20)
            B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
            B1.pack()
            popup.mainloop()
        else:
            if client.Login(self.master.client, usrname, passwd):
                self.master.client.state = States.waiting_for_talk
                self.master.switch_frame(MainPage)
            else:
                popup = tk.Tk()
                popup.wm_title("Error")
                label = ttk.Label(popup, text="Wrong Username or Password", font=('Helvetica'))
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
                B1.pack()
                popup.mainloop()


class RegisterPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.bg_color = 'DeepSkyBlue2'
        self.master.configure(bg = self.bg_color)
        self.configure(bg = self.bg_color)

        tk.Label(self, bg = self.bg_color).grid(row = 0, column = 0, columnspan=4, rowspan = 1, pady = 0) 
        tk.Label(self, text="Please enter", font=('Helvetica', 16, "bold"), bg = self.bg_color).grid(row = 2, columnspan=4, rowspan = 1) 
        tk.Label(self, text="following informations.", font=('Helvetica', 16, "bold"), bg = self.bg_color).grid(row = 3, columnspan=4, rowspan = 1) 
        tk.Label(self, bg = self.bg_color).grid(row = 4, column = 0, columnspan=4, rowspan = 1, pady = 1)     

        # username
        self.username = tk.StringVar()
        tk.Label(self, text="--- Username ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 5, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.username).grid(row = 7, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 8, column = 0, columnspan=4, rowspan = 2)

        # password
        self.password = tk.StringVar()
        tk.Label(self, text="--- Password ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 9, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.password).grid(row = 11, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 12, column = 0, columnspan=4, rowspan = 2)

        # password again
        self.password_confirm = tk.StringVar()
        tk.Label(self, text="--- Password Again ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 13, columnspan=4, pady = 5)
        tk.Entry(self, textvariable=self.password_confirm).grid(row = 15, columnspan=4, pady = 5)

        tk.Label(self, bg = self.bg_color).grid(row = 16, column = 0, columnspan=4, rowspan = 1, pady = 2)

        # reigster
        tk.Button(self, text="Register", font=('Helvetica', 12, "bold"), width = 16, command=self.reigster).grid(row = 17, column = 0, columnspan=4, pady = 5)

        # Back to login
        tk.Button(self, text="Back", font=('Helvetica', 12, "bold"), width = 16, command=lambda: master.switch_frame(StartPage)).grid(row = 18, column = 0, columnspan=4, pady = 10)


    def reigster(self):
        usrname = self.username.get()
        passwd = self.password.get()
        password_confirm = self.password_confirm.get()
        print("self.username.get():", usrname)
        print("self.password.get():", passwd)
        print("self.password_confirm.get():", password_confirm)

        if passwd != password_confirm:
            popup = tk.Tk()
            popup.wm_title("Error")
            label = ttk.Label(popup, text="Passwords are not same, please enter again.", font=('Helvetica'))
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
            B1.pack()
            popup.mainloop()
        elif(not re.match("^[A-Za-z0-9_]+$", usrname) or not re.match("^[A-Za-z0-9_]+$", passwd)):
            popup = tk.Tk()
            popup.wm_title("Error")
            label = ttk.Label(popup, text="Username or Password contains invalid characters.\n(letters, numbers and underscores only.)", font=('Helvetica'), anchor='center', justify = 'center')
            label.pack(side="top", fill="x", pady=20)
            B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
            B1.pack()
            popup.mainloop()
        else:
            if client.Sign_up(self.master.client, usrname, passwd, password_confirm):
                popup = tk.Tk()
                popup.wm_title("Congratulations!") 
                label = ttk.Label(popup, text="Your registration has completed.\nWelcome!", font=('Helvetica'), anchor='center', justify = 'center')
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Login now", command = popup.destroy)
                B1.pack()
                self.master.switch_frame(StartPage)
            else:
                popup = tk.Tk()
                popup.wm_title("Sorry")
                label = ttk.Label(popup, text="The account has been used.", font=('Helvetica'))
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Try again", command = popup.destroy)
                B1.pack()
                popup.mainloop()



class MainPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.running = None
        self.click = False
        self.bg_color = 'DeepSkyBlue2'
        self.configure(bg = self.bg_color) 
        tk.Label(self, bg = self.bg_color).grid(row = 0, rowspan = 1, pady = 5)
        tk.Label(self, text="Walkie-Talkie", font=('Helvetica', 24, "bold"), bg = self.bg_color).grid(row = 1, pady = 5)
        self.photo = ImageTk.PhotoImage(file = "record.png")
        self.record_button = tk.Button(self, text="record!", image = self.photo, bg = self.bg_color)
        self.record_button.grid(row = 2, pady = 5)
        
        self.record_button.bind('<ButtonPress-1>', lambda event: self.create_recording_thread())#self.start_recording())
        self.record_button.bind('<ButtonRelease-1>', lambda event: self.stop_recording())
        self.logout_button = tk.Button(self, text="logout", command=self.logout)
        self.logout_button.grid(row = 3, pady = 20)

        self.audio_socket = client.build_connection(args)
        send_data = self.master.client.username
        send_raw_data = send_data.encode('utf-8')
        self.audio_socket.connect.sendall(send_raw_data)
        self.recv_sound = thread_recv_sound(self.audio_socket.connect)
        self.recv_sound.run()

    def logout(self):
        client.logout(self.master.client)
        self.master.switch_frame(StartPage)

    def create_recording_thread(self):
        self.thread_recording = threading.Thread(target = self.start_recording)
        self.thread_recording.setDaemon(True)
        self.thread_recording.start()
    '''
    def start_recording(self):        
        print('start recording', flush=True)
        self.click = True
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        fs = 44100  # Record at 44100 samples per second
        # filename = "record/output.wav"

        p = pyaudio.PyAudio()  # Create an interface to PortAudio
        stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        while self.click:
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()
        # index = 0
        # while self.click:
            
        #     #for i in range(100):
        #     self.running = recorder.Recorder(channels=1).record(0.1, output='record/{:03d}.wav'.format(index))
        #     # print('-----recording-----', flush=True)
            
        #     #for i in range(100):
            
        #     # print('-----playing-----', flush=True)
        #     index += 1
        k = 32
        for i in range(len(frames)//k):
            wf = wave.open('record/{:03d}.wav'.format(i), 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames[i*k:i*k+k]))
            wf.close()
        print('-------playing-------', flush=True)
        #for i in range(len(frames)//k):
        #    recorder.Recorder.play('record/{:03d}.wav'.format(i))
        print('-----end playing-----', flush=True)

    def stop_recording(self):
        print('stop recording', flush=True)
        self.click = False
        self.thread_recording.join()

        # if self.running != None:
        #     self.running.close()
        #     self.running = None
'''
# main 
if __name__ == '__main__':
    # window = tk.Tk()
    # window.title('CNL Walkie-Talkie')
    # window.geometry('300x500')
    # window.resizable(0, 0)
    parser = argparse.ArgumentParser()
    parser.add_argument("IP", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="port of the IP")
    global args
    args = parser.parse_args()

    app = GUI()
    app.mainloop()
