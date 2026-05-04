"""
SmartScrollFrame — CTkScrollableFrame محسّن:
- عجلة الماوس تعمل على Linux (Button-4/5) + Windows/Mac (MouseWheel)
- الـ scrollbar يظهر فقط عند وجود محتوى زائد (ديناميكي)
- لا تعارض مع النظام المدمج
"""
import sys
import customtkinter as ctk


class SmartScrollFrame(ctk.CTkScrollableFrame):
    """
    CTkScrollableFrame مع:
    1. دعم Linux mousewheel (Button-4/5)
    2. scrollbar يختفي تلقائياً عند عدم الحاجة
    """

    def __init__(self, master, **kwargs):
        # إخفاء الـ scrollbar افتراضياً — نتحكم فيه يدوياً
        super().__init__(master, **kwargs)

        # Linux: ربط Button-4/5 على مستوى الـ canvas مباشرة
        if sys.platform.startswith("linux"):
            self._parent_canvas.bind("<Button-4>", self._linux_scroll_up,   add="+")
            self._parent_canvas.bind("<Button-5>", self._linux_scroll_down, add="+")
            self.bind("<Button-4>", self._linux_scroll_up,   add="+")
            self.bind("<Button-5>", self._linux_scroll_down, add="+")

        # مراقبة تغيير المحتوى لإظهار/إخفاء الـ scrollbar
        self.bind("<Configure>", self._update_scrollbar_visibility, add="+")
        self._parent_canvas.bind("<Configure>", self._update_scrollbar_visibility, add="+")

        # إخفاء الـ scrollbar في البداية
        self._scrollbar.grid_remove()

    def _linux_scroll_up(self, event):
        if self._parent_canvas.yview() != (0.0, 1.0):
            self._parent_canvas.yview_scroll(-1, "units")
        return "break"

    def _linux_scroll_down(self, event):
        if self._parent_canvas.yview() != (0.0, 1.0):
            self._parent_canvas.yview_scroll(1, "units")
        return "break"

    def _update_scrollbar_visibility(self, event=None):
        """إظهار الـ scrollbar فقط عند وجود محتوى يتجاوز الحاوية"""
        try:
            yview = self._parent_canvas.yview()
            if yview == (0.0, 1.0):
                self._scrollbar.grid_remove()
            else:
                self._scrollbar.grid()
        except Exception:
            pass
