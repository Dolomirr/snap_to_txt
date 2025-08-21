import time
import tkinter as tk

import mss
from PIL import Image

BORDER_THICKNESS = 1
BORDER_COLOR = "red"
REPAINT_DELAY = 0.03
UPDATE_INTERVAL_MS = 4

def select_region():  # noqa: PLR0915
    with mss.mss() as sct:
        virtual_screen = sct.monitors[0]
        width = virtual_screen["width"]
        height = virtual_screen["height"]
        left = virtual_screen["left"]
        top = virtual_screen["top"]

    root = tk.Tk()
    root.geometry(f"{width}x{height}+{left}+{top}")
    root.overrideredirect(boolean=True)
    root.attributes("-topmost", True)  # noqa: FBT003
    root.attributes("-alpha", 0.0)
    root.configure(bg="")

    borders = {"top": None, "left": None, "right": None, "bottom": None}
    start_x = start_y = 0
    dragging = False

    pending = {"x1": 0, "y1": 0, "x2": 0, "y2": 0, "scheduled": False}
    result = None

    def ensure_borders():
        
        if any(brd for brd in borders.values()) is None:
            msg = 'Error loading snap'
            raise RuntimeError(msg)
        
        for name in borders:
            if borders[name] is None or not bool(borders[name].winfo_exists()):
                w = tk.Toplevel(root)
                w.overrideredirect(True)
                w.attributes("-topmost", True)
                w.configure(background=BORDER_COLOR)
                w.bind("<ButtonPress-1>", on_click)
                w.bind("<B1-Motion>", on_drag)
                w.bind("<ButtonRelease-1>", on_release)
                borders[name] = w
        for w in borders.values():
            try:
                w.lift()
            except Exception:
                pass

    def apply_pending_geometry():
        pending["scheduled"] = False
        x1, y1, x2, y2 = pending["x1"], pending["y1"], pending["x2"], pending["y2"]

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        w = max(0, int(x2 - x1))
        h = max(0, int(y2 - y1))
        t = BORDER_THICKNESS

        try:
            borders["top"].geometry(f"{w}x{t}+{x1}+{y1}")
            borders["bottom"].geometry(f"{w}x{t}+{x1}+{y2 - t}")
            borders["left"].geometry(f"{t}x{h}+{x1}+{y1}")
            borders["right"].geometry(f"{t}x{h}+{x2 - t}+{y1}")
        except Exception:
            pass

    def schedule_geometry_update(x1, y1, x2, y2):
        pending["x1"], pending["y1"], pending["x2"], pending["y2"] = x1, y1, x2, y2
        if not pending["scheduled"]:
            pending["scheduled"] = True
            root.after(UPDATE_INTERVAL_MS, apply_pending_geometry)

    def destroy_borders():
        for name in list(borders.keys()):
            w = borders[name]
            if w is not None and bool(w.winfo_exists()):
                try:
                    w.destroy()
                except Exception:
                    pass
            borders[name] = None

    def on_click(event):
        nonlocal start_x, start_y, dragging
        dragging = True
        start_x, start_y = int(event.x_root), int(event.y_root)
        ensure_borders()
        try:
            root.grab_set()
        except Exception:
            pass

    def on_drag(event):
        if not dragging:
            return
        cur_x, cur_y = int(event.x_root), int(event.y_root)
        schedule_geometry_update(start_x, start_y, cur_x, cur_y)

    def on_release(event):
        nonlocal dragging
        nonlocal result
        if not dragging:
            return
        dragging = False
        end_x, end_y = int(event.x_root), int(event.y_root)
        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        w, h = x2 - x1, y2 - y1

        try:
            root.grab_release()
        except Exception:
            pass

        destroy_borders()
        root.withdraw()
        root.update_idletasks()
        root.update()
        time.sleep(REPAINT_DELAY)

        snapped_img = capture_region(x1, y1, w, h)
        root.destroy()
        result = snapped_img

    def on_cancel(event=None):
        try:
            root.grab_release()
        except Exception:
            pass
        destroy_borders()
        root.destroy()

    root.bind("<ButtonPress-1>", on_click)
    root.bind("<B1-Motion>", on_drag)
    root.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_cancel)

    root.mainloop()
    
    return result
    

def capture_region(x, y, width, height):
    if width <= 0 or height <= 0:
        print("Empty selection; nothing saved.")
        return
    with mss.mss() as sct:
        img = sct.grab({"top": int(y), "left": int(x), "width": int(width), "height": int(height)})
        pil_img = Image.frombytes("RGB", img.size, img.rgb)
    
    # pil_img.show()
    return pil_img

        

if __name__ == "__main__":
    result = select_region()
    if result is not None:
        result.show()
