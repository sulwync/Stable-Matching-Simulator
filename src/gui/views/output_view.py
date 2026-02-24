from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class OutputView(ttk.LabelFrame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, text="Output", padding=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        wrapper = ttk.Frame(self)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        self.vbar = ttk.Scrollbar(wrapper, orient="vertical")
        self.vbar.grid(row=0, column=1, sticky="ns")

        self.report = tk.Text(
            wrapper,
            wrap="word",
            height=1,
            padx=10, pady=10,
            state="disabled",
        )
        self.report.grid(row=0, column=0, sticky="nsew")
        self.report.configure(yscrollcommand=self.vbar.set)
        self.vbar.configure(command=self.report.yview)

        self.report.tag_configure("title", font=("Segoe UI", 12, "bold"))
        self.report.tag_configure("section", font=("Segoe UI", 10, "bold"))
        self.report.tag_configure("muted", foreground="#666666")
        self.report.tag_configure("mono", font=("Consolas", 10))
        self.report.tag_configure("good", foreground="#1a7f37")
        self.report.tag_configure("bad", foreground="#b42318")
        self.report.tag_configure("key", font=("Segoe UI", 10, "bold"))

        self.set_status("")

        # Log controls
        self._events: list[str] = []
        self._log_visible = False

        log_controls = ttk.Frame(self)
        log_controls.grid(row=99, column=0, sticky="ew", pady=(10, 0))
        log_controls.grid_columnconfigure(0, weight=1)

        self.btn_view_log = ttk.Button(log_controls, text="View Log", command=self._show_log)
        self.btn_hide_log = ttk.Button(log_controls, text="Hide Log", command=self._hide_log)
        self.btn_export_log = ttk.Button(log_controls, text="Export Log", command=self._export_log)

        self.btn_view_log.pack(side="left")

        # Log area
        self.log_frame = ttk.Frame(self)
        self.log_frame.grid(row=100, column=0, sticky="nsew", pady=(8, 0))
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.log_text = tk.Text(self.log_frame, height=10, wrap="none")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        ys = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        ys.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=ys.set)

        xs = ttk.Scrollbar(self.log_frame, orient="horizontal", command=self.log_text.xview)
        xs.grid(row=1, column=0, sticky="ew")
        self.log_text.configure(xscrollcommand=xs.set)

        self.log_frame.grid_remove()

    def reset(self) -> None:
        self._write("")

    def set_status(self, msg: str) -> None:
        return

    def _write_line(self, text: str, tag: str | None) -> None:
        if tag:
            self.report.insert("end", text + "\n", (tag,))
        else:
            self.report.insert("end", text + "\n")

    def _write_mono_table_hos_match(self, hosMatch: dict[str, set[str]]) -> None:
        for h in sorted(hosMatch.keys()):
            rs = sorted(hosMatch[h])
            rs_str = ", ".join(rs) if rs else "(none)"
            line = f"{h:<9}| {rs_str}"
            self._write_line(line, "mono")

    def render_results(
        self,
        *,
        resMatch: dict[str, str | None],
        hosMatch: dict[str, set[str]],
        unmatched_explain: list[tuple[str, dict]] | None = None,
        stats: dict | None = None,
    ) -> None:
        self.report.configure(state="normal")
        self.report.delete("1.0", "end")

        # Header
        self._write_line("Simulation Results", "title")
        self._write_line(" ", None)

        # Matches
        self._write_line("Stable Matches", "section")
        self._write_line("Hospital | Resident", "mono")
        self._write_line("-" * 20, "mono")
        self._write_mono_table_hos_match(hosMatch)
        self._write_line(" ", None)

        # Unmatched
        unmatched_res = sorted([r for r, h in resMatch.items() if h is None])
        self._write_line("Unmatched Participants", "section")

        if not unmatched_res:
            self._write_line("All residents matched ✅", "good")
        else:
            self._write_line(f"{len(unmatched_res)} resident(s) unmatched:", "bad")
            self._write_line("  " + ", ".join(unmatched_res), "mono")

        self._write_line(" ", None)

        # Unmatched explanation
        self._write_line("Why they were unmatched", "section")
        if unmatched_explain is None:
            self._write_line("(No explanation provided)", "muted")
        elif len(unmatched_explain) == 0:
            self._write_line("(All residents matched)", "good")
        else:
            for r, info in unmatched_explain:
                self._write_line(f"{r}", "key")
                for k in ["ranked", "unranked", "eligible", "ineligible", "blocked", "closestMiss", "note"]:
                    if k not in info:
                        continue
                    v = info[k]
                    if v in (None, [], ""):
                        continue

                    label = k.replace("closestMiss", "Closest miss") \
                            .replace("ineligible", "Ineligible") \
                            .replace("eligible", "Eligible") \
                            .replace("unranked", "Unranked") \
                            .replace("ranked", "Ranked") \
                            .replace("blocked", "Blocked") \
                            .replace("note", "Note")

                    if isinstance(v, list):
                        v_str = ", ".join(v)
                    else:
                        v_str = str(v)

                    bullet = f"  • {label}: {v_str}"
                    tag = "bad" if label in ("Blocked", "Unranked") else None
                    self._write_line(bullet, tag)
                self._write_line(" ", None)

        # Max proposals by a resident
        self._write_line("Max Proposals by a Resident", "section")

        mp = (stats or {}).get("Max Proposals By A Resident")
        if not mp:
            self._write_line("No Data", "muted")
        else:
            res_list, count = mp
            res_list = sorted(res_list) if isinstance(res_list, list) else []
            if count == 0 or not res_list:
                self._write_line("(No Proposals Recorded", "muted")
            else:
                who = "resident" if len(res_list) == 1 else "residents"
                proposals_word = "proposal" if count == 1 else "proposals"
                self._write_line(f"{len(res_list)} {who} made {count} {proposals_word}", "bad")
                self._write_line("  " + ", ".join(res_list), "mono")

        self._write_line("", None)

        # Stats
        if not stats:
            self._write_line("No statistics", "muted")
        else:
            def pct(x: float) -> str:
                return f"{x*100:.2f}%"

            def f2(x: float) -> str:
                return f"{x:.2f}"

            # 1) Match health
            ur = stats.get("Unmatched Rate", 0.0)
            self._write_line("Match Health", "key")
            self._write_line(f"Unmatched residents: {pct(ur)}", "bad" if ur > 0 else "good")
            self._write_line("", None)

            # 2) Resident satisfaction
            fcr = stats.get("First Choice Rate", 0.0)
            fcc = stats.get("First Choice Count", 0)
            avg_rr = stats.get("Average Resident's Preference Rank", 0.0)

            self._write_line("Resident Satisfaction", "key")
            self._write_line(f"First-choice matches: {fcc} ({pct(fcr)})", "good" if fcr >= 0.7 else None)
            self._write_line(f"Average resident rank: {f2(avg_rr)} (1.00 = best)", None)
            self._write_line("", None)

            # 3) Hospital satisfaction
            avg_hr = stats.get("Average Hospital's Preference Rank", 0.0)
            self._write_line("Hospital Satisfaction", "key")
            self._write_line(f"Average hospital rank: {f2(avg_hr)} (1.00 = best)", None)
            self._write_line("", None)

            # 4) Algorithm effort
            tp = stats.get("Total Proposals", 0)
            self._write_line("Algorithm Effort", "key")
            self._write_line(f"Total proposals made: {tp}", None)
            self._write_line("", None)

            # 5) Stability
            bp = stats.get("Blocking Pairs", [])
            self._write_line("Stability Check", "key")
            if not bp:
                self._write_line("Blocking pairs: None (stable)", "good")
            else:
                self._write_line(f"Blocking pairs found: {len(bp)} ❌ (not stable)", "bad")
                for (r, h) in bp[:20]:
                    self._write_line(f"     - ({r}, {h})", "mono")
                if len(bp) > 20:
                    self._write_line(f"     ... +{len(bp)-20} more", "muted")

            self._write_line(" ", None)

        self.report.configure(state="disabled")
        self.report.see("1.0")

    def _format_hos_match(self, hosMatch: dict[str, set[str]]) -> str:
        out: list[str] = []
        for h in sorted(hosMatch.keys()):
            rs = sorted(hosMatch[h])
            out.append(f"{h}: " + (", ".join(rs) if rs else "(none)") + "\n")
        return "".join(out)

    def _format_unmatched_explain(self, expl: list[tuple[str, dict]]) -> str:
        out: list[str] = []
        for r, info in expl:
            out.append(f"{r}:\n")
            for k in ["ranked", "unranked", "eligible", "ineligible", "closestMiss", "blocked", "note"]:
                if k in info:
                    out.append(f"  - {k}: {info[k]}\n")
            out.append("\n")
        return "".join(out)

    def _format_stats(self, stats: dict) -> str:
        out: list[str] = []
        for k, v in stats.items():
            out.append(f"{k}: {v}\n\n")
        return "".join(out).rstrip() + "\n"

    def _write(self, text: str) -> None:
        self.report.configure(state="normal")
        self.report.delete("1.0", "end")
        self.report.insert("1.0", text)
        self.report.configure(state="disabled")

    def append_section(self, title: str, body: str) -> None:
        self.report.configure(state="normal")
        self.report.insert("end", f"\n{title}\n", ("h1",))
        self.report.insert("end", body + "\n")
        self.report.configure(state="disabled")
        self.report.see("end")

    def set_log(self, events: list[str]) -> None:
        self._events = events or []
        # If log is visible, refresh content
        if self._log_visible:
            self._render_log()

        # If no events, force UI back to default state
        if not self._events:
            self._hide_log()

    def _render_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", "\n".join(self._events) if self._events else "(No log events)")
        self.log_text.configure(state="disabled")

    def _show_log(self) -> None:
        if not self._events:
            messagebox.showinfo("View Log", "No log events available. Run the simulation first.")
            return

        self._log_visible = True
        self._render_log()
        self.log_frame.grid()

        # Hide "View Log"
        self.btn_view_log.pack_forget()

        # Show "Hide Log" + "Export Log"
        self.btn_hide_log.pack(side="left")
        self.btn_export_log.pack(side="left", padx=(8, 0))

    def _hide_log(self) -> None:
        # Hide log area
        self._log_visible = False
        self.log_frame.grid_remove()

        # Hide "Hide Log" + "Export Log" if they are shown
        self.btn_hide_log.pack_forget()
        self.btn_export_log.pack_forget()

        # Show "View Log" again
        if not self.btn_view_log.winfo_ismapped():
            self.btn_view_log.pack(side="left")

    def _export_log(self) -> None:
        if not self._events:
            messagebox.showinfo("Export Log", "No log events available.")
            return

        path = filedialog.asksaveasfilename(
            title="Export log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self._events))
            messagebox.showinfo("Export Log", "Log exported successfully.")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))