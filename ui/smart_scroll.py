"""
SmartScrollFrame — CTkScrollableFrame محسّن للـ Linux
- عجلة الماوس تعمل على أي widget داخل الـ frame (bind_all)
- scrollbar يظهر فقط عند الحاجة
"""
import sys
import customtkinter as ctk


class SmartScrollFrame(ctk.CTkScrollableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._sb_visible = True
        self._sb_check_id = None

        # Linux: bind_all مثل CTkScrollableFrame لكن لـ Button-4/5
        if sys.platform.startswith("linux"):
            self.bind_all("<Button-4>", self._linux_wheel, add="+")
            self.bind_all("<Button-5>", self._linux_wheel, add="+")

        self.bind("<Configure>", self._schedule_sb_check, add="+")
        self._parent_canvas.bind("<Configure>", self._schedule_sb_check, add="+")

    def _linux_wheel(self, event):
        # نفس منطق check_if_master_is_canvas
        if not self.check_if_master_is_canvas(event.widget):
            return
        if self._parent_canvas.yview() == (0.0, 1.0):
            return
        if event.num == 4:
            self._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._parent_canvas.yview_scroll(1, "units")

    def _schedule_sb_check(self, event=None):
        if self._sb_check_id:
            try:
                self.after_cancel(self._sb_check_id)
            except Exception:
                pass
        self._sb_check_id = self.after(50, self._check_scrollbar)

    def _check_scrollbar(self):
        self._sb_check_id = None
        try:
            needs = self._parent_canvas.yview() != (0.0, 1.0)
            if needs and not self._sb_visible:
                self._scrollbar.grid()
                self._sb_visible = True
            elif not needs and self._sb_visible:
                self._scrollbar.grid_remove()
                self._sb_visible = False
        except Exception:
            pass
