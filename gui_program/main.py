# 标准库
import os
import time
import threading
from collections import Counter
from io import BytesIO

# 第三方库
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
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
    "code_count": 14,
    "enable_send": True,
    "prefix_text": "推送hn300信息",
    "enable_tag": True,
    "tag_style": "空心36_③⑥",
    "show_span_sum": False
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

def get_tag(code, enable_tag, tag_style):
    if not enable_tag:
        return ""
    is_3 = len(set(code[-3:])) < 3
    base = '3' if is_3 else '6'
    style_map = {
        '空心36_③⑥': {'3': '③', '6': '⑥'},
        '罗马数字36_ⅢⅥ': {'3': 'Ⅲ', '6': 'Ⅵ'},
        '实心36_❸❻': {'3': '❸', '6': '❻'},
        '括号36_⑶⑹': {'3': '⑶', '6': '⑹'},
        '序号36_⒊⒍': {'3': '⒊', '6': '⒍'},
    }
    return style_map.get(tag_style, {}).get(base, '')

def extract_codes(path, count, enable_tag=True, tag_style="空心36_③⑥", show_span_sum = False):
    first_line = ""
    lines = []
    all_digits = []
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                first_line = line
            if i >= count:
                break
            parts = line.strip().split()
            if len(parts) == 2 and '-' in parts[0]:
                period = parts[0].split('-')[1].zfill(4)
                code = parts[1].zfill(5)
                # tag = '③' if len(set(code[-3:])) < 3 else '⑥'
                tag = get_tag(code, enable_tag, tag_style)
                span_sum = ""
                if show_span_sum:
                    digits = [int(d) for d in code]
                    span = max(digits) - min(digits)
                    total = sum(digits)
                    span_sum = f" 跨{span} 和{total}"
                lines.append(f"{i+1} 【{code}】{tag} {span_sum}")

                all_digits.extend(list(code))  # 收集每个数字用于统计

    # 统计数字频率
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
    # print(f"[debug] final_code_text = {final_text}")
    return final_text, first_line


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

def send_message_and_images(log_func=None, code_from_txt=None):
    # hwnds = find_windows_by_exe_path(TARGET_EXE_PATH)
    hwnds = find_windows_by_exe_path( CONFIG_JSON.get("oldqq_exe_path", "") )
    if not hwnds:
        if log_func: log_func("未找到目标程序对应窗口")
        return

    hwnd = hwnds[0]
    win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
    x, y, w, h = 100, 100, 500, 500
    win32gui.MoveWindow(hwnd, x, y, w, h, True)
    time.sleep(0.5)

    textbox_rel = (50, 450)
    sendbtn_rel = (450, 466)

    click_textbox_x = x + textbox_rel[0]
    click_textbox_y = y + textbox_rel[1]
    click_sendbtn_x = x + sendbtn_rel[0]
    click_sendbtn_y = y + sendbtn_rel[1]

    # if log_func: log_func("点击文本框...")
    # pyautogui.click(click_textbox_x, click_textbox_y)
    # time.sleep(0.1)

    # if log_func: log_func("输入123...")
    # pyautogui.write("123", interval=0.1)
    # time.sleep(0.1)

    # if log_func: log_func("点击发送按钮...")
    # pyautogui.click(click_sendbtn_x, click_sendbtn_y)
    # time.sleep(0.3)

    # 发送从 txt 提取的内容
    if code_from_txt:
        if log_func: log_func(f"发送代码总文本")
        pyautogui.click(click_textbox_x, click_textbox_y)
        time.sleep(0.1)
        # pyautogui.write(code_from_txt, interval=0.01)
        # 设置剪贴板内容
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, code_from_txt)
        win32clipboard.CloseClipboard()

        # 粘贴剪贴板内容（Ctrl+V）
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyautogui.click(click_sendbtn_x, click_sendbtn_y)
        time.sleep(0.5)

    time.sleep(0.9)

    for img_url in [
        "http://101.132.131.209:6712/zhongying",
        "http://101.132.131.209:6712/yintianxia",
    ]:
        if log_func: log_func(f"发送图片: {img_url}")
        download_image_to_clipboard(img_url)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        # pyautogui.click(click_sendbtn_x, click_sendbtn_y)
        # time.sleep(0.3)
    
    pyautogui.click(click_sendbtn_x, click_sendbtn_y)
    time.sleep(0.3)



