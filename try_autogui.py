import win32gui
import win32process
import psutil
import pyautogui
import time
import os
import requests
from io import BytesIO
from PIL import Image
import win32clipboard
import win32con

TARGET_EXE_PATH = r"E:\SSoftwareFiles\QQOld\Bin\QQ.exe"

def enum_windows_callback(hwnd, results):
    if not win32gui.IsWindowVisible(hwnd):
        return
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        p = psutil.Process(pid)
        exe_path = p.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return

    # 比较路径，找目标窗口
    if os.path.normcase(exe_path) == os.path.normcase(TARGET_EXE_PATH):
        results.append(hwnd)

def find_windows_by_exe_path(target_path):
    results = []
    win32gui.EnumWindows(enum_windows_callback, results)
    return results

def download_image_to_clipboard(url):
    # 下载图片
    response = requests.get(url)
    response.raise_for_status()

    # 读取图片内容
    image = Image.open(BytesIO(response.content))

    # 转换为 DIB 格式并写入剪贴板
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # 去掉 BMP 文件头（保留 DIB 数据）
    output.close()

    # 写入剪贴板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_DIB, data)
    win32clipboard.CloseClipboard()

def main():
    hwnds = find_windows_by_exe_path(TARGET_EXE_PATH)
    if not hwnds:
        print("未找到目标程序对应窗口")
        return

    hwnd = hwnds[0]
    print(f"找到目标窗口 HWND: {hwnd}")

    # 先恢复窗口（防止最小化）
    win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE = 9

    # 设置窗口位置和大小，位置这里选屏幕左上角 100,100，大小 500x500
    x, y, w, h = 100, 100, 500, 500
    win32gui.MoveWindow(hwnd, x, y, w, h, True)

    time.sleep(0.5)  # 等待窗口刷新

    # 窗口内部控件相对坐标（你自己调）
    textbox_rel = (50, 450)
    sendbtn_rel = (450, 466)

    # 计算屏幕点击坐标
    click_textbox_x = x + textbox_rel[0]
    click_textbox_y = y + textbox_rel[1]
    click_sendbtn_x = x + sendbtn_rel[0]
    click_sendbtn_y = y + sendbtn_rel[1]

    print("点击文本框...")
    pyautogui.click(click_textbox_x, click_textbox_y)
    time.sleep(0.1)

    print("输入文字...")
    pyautogui.write("123", interval=0.1)
    time.sleep(0.01)

    print("点击发送按钮...")
    pyautogui.click(click_sendbtn_x, click_sendbtn_y)

    # 下载图片并放入剪贴板
    print("下载图片并放入剪贴板...")
    download_image_to_clipboard("http://101.132.131.209:6712/yintianxia")
    # another url: "http://101.132.131.209:6712/zhongying"
    time.sleep(0.5)

    # 模拟 Ctrl + V 粘贴图片
    print("粘贴图片...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # 点击发送按钮
    print("点击发送按钮...")
    pyautogui.click(click_sendbtn_x, click_sendbtn_y)

if __name__ == "__main__":
    main()
