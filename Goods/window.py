import tkinter as tk
from tkinter import Listbox, filedialog, END, ACTIVE
import datetime
import os
window = tk.Tk()
window.title("建档工具")
window.geometry("731x480")
scroll = tk.Scrollbar(window)
text = tk.Text(window, width=100, height=15)
curfile = os.getcwd()


def insert(func):
    def inner(*args, **kwargs):
        text.insert('end', f'{datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S: ")}')
        func(*args, **kwargs)
        text.see(END)
    return inner


text.insert_end_line = insert(text.insert)


