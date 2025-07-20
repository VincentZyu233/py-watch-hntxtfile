import sys

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径，兼容 PyInstaller 打包和开发环境。
    """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 标准库
import os
import time
from enum import Enum
import threading
from collections import Counter
from io import BytesIO

# 第三方库
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
import pygetwindow as gw
from PIL import Image
import yaml
import requests
import psutil
import pyautogui

# Windows专用库
import win32gui
import win32process
import win32clipboard
import win32con




CONFIG_JSON = {}
DEFAULT_CONFIG = {
    "target_txt_path": r"G:\GGames\Minecraft\shuyeyun\qq-bot\miao-qinghuitou\恒行5挂机软件\OpenCode\HN5FC.txt",
    "oldqq_exe_path": r"E:\SSoftwareFiles\QQOld\Bin\QQ.exe",
    "qq_window_titles": "开发测试1-hn300,开发测试2-hn300",
    "code_count": 14,
    "enable_send": True,
    "prefix_text": "推送hn300信息",
    "enable_tag": True,
    "tag_style": "空心36_③⑥",
    "show_span_sum": False,
    "span_sum_use_circle_style": False,
    "img_server_url": "http://101.132.131.209:6712"
}

CONFIG_FILE = "./config.yaml"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, allow_unicode=True)


def enum_windows_callback(hwnd, results):
    if not win32gui.IsWindowVisible(hwnd):
        return
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        p = psutil.Process(pid)
        exe_path = p.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return

    # if os.path.normcase(exe_path) == os.path.normcase(TARGET_EXE_PATH):
    if os.path.normcase(exe_path) == os.path.normcase(CONFIG_JSON.get("oldqq_exe_path", "")):
        results.append(hwnd)

def find_windows_by_exe_path(target_path):
    def callback(hwnd, results):
        if not win32gui.IsWindowVisible(hwnd):
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            p = psutil.Process(pid)
            exe_path = p.exe()
            if os.path.normcase(exe_path) == os.path.normcase(target_path):
                results.append(hwnd)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return

    results = []
    win32gui.EnumWindows(callback, results)
    return results

DIGIT_STYLE_MAP = {
    '空心36_③⑥': {'0':'⓪', '1':'①', '2':'②', '3': '③', '4':'④', '5':'⑤', '6': '⑥', '7':'⑦', '8':'⑧', '9':'⑨'},
    '罗马数字36_ⅢⅥ': {'0':'０', '1':'Ⅰ', '2':'Ⅱ', '3': 'Ⅲ', '4':'Ⅳ', '5':'Ⅴ', '6': 'Ⅵ', '7':'Ⅶ', '8':'Ⅷ', '9':'Ⅸ'},
    '实心36_❸❻': {'0':'⓿', '1':'❶', '2':'❷', '3': '❸', '4':'❹', '5':'❺', '6': '❻', '7':'❼', '8':'❽', '9':'❾'},
    '括号36_⑶⑹': {'0':'⑽', '1':'⑴', '2':'⑵', '3': '⑶', '4':'⑷', '5':'⑸', '6': '⑹', '7':'⑺', '8':'⑻', '9':'⑼'}, # 0用别的，比如⑽
    '序号36_⒊⒍': {'0':'⓿', '1':'⒈', '2':'⒉', '3': '⒊', '4':'⒋', '5':'⒌', '6': '⒍', '7':'⒎', '8':'⒏', '9':'⒐'},
}

CIRCLED_NUMBE_MAP_1_TO_50 = {
    1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤',
    6: '⑥', 7: '⑦', 8: '⑧', 9: '⑨', 10: '⑩',
    11: '⑪', 12: '⑫', 13: '⑬', 14: '⑭', 15: '⑮',
    16: '⑯', 17: '⑰', 18: '⑱', 19: '⑲', 20: '⑳',
    21: '㉑', 22: '㉒', 23: '㉓', 24: '㉔', 25: '㉕',
    26: '㉖', 27: '㉗', 28: '㉘', 29: '㉙', 30: '㉚',
    31: '㉛', 32: '㉜', 33: '㉝', 34: '㉞', 35: '㉟',
    36: '㊱', 37: '㊲', 38: '㊳', 39: '㊴', 40: '㊵',
    41: '㊶', 42: '㊷', 43: '㊸', 44: '㊹', 45: '㊺',
    46: '㊻', 47: '㊼', 48: '㊽', 49: '㊾', 50: '㊿'
}

def get_tag(code, enable_tag, tag_style):
    if not enable_tag:
        return ""
    is_3 = len(set(code[-3:])) < 3
    base = '3' if is_3 else '6'
    return DIGIT_STYLE_MAP.get(tag_style, {}).get(base, '')

def convert_digit_to_tag(digit, style):
    return DIGIT_STYLE_MAP.get(style, {}).get(str(digit), str(digit))

class FileFormat(Enum):
    """
    定义两种文件格式。
    HENGHANG: 期号带连字符的格式 (e.g., 250719-164 99016)
    XINHANG: 期号不带连字符的格式 (e.g., 2502090581 21929)
    """
    HENGHANG = "HENGHANG"
    XINHANG = "XINHANG"


def extract_codes(log_func, path, count, enable_tag, tag_style, show_span_sum, span_sum_use_circle_style):
    first_line_content = ""
    lines = []
    all_digits = []

    # Add a check for file existence at the very beginning of extract_codes
    if not os.path.exists(path):
        if log_func:
            log_func(f"❌ 错误：txt 文件路径不存在：{path}")
        return "", ""

    with open(path, 'r', encoding='utf-8') as f:
        # 1. 读取第一行内容，不再用于判断格式
        try:
            first_line_content = f.readline().strip()
            # Reset file pointer to the beginning to read all lines
            f.seek(0)
        except Exception as e:
            if log_func:
                log_func(f"Error reading first line: {e}")
            return "", ""

        # 2. 遍历文件读取行数据
        for i, line in enumerate(f):
            # If we've processed the desired number of lines (plus the first line), break
            if i > count:
                break
            
            # Skip empty lines
            stripped_line = line.strip()
            if not stripped_line:
                continue

            parts = stripped_line.split()
            if len(parts) != 2:
                if log_func:
                    log_func(f"Warning: Skipped malformed line (expected 2 parts, got {len(parts)}): {stripped_line}")
                continue

            period_raw = parts[0]
            code = parts[1].zfill(5) # Ensure code is 5 digits

            # Extract the last three digits for the period
            period = period_raw[-3:]

            # Process tag and span_sum (this logic remains consistent)
            tag = get_tag(code, enable_tag, tag_style)
            span_sum_text = ""
            if show_span_sum:
                digits = [int(d) for d in code]
                span = max(digits) - min(digits)
                total = sum(digits)

                if span_sum_use_circle_style:
                    converted_span = CIRCLED_NUMBE_MAP_1_TO_50.get(span, str(span))
                    converted_total = CIRCLED_NUMBE_MAP_1_TO_50.get(total, str(total))
                    span_sum_text = f" 跨{converted_span} 和{converted_total}"
                else:
                    span_sum_text = f" 跨{span} 和{total}"

            lines.append(f"{period} 【{code}】{tag} {span_sum_text}")
            all_digits.extend(list(code)) # Collect each digit for statistics

    # Reverse the lines
    lines = lines[::-1]

    # Calculate digit frequency (this logic remains consistent)
    digit_freq = Counter(all_digits)
    sorted_digits = digit_freq.most_common()

    hot = [d for d, _ in sorted_digits[:3]]
    warm = [d for d, _ in sorted_digits[3:7]]
    cold = [d for d, _ in sorted_digits[7:10]]

    stat_text = "----------------\n"
    stat_text += f"热：{' '.join(hot)}\n"
    stat_text += f"温：{' '.join(warm)}\n"
    stat_text += f"冷：{' '.join(cold)}\n"
    stat_text += "----------------"

    final_text = "\n".join(lines) + "\n" + stat_text
    return final_text, first_line_content # Return the content of the first line

def download_image_to_clipboard(url):
    response = requests.get(url)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_DIB, data)
    win32clipboard.CloseClipboard()


def send_message_and_images(log_func, code_from_txt, exe_path, target_titles, img_server_url):
    title_list = [t.strip() for t in target_titles.split(",") if t.strip()]
    matched_windows = []

    all_windows = gw.getAllWindows()

    for title in title_list:
        for win in all_windows:
            if win.title == title:
                hwnd = win._hWnd
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    p = psutil.Process(pid)
                    if os.path.normcase(p.exe()) == os.path.normcase(exe_path):
                        matched_windows.append((title, hwnd))
                        break  # 一个 title 只匹配一个窗口
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            if log_func:
                log_func(f"⚠️ 未找到标题为「{title}」且 exe 匹配的窗口")

    if not matched_windows:
        if log_func: log_func("❌ 未匹配到任何符合条件的窗口")
        return
    
    if log_func: log_func(f"🔍 所有符合条件的窗口: {matched_windows}")

    offset_x = 0
    offset_y = 0
    increment_x = 50 # 每次向右偏移50像素
    increment_y = 50 # 每次向下偏移50像素

    # 遍历所有匹配窗口并发送内容
    for title, hwnd in matched_windows:
        if log_func: log_func(f"✅ 开始向窗口「{title}」发送消息...")

        # 获取窗口当前的尺寸和位置
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        current_w = right - left
        current_h = bottom - top

        # 计算新的窗口坐标：在当前坐标基础上增加偏移量
        new_x = 100 + offset_x # 初始X坐标100，加上累积偏移
        new_y = 100 + offset_y # 初始Y坐标100，加上累积偏移

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) # 还原窗口
        win32gui.MoveWindow(hwnd, new_x, new_y, current_w, current_h, True)
        time.sleep(0.2) # 给予窗口移动和渲染的时间

        # 更新下一个窗口的偏移量
        offset_x += increment_x
        offset_y += increment_y

        textbox_rel = (50, 450)
        sendbtn_rel = (450, 466)
        click_textbox_x = new_x + textbox_rel[0]
        click_textbox_y = new_y + textbox_rel[1]
        click_sendbtn_x = new_x + sendbtn_rel[0]
        click_sendbtn_y = new_y + sendbtn_rel[1]

        # 输入文本内容
        if log_func: log_func(f"向「{title}」粘贴txt文本")
        win32gui.SetForegroundWindow(hwnd) # 将当前窗口置于前台
        time.sleep(0.2) # 等待窗口完全激活
        pyautogui.click(click_textbox_x, click_textbox_y)
        time.sleep(0.1)
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, code_from_txt)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        # pyautogui.click(click_sendbtn_x, click_sendbtn_y)
        pyautogui.hotkey('ctrl', 'enter')
        time.sleep(0.1)

        
        win32gui.SetForegroundWindow(hwnd) # 将当前窗口置于前台
        time.sleep(0.2) # 等待窗口完全激活
        # 发送图片
        for img_path in ["zhongying", "yintianxia"]:
            img_url = f"{img_server_url}/{img_path}"
            if log_func: log_func(f"向「{title}」粘贴图片: {img_url}")
            download_image_to_clipboard(img_url)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
        
        # pyautogui.click(click_sendbtn_x, click_sendbtn_y)
        pyautogui.hotkey('ctrl', 'enter')
        time.sleep(0.3)



class FileWatcherApp:
    def get_current_config(self):
        return {
            "oldqq_exe_path": self.qq_exe_path_var.get(),
            "target_txt_path": self.target_txt_path_var.get(),
            "qq_window_titles": self.qq_window_titles_var.get().strip(),
            "code_count": int(self.code_count_var.get()),
            "enable_send": self.enable_send_var.get(),
            "prefix_text": self.prefix_text_var.get().strip(),
            "enable_tag": self.enable_tag_var.get(),
            "tag_style": self.tag_style_var.get(),
            "show_span_sum": self.show_span_sum_var.get(),
            "span_sum_use_circle_style": self.span_sum_use_circle_style_var.get(),
            "img_server_url": self.img_server_url_var.get().strip(),
        }

    def __init__(self, root):
        # style = ttk.Style()
        # style.theme_use('vista')  # 可选 'clam'、'alt'、'default'、'vista'、'xpnative'

        self.root = root
        self.root.title("[20250720v3][VincentZyu]监控txt文件+发送QQ")

        self.last_mtime = None  # 这里初始化
        
        self.qq_exe_path_var = tk.StringVar(value=CONFIG_JSON.get("oldqq_exe_path"))
        self.target_txt_path_var = tk.StringVar(value=CONFIG_JSON.get("target_txt_path"))

        # 路径选择区
        path_frame = tk.LabelFrame(root, text="路径设置", padx=10, pady=5)
        path_frame.pack(fill='x', padx=10, pady=(10, 5))

        tk.Label(path_frame, text="QQ 可执行文件路径:").grid(row=1, column=0, sticky='w')
        self.qq_path_entry = ttk.Entry(path_frame, textvariable=self.qq_exe_path_var, width=60)
        self.qq_path_entry.grid(row=1, column=1, sticky='we', padx=(5, 0))
        ttk.Button(path_frame, text="浏览", command=self.select_qq_exe).grid(row=1, column=2, padx=5)


        tk.Label(path_frame, text="选择 txt 文件路径:").grid(row=0, column=0, sticky='w')
        self.target_txt_path_entry = ttk.Entry(path_frame, textvariable=self.target_txt_path_var, width=60)
        self.target_txt_path_entry.grid(row=0, column=1, sticky='we', padx=(5, 0))
        ttk.Button(path_frame, text="浏览", command=self.select_file).grid(row=0, column=2, padx=5)
        path_frame.columnconfigure(1, weight=1)

        # 参数设置区
        param_frame = tk.LabelFrame(root, text="发送参数", padx=10, pady=5)
        param_frame.pack(fill='x', padx=10, pady=(0, 5))

        tk.Label(param_frame, text="窗口标题(英文逗号分隔):").grid(row=0, column=0, sticky='w')
        self.qq_window_titles_var = tk.StringVar(value=CONFIG_JSON.get("qq_window_titles"))
        ttk.Entry(param_frame, textvariable=self.qq_window_titles_var, width=40).grid(row=0, column=1, columnspan=2, sticky='we', pady=2)


        tk.Label(param_frame, text="发送前 N 行:").grid(row=1, column=0, sticky='w')
        self.code_count_var = tk.StringVar(value=str(CONFIG_JSON.get("code_count")))
        ttk.Entry(param_frame, textvariable=self.code_count_var, width=8).grid(row=1, column=1, sticky='w', padx=(0, 10))

        self.enable_send_var = tk.BooleanVar(value=bool(CONFIG_JSON.get("enable_send")))
        ttk.Checkbutton(param_frame, text="启用发送 QQ 消息", variable=self.enable_send_var).grid(row=1, column=2, sticky='w', padx=(0, 10))

        tk.Label(param_frame, text="开头文字:").grid(row=2, column=0, sticky='w')
        self.prefix_text_var = tk.StringVar(value=str(CONFIG_JSON.get("prefix_text")))
        ttk.Entry(param_frame, textvariable=self.prefix_text_var, width=40).grid(row=2, column=1, columnspan=2, sticky='we', pady=2)

        self.enable_tag_var = tk.BooleanVar(value=CONFIG_JSON.get("enable_tag"))
        ttk.Checkbutton(param_frame, text="加尾部 36tag", variable=self.enable_tag_var).grid(row=3, column=0, sticky='w')

        tk.Label(param_frame, text="tag 样式:").grid(row=3, column=1, sticky='e')
        self.tag_style_var = tk.StringVar(value="空心36_③⑥")
        tk.OptionMenu(param_frame, self.tag_style_var, "空心36_③⑥", "罗马数字36_ⅢⅥ", "实心36_❸❻", "括号36_⑶⑹", "序号36_⒊⒍").grid(row=3, column=2, sticky='w')

        self.show_span_sum_var = tk.BooleanVar(value=CONFIG_JSON.get("show_span_sum"))
        ttk.Checkbutton(param_frame, text="显示 跨 / 和", variable=self.show_span_sum_var).grid(row=4, column=0, sticky='w', pady=(2, 0))

        self.span_sum_use_circle_style_var = tk.BooleanVar(value=CONFIG_JSON.get("span_sum_use_circle_style"))
        ttk.Checkbutton(param_frame, text="跨和使用空心数字圈样式", variable=self.span_sum_use_circle_style_var).grid(row=4, column=1, sticky='w', pady=(2, 0), padx=(10,0))

        # 增加图片服务器地址配置输入框
        tk.Label(param_frame, text="图片服务器地址:").grid(row=5, column=0, sticky='w')
        self.img_server_url_var = tk.StringVar(value=CONFIG_JSON.get("img_server_url"))
        ttk.Entry(param_frame, textvariable=self.img_server_url_var, width=40).grid(row=5, column=1, columnspan=2, sticky='we', pady=2)

        # 在图片服务器地址输入框下方添加说明文字
        tk.Label(param_frame, text="格式是 http(s)://ip:port，末尾没有斜杠", fg="red").grid(row=6, column=0, columnspan=3, sticky='w')


        # 操作按钮区
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', padx=10, pady=(0, 5))
        ttk.Button(btn_frame, text="手动发送 数字 + 图片", command=self.trigger_send).pack(anchor='w')

        # Console输出区
        tk.Label(root, text="Console 输出:").pack(anchor='w', padx=10, pady=(5, 0))
        self.console = ScrolledText(root, height=15, state='disabled')
        self.console.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    
    def select_qq_exe(self):
        path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if path and path.lower().endswith(".exe"):
            self.qq_exe_path_var.set(path)
            self.log(f"已设置 QQ 可执行文件路径为：{path}")
        else:
            self.log("❌ 无效的 QQ 可执行路径，必须为 .exe 文件")


    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.target_txt_path_var.set(path)
            self.last_mtime = None
            self.log(f"已切换监控路径为：{path}")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[INFO] {timestamp} {message}\n"
        self.console.configure(state='normal')
        self.console.insert(tk.END, full_message)
        self.console.configure(state='disabled')
        self.console.see(tk.END)

    def watch_file(self):
        while self.running:
            path = self.target_txt_path_var.get()
            if os.path.isfile(path):
                try:
                    mtime = os.path.getmtime(path)
                    if self.last_mtime is None:
                        self.last_mtime = mtime
                    elif mtime != self.last_mtime:
                        self.last_mtime = mtime
                        self.log("检测到文件变动，执行发送操作！")
                        self.trigger_send()
                except Exception as e:
                    self.log(f"监控文件时出错：{e}")
            time.sleep(0.9)

    def trigger_send(self):
        self.log("开始执行发送...")


        qq_exe_path = self.qq_exe_path_var.get()
        file_path = self.target_txt_path_var.get()

        # Add checks for file and exe paths before proceeding
        if not os.path.exists(qq_exe_path):
            self.log(f"❌ QQ 可执行文件路径不存在：{qq_exe_path}，请检查。")
            return
        if not os.path.exists(file_path):
            self.log(f"❌ txt 文件路径不存在：{file_path}，请检查。")
            return

        target_titles = self.qq_window_titles_var.get()
        code_count = int(self.code_count_var.get())
        enable_send = self.enable_send_var.get()
        prefix_text = self.prefix_text_var.get().strip()
        enable_tag = self.enable_tag_var.get()
        tag_style = self.tag_style_var.get()
        show_span_sum = self.show_span_sum_var.get()
        span_sum_use_circle_style = self.span_sum_use_circle_style_var.get()

        extracted, latest_code = extract_codes(self.log, file_path, code_count, enable_tag, tag_style, show_span_sum, span_sum_use_circle_style)
        if prefix_text:
            extracted = prefix_text + "\n" + extracted

        self.log(f"提取前 {code_count} 行 code：\n 最新一期: {latest_code}")

        if not enable_send:
            self.log("发送已禁用，仅输出日志")
            return
        
        img_server_url = self.img_server_url_var.get().strip()
        def do_send():
            send_message_and_images(self.log, code_from_txt=extracted, exe_path=qq_exe_path, target_titles=target_titles, img_server_url=img_server_url)

        threading.Thread(target=do_send, daemon=True).start()

    def stop(self):
        self.running = False



if __name__ == "__main__":
    CONFIG_JSON = load_config()
    style = Style("flatly")  # 你可以换成 'superhero', 'cyborg', 'journal' 等等
    root = style.master       # 相当于 root = tk.Tk()
    # root = tk.Tk()
    app = FileWatcherApp(root)

    app.running = True
    threading.Thread(target=app.watch_file, daemon=True).start()

    icon_img_path = get_resource_path("assets\\logo.png")
    try:
        icon_img = tk.PhotoImage(file=icon_img_path)
        root.iconphoto(True, icon_img)
    except tk.TclError as e:
        app.log(f"加载 logo 失败: {e}. 请确保 assets/logo.png 文件存在。")
        # 可以选择设置一个默认图标或者不设置

    root.protocol("WM_DELETE_WINDOW", lambda: (save_config(app.get_current_config()), app.stop(), root.destroy()))
    root.mainloop()
