from __future__ import annotations

import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gui.controller import AppController
from gui.views.hospitals_view import HospitalsView
from gui.views.residents_view import ResidentsView
from gui.views.output_view import OutputView

class StableMatchingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Stable Matching Simulator")
        self.geometry("1100x560")
        self.minsize(980, 520)

        self.style = ttk.Style(self)
        self.controller = AppController()
        self._build_layout()
        self._last_run_result = None

    def _build_layout(self) -> None:
        # Root grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # Top title bar
        header = ttk.Frame(self, padding=(12, 10, 12, 6))
        header.grid(row=0, column=0, sticky="ew")

        title = ttk.Label(header, text="Stable Matching Simulator", font=("Segoe UI", 16, "bold"))
        title.pack(side="top")

        # Main body: 3 columns
        body = ttk.Frame(self, padding=(12, 0, 12, 10))
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)

        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")
        body.grid_columnconfigure(2, weight=1, uniform="col")

        self.hospitals_view = HospitalsView(body, on_mode_change=self._on_mode_change)
        self.hospitals_view.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.residents_view = ResidentsView(body)
        self.residents_view.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        self.output_view = OutputView(body)
        self.output_view.grid(row=0, column=2, sticky="nsew")

        # Footer buttons
        footer = ttk.Frame(self, padding=(12, 0, 12, 12))
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        btn_row = ttk.Frame(footer)
        btn_row.grid(row=0, column=0, sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)

        # Left group
        left = ttk.Frame(btn_row)
        left.grid(row=0, column=0, sticky="w")

        ttk.Button(left, text="Import Dataset", command=self._on_import_dataset).pack(side="left", padx=(0, 10))
        ttk.Button(left, text="Run Simulation", command=self._on_run).pack(side="left")

        # Right group
        right = ttk.Frame(btn_row)
        right.grid(row=0, column=1, sticky="e")

        ttk.Button(right, text="Restart", command=self._on_restart).pack(side="left", padx=(0, 10))
        ttk.Button(right, text="Export Dataset", command=self._on_export_dataset).pack(side="left", padx=(0, 10))
        ttk.Button(right, text="Export Results", command=self._on_export_results).pack(side="left")

    def _on_mode_change(self, is_auto: bool) -> None:
        self.hospitals_view.set_auto_mode(is_auto)
        self.residents_view.set_auto_mode(is_auto)

    def _on_run(self) -> None:
        is_auto = self.hospitals_view._is_auto.get()

        hospitals = self.hospitals_view.get_data()
        residents = self.residents_view.get_data()

        result = self.controller.run(
            is_auto=is_auto,
            hospitals=hospitals,
            residents=residents,
        )

        # Auto: display generated hospital preference in the UI
        if result.mode == "auto" and result.hosPref is not None:
            self.hospitals_view.set_generated_preferences(result.hosPref)

        # Render to OutputView
        self.output_view.render_results(
            resMatch=result.resMatch,
            hosMatch=result.hosMatch,
            unmatched_explain=result.unmatched_explain,
            stats=result.stats,
        )

        self.output_view.set_log(result.events or [])
        self._last_run_result = result

        self.output_view.set_events_json(result.events_json or [])
        self.output_view.set_visualize_handler(self._open_d3_viewer)

    def _open_d3_viewer(self, events_json: list[dict]) -> None:
        if not events_json:
            messagebox.showinfo("Visualize (D3)", "No replay events available. Run the simulation first.")
            return

        fd, path = tempfile.mkstemp(prefix="stablematch_events_", suffix=".json")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(events_json, f)

        # Ensure module resolution by running from project root
        project_root = str(Path(__file__).resolve().parents[1])
        subprocess.Popen([sys.executable, "-m", "gui.d3_viewer", path], cwd=project_root)

    def _on_import_dataset(self) -> None:
        path = filedialog.askopenfilename(
            title="Import dataset",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Import failed", f"Could not read JSON:\n{e}")
            return

        mode = (data.get("mode") or "manual").lower()
        hospitals = data.get("hospitals", [])
        residents = data.get("residents", [])

        if not hospitals or not residents:
            messagebox.showerror("Import failed", "Dataset missing hospitals or residents.")
            return

        if mode == "manual":
            self.hospitals_view.load_manual_dataset(hospitals)
            self.residents_view.load_manual_dataset(residents)

        elif mode == "auto":
            for h in hospitals:
                if "preferred_degree" not in h and "pref_degree" in h:
                    h["preferred_degree"] = h["pref_degree"]
            self.hospitals_view.load_auto_dataset(hospitals)
            self.residents_view.load_auto_dataset(residents)

        else:
            messagebox.showerror("Import failed", f"Unsupported mode: {mode}")
            return

        self.output_view.reset()

    def _on_export_dataset(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export dataset",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        def split_list(s: str) -> list[str]:
            if not s:
                return []
            return [t.strip() for t in s.replace(",", " ").split() if t.strip()]

        try:
            is_auto = self.hospitals_view._is_auto.get()
            hospitals = self.hospitals_view.get_data()
            residents = self.residents_view.get_data()

            dataset = {
                "name": "Exported Dataset",
                "mode": "auto" if is_auto else "manual",
                "hospitals": [],
                "residents": [],
            }

            # Hospitals
            for i, h in enumerate(hospitals, start=1):
                obj = {"id": f"H{i}"}

                cap_s = (h.get("capacity_str") or "").strip()
                obj["capacity"] = int(cap_s) if cap_s.isdigit() else 0

                if is_auto:
                    deg = (h.get("pref_deg_str") or "").strip()
                    if deg == "Preferred Degree Type":
                        deg = ""
                    obj["pref_degree"] = deg
                else:
                    pref_s = (h.get("manual_pref_str") or "").strip()
                    obj["preference"] = split_list(pref_s)

                dataset["hospitals"].append(obj)

            # Residents
            for i, r in enumerate(residents, start=1):
                obj = {"id": f"R{i}"}

                pref_s = (r.get("pref_str") or "").strip()
                obj["preference"] = split_list(pref_s)

                if is_auto:
                    gpa_s = (r.get("gpa_str") or "").strip()
                    try:
                        obj["gpa"] = float(gpa_s) if gpa_s else 0.0
                    except Exception:
                        obj["gpa"] = 0.0

                    deg = (r.get("deg_str") or "").strip()
                    if deg == "Degree Type":
                        deg = ""
                    obj["degree"] = deg or None

                dataset["residents"].append(obj)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(dataset, f, indent=2)

            messagebox.showinfo("Export dataset", "Dataset exported successfully.")

        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _on_export_results(self) -> None:
        if self._last_run_result is None:
            messagebox.showinfo("Export Results", "Run the simulation first.")
            return

        path = filedialog.asksaveasfilename(
            title="Export results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        try:
            result = self._last_run_result

            payload = {
                "mode": result.mode,
                "resMatch": result.resMatch,
                "hosMatch": {k: sorted(list(v)) for k, v in result.hosMatch.items()},
                "stats": result.stats,
                "unmatched_explain": result.unmatched_explain,
            }
            if result.hosPref is not None:
                payload["hosPref"] = result.hosPref

            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _on_restart(self) -> None:
        self.hospitals_view.reset()
        self.residents_view.reset()
        self.output_view.reset()
        self._last_run_result = None
        is_auto = self.hospitals_view._is_auto.get()
        self._on_mode_change(is_auto)
        self.output_view.set_log([])
        self.output_view.set_events_json([])

def main() -> None:
    app = StableMatchingApp()
    app.mainloop()

if __name__ == "__main__":
    main()
