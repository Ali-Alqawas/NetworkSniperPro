"""
SmartScrollFrame — CTkScrollableFrame محسّن للـ Linux
- عجلة الماوس تعمل على Linux (Button-4/5)
- scrollbar يظهر فقط عند الحاجة (بدون configure loop)
"""
import sys
import customtkinter as ctk


class SmartScrollFrame(ctk.CTkScrollableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._sb_visible = True
        self._sb_check_id = None

        # Linux: Button-4/5 على الـ canvas والـ frame
        if sys.platform.startswith("linux"):
            for widget in (self._parent_canvas, self):
                widget.bind("<Button-4>", self._scroll_up,   add="+")
                widget.bind("<Button-5>", self._scroll_down, add="+")

        # فحص الـ scrollbar بعد رسم المحتوى (مرة واحدة بعد idle)
        self.bind("<Configure>", self._schedule_sb_check, add="+")
        self._parent_canvas.bind("<Configure>", self._schedule_sb_check, add="+")

    def _scroll_up(self, event):
        if self._parent_canvas.yview() != (0.0, 1.0):
            self._parent_canvas.yview_scroll(-1, "units")
        return "break"

    def _scroll_down(self, event):
        if self._parent_canvas.yview() != (0.0, 1.0):
            self._parent_canvas.yview_scroll(1, "units")
        return "break"

    def _schedule_sb_check(self, event=None):
        """جدولة الفحص بعد انتهاء كل أحداث الـ configure الحالية"""
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
