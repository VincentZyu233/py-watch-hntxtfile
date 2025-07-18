import win32gui
import win32con
import win32api
import time

QQ_PATH = r"E:\SSoftwareFiles\QQOld\Bin\QQ.exe"
TARGET_TITLE = "1水_qwq群"

def enum_handler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if TARGET_TITLE in title:
            ctx.append(hwnd)

def get_target_hwnd():
    hwnds = []
    win32gui.EnumWindows(enum_handler, hwnds)
    return hwnds[0] if hwnds else None

def run_monitor():
    last_focused = None
    while True:
        focused_hwnd = win32gui.GetForegroundWindow()
        if focused_hwnd != last_focused:
            last_focused = focused_hwnd
            title = win32gui.GetWindowText(focused_hwnd)
            print(f"[焦点切换] 当前窗口: {title}")
            
            # 检测是否是 QQ 聊天窗口
            if TARGET_TITLE in title:
                print("[!] 焦点进入 QQ 窗口，尝试检测子控件")
                hwnd_chat = get_target_hwnd()
                detect_sub_controls(hwnd_chat)
        time.sleep(0.5)

def detect_sub_controls(hwnd):
    def enum_child(hwnd, _):
        cls = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        print(f"  子窗口: class={cls}, text='{title}', hwnd={hwnd}")
    win32gui.EnumChildWindows(hwnd, enum_child, None)

if __name__ == "__main__":
    run_monitor()
