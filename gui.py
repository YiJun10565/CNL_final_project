import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.scrolledtext as tst
import tkinter.filedialog as fd
import recorder

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
        tk.Label(self, text="CNL", font=('Helvetica', 48, "bold")).pack(side="top", fill="x", pady=3)
        tk.Label(self, text="Walkie-Talkie", font=('Helvetica', 24, "bold")).pack(side="top", fill="x", pady=3)
        tk.Label(self, text="Username", font=('Helvetica', 12)).pack()
        tk.Entry(self).pack(side = 'left')
        self.login_button = tk.Button(self, text="login", command=lambda: master.switch_frame(MainPage))
        self.login_button.pack(side = 'right')

class MainPage(tk.Frame):
    def __init__(self, master):
        self.running = None
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self, bg='blue')
        tk.Label(self, text="Page one", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
        self.record_button = tk.Button(self, text="record!")
        self.record_button.pack()
        self.record_button.bind('<ButtonPress-1>', lambda event: self.start_recording())
        self.record_button.bind('<ButtonRelease-1>', lambda event: self.stop_recording())
        self.login_button = tk.Button(self, text="logout", command=lambda: master.switch_frame(StartPage))
        self.login_button.pack()
    def start_recording(self):
        print('start recording')
        self.running = recorder.Recorder(channels=2).record(10, output='todo.wav')

    def stop_recording(self):
        print('stop recording')
        if self.running != None:
            self.running.close()
            self.running = None

# main 
if __name__ == '__main__':
    # window = tk.Tk()
    # window.title('CNL Walkie-Talkie')
    # window.geometry('300x500')
    # window.resizable(0, 0)
    app = GUI()
    app.mainloop()