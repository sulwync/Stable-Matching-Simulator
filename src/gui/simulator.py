from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# Make sibling packages importable when running gui/app.py directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gui.controller import AppController
from gui.views.hospitals_view import HospitalsView
from gui.views.residents_view import ResidentsView
from gui.views.output_view import OutputView


class StableMatchingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Stable Matching Simulator")
        self.geometry("1100x650")
        self.minsize(980, 560)

        self.style = ttk.Style(self)
        self.controller = AppController()
        self._build_layout()

    def _build_layout(self) -> None:
        # Top title bar
        header = ttk.Frame(self, padding=(12, 10, 12, 6))
        header.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Stable Matching Simulator", font=("Segoe UI", 16, "bold"))
        title.pack(side="top")

        # Main body: 3 columns
        body = ttk.Frame(self, padding=(12, 0, 12, 10))
        body.grid(row=1, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")
        body.grid_columnconfigure(2, weight=1, uniform="col")
        body.grid_rowconfigure(0, weight=1)

        self.hospitals_view = HospitalsView(body, on_mode_change=self._on_mode_change)
        self.hospitals_view.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.residents_view = ResidentsView(body)
        self.residents_view.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        self.output_view = OutputView(body)
        self.output_view.grid(row=0, column=2, sticky="nsew")

    def _on_mode_change(self, is_auto: bool) -> None:
        self.hospitals_view.set_auto_mode(is_auto)
        self.residents_view.set_auto_mode(is_auto)
        self.output_view.set_status(f"Mode: {'Auto' if is_auto else 'Manual'}")

        # Bottom buttons
        footer = ttk.Frame(self, padding=(12, 0, 12, 12))
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        btn_row = ttk.Frame(footer)
        btn_row.grid(row=0, column=0, sticky="ew")

        ttk.Button(btn_row, text="Run Simulation", command=self._on_run).pack(side="left", padx=(0, 10))
        ttk.Button(btn_row, text="Restart", command=self._on_restart).pack(side="left")

        ttk.Button(btn_row, text="Export Dataset", command=self._on_export_dataset).pack(side="right", padx=(10, 0))
        ttk.Button(btn_row, text="Export Results", command=self._on_export_results).pack(side="right")

    def _on_run(self) -> None:
        self.output_view.set_status("Run clicked (wiring next).")

    def _on_restart(self) -> None:
        self.hospitals_view.reset()
        self.residents_view.reset()
        self.output_view.reset()

    def _on_export_dataset(self) -> None:
        self.output_view.set_status("Export dataset (later).")

    def _on_export_results(self) -> None:
        self.output_view.set_status("Export results (later).")


def main() -> None:
    app = StableMatchingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