class FileWatcherApp:
    def get_current_config(self):
        return {
            "oldqq_exe_path": self.qq_exe_path_var.get(),
            "target_txt_path": self.target_txt_path_var.get(),
            "code_count": int(self.code_count_var.get()),
            "enable_send": self.enable_send_var.get(),
            "prefix_text": self.prefix_text_var.get().strip(),
            "enable_tag": self.enable_tag_var.get(),
            "tag_style": self.tag_style_var.get(),
            "show_span_sum": self.show_span_sum_var.get()
        }

    def __init__(self, root):
        self.root = root
        self.root.title("[VincentZyu]监控txt文件+发送QQ")

        self.last_mtime = None  # 这里初始化
        
        self.qq_exe_path_var = tk.StringVar(value=CONFIG_JSON.get("oldqq_exe_path"))
        self.target_txt_path_var = tk.StringVar(value=CONFIG_JSON.get("target_txt_path"))

        # 路径选择区
        path_frame = tk.LabelFrame(root, text="路径设置", padx=10, pady=5)
        path_frame.pack(fill='x', padx=10, pady=(10, 5))

        tk.Label(path_frame, text="QQ 可执行文件路径:").grid(row=1, column=0, sticky='w')
        self.qq_path_entry = tk.Entry(path_frame, textvariable=self.qq_exe_path_var, width=60)
        self.qq_path_entry.grid(row=1, column=1, sticky='we', padx=(5, 0))
        tk.Button(path_frame, text="浏览", command=self.select_qq_exe).grid(row=1, column=2, padx=5)


        tk.Label(path_frame, text="选择 txt 文件路径:").grid(row=0, column=0, sticky='w')
        self.target_txt_path_entry = tk.Entry(path_frame, textvariable=self.target_txt_path_var, width=60)
        self.target_txt_path_entry.grid(row=0, column=1, sticky='we', padx=(5, 0))
        tk.Button(path_frame, text="浏览", command=self.select_file).grid(row=0, column=2, padx=5)
        path_frame.columnconfigure(1, weight=1)

        # 参数设置区
        param_frame = tk.LabelFrame(root, text="发送参数", padx=10, pady=5)
        param_frame.pack(fill='x', padx=10, pady=(0, 5))

        tk.Label(param_frame, text="发送前 N 行:").grid(row=0, column=0, sticky='w')
        self.code_count_var = tk.StringVar(value=str(CONFIG_JSON.get("code_count")))
        tk.Entry(param_frame, textvariable=self.code_count_var, width=8).grid(row=0, column=1, sticky='w', padx=(0, 10))

        self.enable_send_var = tk.BooleanVar(value=bool(CONFIG_JSON.get("enable_send")))
        tk.Checkbutton(param_frame, text="启用发送 QQ 消息", variable=self.enable_send_var).grid(row=0, column=2, sticky='w', padx=(0, 10))

        tk.Label(param_frame, text="开头文字:").grid(row=1, column=0, sticky='w')
        self.prefix_text_var = tk.StringVar(value=str(CONFIG_JSON.get("prefix_text")))
        tk.Entry(param_frame, textvariable=self.prefix_text_var, width=40).grid(row=1, column=1, columnspan=2, sticky='we', pady=2)

        self.enable_tag_var = tk.BooleanVar(value=CONFIG_JSON.get("enable_tag"))
        tk.Checkbutton(param_frame, text="加尾部 36tag", variable=self.enable_tag_var).grid(row=2, column=0, sticky='w')

        tk.Label(param_frame, text="tag 样式:").grid(row=2, column=1, sticky='e')
        self.tag_style_var = tk.StringVar(value="空心36_③⑥")
        tk.OptionMenu(param_frame, self.tag_style_var, "空心36_③⑥", "罗马数字36_ⅢⅥ", "实心36_❸❻", "括号36_⑶⑹", "序号36_⒊⒍").grid(row=2, column=2, sticky='w')

        self.show_span_sum_var = tk.BooleanVar(value=False)
        tk.Checkbutton(param_frame, text="显示 跨 / 和", variable=self.show_span_sum_var).grid(row=3, column=0, sticky='w', pady=(2, 0))

        # 操作按钮区
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', padx=10, pady=(0, 5))
        tk.Button(btn_frame, text="手动发送 数字 + 图片", command=self.trigger_send).pack(anchor='w')

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
            time.sleep(1)

    def trigger_send(self):
        self.log("开始执行发送...")
        # threading.Thread(target=send_message_and_images, args=(self.log,), daemon=True).start()
        try:
            code_count = int(self.code_count_var.get())
        except ValueError:
            self.log("code_count 输入无效，使用默认值 14")
            code_count = 14

        enable_send = self.enable_send_var.get()
        file_path = self.target_txt_path_var.get()

        # 获取提取的文本代码（例如 0159\t14165）
        # extracted, latest_code = extract_codes(file_path, code_count)
        enable_tag = self.enable_tag_var.get()
        tag_style = self.tag_style_var.get()
        show_span_sum = self.show_span_sum_var.get()
        prefix_text = self.prefix_text_var.get().strip()
        extracted, latest_code = extract_codes(file_path, code_count, enable_tag, tag_style, show_span_sum)
        if prefix_text:
            extracted = prefix_text + "\n" + extracted

        self.log(f"提取前 {code_count} 行 code：\n 最新一期: {latest_code}")

        if not enable_send:
            self.log("发送已禁用，仅输出日志")
            return

        def do_send():
            send_message_and_images(self.log, code_from_txt=extracted)

        threading.Thread(target=do_send, daemon=True).start()

    def stop(self):
        self.running = False



if __name__ == "__main__":
    CONFIG_JSON = load_config()
    root = tk.Tk()
    app = FileWatcherApp(root)

    app.running = True
    threading.Thread(target=app.watch_file, daemon=True).start()

    root.protocol("WM_DELETE_WINDOW", lambda: (save_config(app.get_current_config()), app.stop(), root.destroy()))
    root.mainloop()
