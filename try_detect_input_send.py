import win32gui
import win32con
import win32process
import psutil
import time
import pyautogui

# ==== 配置 ====
WINDOW_TITLE = "1水_qwq群"
TARGET_EXE_PATH = r"E:\SSoftwareFiles\QQOld\Bin\QQ.exe"
SEND_TEXT = "123"

def find_target_window():
    hwnds = []

    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if WINDOW_TITLE in title:
                hwnds.append(hwnd)

    win32gui.EnumWindows(enum_windows_callback, None)

    for hwnd in hwnds:
        # 获取进程 ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        exe_path = psutil.Process(pid).exe()
        if exe_path.lower() == TARGET_EXE_PATH.lower():
            return hwnd
    return None

def restore_and_focus(hwnd):
    # 如果窗口最小化了，恢复它
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

def send_message_via_gui():
    hwnd = find_target_window()
    if not hwnd:
        print("[ERR] 没找到目标窗口。")
        return

    print(f"[OK] 找到窗口 hwnd={hwnd}")
    restore_and_focus(hwnd)

    # 使用图像匹配找到文本框和发送按钮
    print("[INFO] 尝试图像识别控件...")
    textbox = pyautogui.locateCenterOnScreen("textbox_template.png", confidence=0.8)
    sendbtn = pyautogui.locateCenterOnScreen("sendbtn_template.png", confidence=0.8)

    if not textbox or not sendbtn:
        print("[ERR] 没找到控件位置。请确保模板图像匹配，且QQ窗口已打开。")
        return

    print("[OK] 找到控件位置，模拟输入...")
    pyautogui.click(textbox)
    pyautogui.write(SEND_TEXT, interval=0.05)
    pyautogui.click(sendbtn)
    print("[OK] 发送完成。")

if __name__ == "__main__":
    send_message_via_gui()
