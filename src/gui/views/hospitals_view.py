from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.widgets.scrollframe import ScrollFrame
from gui.widgets.placeholder_entry import PlaceholderEntry


DEGREE_OPTIONS = ["Undergraduate", "Postgraduate"]

def add_placeholder(entry: tk.Entry, text: str, *, muted="#888888", normal="#000000") -> None:
    entry.insert(0, text)
    entry.config(fg=muted)

    def on_focus_in(_):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(fg=normal)

    def on_focus_out(_):
        if not entry.get().strip():
            entry.insert(0, text)
            entry.config(fg=muted)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


class HospitalsView(ttk.LabelFrame):
    def __init__(self, master: tk.Misc, on_mode_change: Optional[Callable[[bool], None]] = None):
        super().__init__(master, text="Hospitals", padding=10)

        self._on_mode_change = on_mode_change
        self._is_auto = tk.BooleanVar(value=False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top.grid_columnconfigure(0, weight=1)

        ttk.Checkbutton(
            top,
            text="Auto Generate Preference",
            variable=self._is_auto,
            command=self._toggle_mode,
        ).pack(side="left")

        self.scroll = ScrollFrame(self)
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.inner.grid_columnconfigure(0, weight=1)

        self.btn_add = ttk.Button(self, text="Add More Hospital", command=self.add_hospital)
        self.btn_add.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        self._rows: list[dict] = []

        # start with 2 like your mock
        self.add_hospital()
        self.add_hospital()

        # apply initial mode
        self.set_auto_mode(self._is_auto.get())

    def _toggle_mode(self) -> None:
        is_auto = self._is_auto.get()
        self.set_auto_mode(is_auto)
        if self._on_mode_change:
            self._on_mode_change(is_auto)

    def set_auto_mode(self, is_auto: bool) -> None:
        # Update existing rows to show/hide correct fields
        for row in self._rows:
            self._apply_mode_to_row(row, is_auto)

    def add_hospital(self) -> None:
        idx = len(self._rows) + 1

        box = ttk.LabelFrame(self.scroll.inner, text=f"Hospital {idx}", padding=10)
        box.grid(row=idx - 1, column=0, sticky="ew", pady=(0, 10), padx=(0, 10))
        box.grid_columnconfigure(1, weight=1)

        # Capacity
        cap_label = ttk.Label(box, text="Capacity")
        cap_label.grid(row=0, column=0, sticky="w")

        cap = tk.Entry(box, width=10, relief="solid", bd=1)
        cap.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Manual-only: hospital preference entry
        manual_pref = PlaceholderEntry(box, "Preference (e.g. R1, R3, R2)", relief="solid", bd=1)
        manual_pref.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        # Auto-only: preferred degree type dropdown
        pref_deg = ttk.Combobox(box, values=DEGREE_OPTIONS, state="readonly")
        pref_deg.set("Preferred Degree Type")
        pref_deg.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        # Auto-only: generated hospital preference (display)
        auto_gen = tk.Entry(box, relief="solid", bd=1)
        auto_gen.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        auto_gen.insert(0, "Generated Preference (auto)")
        auto_gen.configure(state="disabled")

        row = {
            "box": box,
            "cap_label": cap_label,
            "cap": cap,
            "manual_pref": manual_pref,
            "pref_deg": pref_deg,
            "auto_gen": auto_gen,
        }

        self._rows.append(row)

        self._apply_mode_to_row(row, self._is_auto.get())

    def _apply_mode_to_row(self, row: dict, is_auto: bool) -> None:
        row["cap_label"].grid()
        row["cap"].grid()

        if is_auto:
            row["manual_pref"].grid_remove()
            row["pref_deg"].grid()
            row["auto_gen"].grid()
        else:
            row["pref_deg"].grid_remove()
            row["auto_gen"].grid_remove()
            row["manual_pref"].grid()


    def reset(self) -> None:
        for row in self._rows:
            row["box"].destroy()
        self._rows.clear()
        self._is_auto.set(False)
        self.add_hospital()
        self.add_hospital()
        self.set_auto_mode(False)
