import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.scrolledtext as tst
import tkinter.filedialog as fd
from PIL import ImageTk, Image
import recorder
import threading
import pyaudio
import wave

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('300x500')
        self.title('CNL Walkie-Talkie')
        self.resizable(0, 0)
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.bg_color = 'DeepSkyBlue2'
        master.configure(bg = self.bg_color)
        self.configure(bg = self.bg_color)      
        tk.Label(self, bg = self.bg_color).grid(row = 0, column = 0, columnspan=4, rowspan = 1, pady = 5)
        tk.Label(self, text="CNL", font=('Helvetica', 48, "bold"), bg = self.bg_color).grid(row = 1, column = 0, columnspan=4, rowspan = 3)
        tk.Label(self, text="Walkie-Talkie", font=('Helvetica', 24, "bold"), bg = self.bg_color).grid(row = 4, columnspan=4, rowspan = 2) 
        tk.Label(self, bg = self.bg_color).grid(row = 6, column = 0, columnspan=4, rowspan = 1, pady = 0)       
        tk.Label(self, text="--- Username ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 8, columnspan=4, pady = 5)
        tk.Entry(self).grid(row = 10, columnspan=4, pady = 5)
        tk.Label(self, bg = self.bg_color).grid(row = 11, column = 0, columnspan=4, rowspan = 2)
        tk.Label(self, text="--- Password ---", font=('Helvetica', 14, "bold"), bg = self.bg_color).grid(row = 12, columnspan=4, pady = 5)
        tk.Entry(self).grid(row = 14, columnspan=4, pady = 5)
        tk.Label(self, bg = self.bg_color).grid(row = 15, column = 0, columnspan=4, rowspan = 1, pady = 0)
        tk.Button(self, text="Login", font=('Helvetica', 12, "bold"), width = 16, command=lambda: master.switch_frame(MainPage)).grid(row = 16, column = 0, columnspan=4, pady = 10)
    ### TODO ###
        tk.Button(self, text="Register", font=('Helvetica', 12, "bold"), width = 16, command=lambda: master.switch_frame(MainPage)).grid(row = 17, column = 0, columnspan=4, pady = 5)


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
        self.login_button = tk.Button(self, text="logout", command=lambda: master.switch_frame(StartPage))
        self.login_button.grid(row = 3, pady = 5)
    def create_recording_thread(self):
        self.thread_recording = threading.Thread(target = self.start_recording)
        self.thread_recording.setDaemon(True)
        self.thread_recording.start()
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
        for i in range(len(frames)//k):
            recorder.Recorder.play('record/{:03d}.wav'.format(i))
        print('-----end playing-----', flush=True)

    def stop_recording(self):
        print('stop recording', flush=True)
        self.click = False
        self.thread_recording.join()

        # if self.running != None:
        #     self.running.close()
        #     self.running = None

# main 
if __name__ == '__main__':
    # window = tk.Tk()
    # window.title('CNL Walkie-Talkie')
    # window.geometry('300x500')
    # window.resizable(0, 0)
    app = GUI()
    app.mainloop()