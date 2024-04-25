import tkinter as tk
from tkinter import scrolledtext
import threading
import queue

class GuiApplication:
    def __init__(self, master):
        self.master = master
        master.title("Network Session Manager")

        # Text widget for logs with a scrollbar
        self.log_area = scrolledtext.ScrolledText(master, width=70, height=20, state='disabled')
        self.log_area.grid(row=0, column=0, padx=10, pady=10)

        # Entry widget for commands
        self.command_entry = tk.Entry(master, width=70)
        self.command_entry.grid(row=1, column=0, sticky='ew', padx=10)
        self.command_entry.bind("<Return>", self.execute_command)

        # Queue to handle logs safely across threads
        self.log_queue = queue.Queue()
        self.update_logs()

    def log_message(self, message):
        self.log_queue.put(message)

    def update_logs(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, message + '\n')
            self.log_area.config(state='disabled')
            self.log_area.yview(tk.END)
        # Schedule the log update
        self.master.after(100, self.update_logs)

    def execute_command(self, event):
        cmd = self.command_entry.get()
        self.log_message(f"Executing command: {cmd}")
        # Add command handling logic here
        self.command_entry.delete(0, tk.END)

def run_gui():
    root = tk.Tk()
    app = GuiApplication(root)
    root.mainloop()

if __name__ == '__main__':
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()
