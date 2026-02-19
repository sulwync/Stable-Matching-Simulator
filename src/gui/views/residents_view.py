from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.widgets.scrollframe import ScrollFrame
from gui.widgets.placeholder_entry import PlaceholderEntry

DEGREE_OPTIONS = ["Undergraduate", "Postgraduate"]


class ResidentsView(ttk.LabelFrame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, text="Residents", padding=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._is_auto = False

        self.scroll = ScrollFrame(self)
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.inner.grid_columnconfigure(0, weight=1)

        self.btn_add = ttk.Button(self, text="Add More Resident", command=self.add_resident)
        self.btn_add.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self._rows: list[dict] = []
        self.add_resident()
        self.add_resident()

        self.set_auto_mode(False)

    def set_auto_mode(self, is_auto: bool) -> None:
        self._is_auto = is_auto
        for row in self._rows:
            self._apply_mode_to_row(row, is_auto)

    def add_resident(self) -> None:
        idx = len(self._rows) + 1

        box = ttk.LabelFrame(self.scroll.inner, text=f"Resident {idx}", padding=10)
        box.grid(row=idx - 1, column=0, sticky="ew", pady=(0, 10), padx=(0, 10))
        box.grid_columnconfigure(0, weight=1)

        top = ttk.Frame(box)
        top.grid(row=0, column=0, columnspan=4, sticky="w")

        gpa_label = ttk.Label(top, text="GPA")
        gpa_label.pack(side="left")

        gpa = tk.Entry(top, width=6, relief="solid", bd=1)
        gpa.pack(side="left", padx=(6, 12))

        deg = ttk.Combobox(top, values=DEGREE_OPTIONS, state="readonly", width=14)
        deg.set("Degree Type")
        deg.pack(side="left")

        # Resident preference (exists in both modes)
        pref = PlaceholderEntry(box, "Preference (e.g. H1, H3, H2)", relief="solid", bd=1)
        pref.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        row = {
            "box": box,
            "top": top,
            "gpa": gpa,
            "gpa_label": gpa_label,
            "deg": deg,
            "pref": pref,
        }

        self._rows.append(row)

        self._apply_mode_to_row(row, self._is_auto)

    def _apply_mode_to_row(self, row: dict, is_auto: bool) -> None:
        if is_auto:
            row["top"].grid()
        else:
            row["top"].grid_remove()

    def reset(self) -> None:
        for row in self._rows:
            row["box"].destroy()
        self._rows.clear()
        self.add_resident()
        self.add_resident()
        self.set_auto_mode(False)
