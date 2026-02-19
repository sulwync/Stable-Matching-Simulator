from __future__ import annotations

import tkinter as tk


class PlaceholderEntry(tk.Entry):
    def __init__(
        self,
        master,
        placeholder: str,
        *,
        muted_fg: str = "#888888",
        normal_fg: str = "#000000",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.muted_fg = muted_fg
        self.normal_fg = normal_fg
        self._has_placeholder = False

        self._show_placeholder()

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self) -> None:
        self.delete(0, "end")
        self.insert(0, self.placeholder)
        self.config(fg=self.muted_fg)
        self._has_placeholder = True

    def _on_focus_in(self, _evt) -> None:
        if self._has_placeholder:
            self.delete(0, "end")
            self.config(fg=self.normal_fg)
            self._has_placeholder = False

    def _on_focus_out(self, _evt) -> None:
        if not self.get().strip():
            self._show_placeholder()

    def get_value(self) -> str:
        if self._has_placeholder:
            return ""
        return self.get().strip()

    def reset(self) -> None:
        self._show_placeholder()
