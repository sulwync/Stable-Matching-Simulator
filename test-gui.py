import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Gui Testing")

canvas = tk.Canvas(root, height=200, width=300, highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = ttk.Frame(canvas)

scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

def on_mousewheel_win_mac(event):
    step = -1 if event.delta > 0 else 1
    canvas.yview_scroll(step, "units")

def on_mousewheel_linux_up(event):   canvas.yview_scroll(-1, "units")
def on_mousewheel_linux_down(event): canvas.yview_scroll( 1, "units")

canvas.bind_all("<MouseWheel>", on_mousewheel_win_mac)
canvas.bind_all("<Button-4>", on_mousewheel_linux_up)
canvas.bind_all("<Button-5>", on_mousewheel_linux_down)

root.bind_class("TCombobox", "<MouseWheel>", lambda e: "break")
root.bind_class("TCombobox", "<Button-4>",  lambda e: "break")
root.bind_class("TCombobox", "<Button-5>",  lambda e: "break")

degrees = ["Undergraduate", "Postgraduate"]

for i in range(10):
    ttk.Label(scroll_frame, text=f"Resident {i+1}").grid(row=i, column=0, padx=5, pady=5, sticky="w")
    cb = ttk.Combobox(scroll_frame, values=degrees, width=18, state="readonly")
    cb.set("Select Degree")
    cb.grid(row=i, column=1, padx=5, pady=5, sticky="w")

root.mainloop()
