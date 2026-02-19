from __future__ import annotations

import tkinter as tk
from tkinter import ttk


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

        self.report.tag_configure("h1", font=("Segoe UI", 11, "bold"))
        self.report.tag_configure("mono", font=("Consolas", 10))

        self.set_status("")

    def reset(self) -> None:
        self._write("")

    def set_status(self, msg: str) -> None:
        return

    def render_results(
        self,
        *,
        resMatch: dict[str, str | None],
        hosMatch: dict[str, set[str]],
        unmatched_explain: list[tuple[str, dict]] | None = None,
        stats: dict | None = None,
    ) -> None:
        
        lines: list[str] = []

        # Stable Matches (hospital -> residents)
        lines.append("Stable Matches\n")
        lines.append(self._format_hos_match(hosMatch))
        lines.append("\n")

        # Unmatched
        lines.append("Unmatched Participants\n")
        unmatched_res = [r for r, h in resMatch.items() if h is None]
        if unmatched_res:
            lines.append("Residents: " + ", ".join(sorted(unmatched_res)) + "\n")
        else:
            lines.append("Residents: (none)\n")
        lines.append("\n")

        if unmatched_explain is not None:
            lines.append("Unmatched Explanation\n")
            lines.append(self._format_unmatched_explain(unmatched_explain))
            lines.append("\n")

        # Stats
        lines.append("Statistic\n")
        if stats:
            lines.append(self._format_stats(stats))
        else:
            lines.append("(no stats)\n")

        self._write("".join(lines))

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
            for k in ["mode", "degree", "gpa", "ranked", "unranked", "eligible", "ineligible", "closestMiss", "blocked", "note"]:
                if k in info:
                    out.append(f"  - {k}: {info[k]}\n")
            out.append("\n")
        return "".join(out)

    def _format_stats(self, stats: dict) -> str:
        out: list[str] = []
        for k, v in stats.items():
            out.append(f"{k}: {v}\n")
        return "".join(out)

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
