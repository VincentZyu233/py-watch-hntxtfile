import sys
import shutil

def extract_assets_if_needed():
    """
    如果是打包的exe环境，在exe同级目录下释放assets文件夹
    """
    try:
        # 检查是否在PyInstaller打包环境中
        if hasattr(sys, '_MEIPASS'):
            # 获取exe文件所在目录
            exe_dir = os.path.dirname(sys.executable)
            assets_target_dir = os.path.join(exe_dir, "assets")
            
            # 如果assets目录不存在，则从打包资源中复制
            if not os.path.exists(assets_target_dir):
                assets_source_dir = os.path.join(sys._MEIPASS, "gui", "assets")
                if os.path.exists(assets_source_dir):
                    shutil.copytree(assets_source_dir, assets_target_dir)
                    print(f"已释放assets文件夹到: {assets_target_dir}")
                else:
                    print(f"警告: 打包资源中未找到assets目录: {assets_source_dir}")
    except Exception as e:
        print(f"释放assets文件夹时出错: {e}")

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径，兼容 PyInstaller 打包和开发环境。
    """
    try:
        # 如果是PyInstaller打包环境
        if hasattr(sys, '_MEIPASS'):
            # 优先使用exe同级目录下的assets
            exe_dir = os.path.dirname(sys.executable)
            local_path = os.path.join(exe_dir, relative_path)
            if os.path.exists(local_path):
                return local_path
            # 如果本地不存在，回退到打包资源
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # 在开发环境下，使用当前脚本所在目录的父目录作为基础路径
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relative_path)
    except Exception:
        # 在开发环境下，使用当前脚本所在目录的父目录作为基础路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

# 标准库
import os
import time
from enum import Enum
import threading
from collections import Counter
from io import BytesIO
import json

# 第三方库
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
import pygetwindow as gw
from PIL import Image, ImageTk
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
    "count_text_entries": 14,
    "count_hot_warm_cold": 30,
    "enable_send": True,
    "prefix_text": "推送hn300信息",
    "enable_tag": True,
    "tag_style": "空心36_③⑥",
    "show_span_sum": False,
    "span_sum_use_circle_style": False,
    "img_server_url": "http://101.132.131.209:6712",
    "enable_send_text": True,
    "enable_send_images": True 
}

CONFIG_FILE = "./config.yaml"

def load_version_info():
    """从 metadata.json 文件加载版本信息"""
    try:
        metadata_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "medatada.json")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            return metadata.get("version", "v1"), metadata.get("data", "unknown")
    except Exception as e:
        print(f"加载版本信息失败: {e}")
        return "v1", "unknown"

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
            if loaded_config:
                config.update(loaded_config)
    return config

def save_config(config):
    try:
        print(f"正在保存配置到: {os.path.abspath(CONFIG_FILE)}")
        print(f"配置内容: {config}")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True)
        print(f"配置保存成功！文件路径: {os.path.abspath(CONFIG_FILE)}")
    except Exception as e:
        print(f"保存配置时出错: {e}")
        import traceback
        traceback.print_exc()


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


def extract_codes(
    log_func, 
    path, 
    countTextEntries, countHotWarmCold,
    enable_tag, tag_style, show_span_sum, span_sum_use_circle_style
):
    first_line_content = ""
    all_processed_lines = [] # 存储所有处理过的行数据

    if not os.path.exists(path):
        if log_func:
            log_func(f"❌ 错误：txt 文件路径不存在：{path}")
        return "", ""

    with open(path, 'r', encoding='utf-8') as f:
        max_count = max(countTextEntries, countHotWarmCold)
        for i, line in enumerate(f):
            if i > max_count:
                break
            stripped_line = line.strip()
            if not stripped_line:
                continue
            parts = stripped_line.split()
            if len(parts) != 2:
                if log_func:
                    log_func(f"Warning: Skipped malformed line (expected 2 parts, got {len(parts)}): {stripped_line}")
                continue
            all_processed_lines.append(parts)
        
    lines_for_display = []
    all_digits_for_text_display = []
    for parts in all_processed_lines[-countTextEntries:]:
        period_raw = parts[0]
        code = parts[1].zfill(5)
        period = period_raw[-3:]

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

        lines_for_display.append(f"{period} 【{code}】{tag} {span_sum_text}")
        all_digits_for_text_display.extend(list(code))
    lines_for_display = lines_for_display[::-1]

    all_digits_for_hot_warm_cold = []
    for parts in all_processed_lines[-countHotWarmCold:]:
        code = parts[1].zfill(5)
        all_digits_for_hot_warm_cold.extend(list(code))
    digit_freq = Counter(all_digits_for_hot_warm_cold)
    sorted_digits = digit_freq.most_common()

    hot = [d for d, _ in sorted_digits[:3]]
    warm = [d for d, _ in sorted_digits[3:7]]
    cold = [d for d, _ in sorted_digits[7:10]]

    stat_text = "----------------\n"
    stat_text += f"热：{' '.join(hot)}\n"
    stat_text += f"温：{' '.join(warm)}\n"
    stat_text += f"冷：{' '.join(cold)}\n"
    stat_text += "----------------"

    final_text = "\n".join(lines_for_display) + "\n" + stat_text
    return final_text, first_line_content

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


def send_message_and_images(
        log_func, 
        code_from_txt, 
        exe_path, 
        target_titles, 
        img_server_url,
        enable_send_text, 
        enable_send_images
    ):
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

        # 1. 保存窗口当前状态
        # 获取窗口信息，判断是否最小化
        window_placement = win32gui.GetWindowPlacement(hwnd)
        # window_placement[1] 是显示状态 (SW_SHOWNORMAL, SW_SHOWMINIMIZED, SW_SHOWMAXIMIZED)
        was_minimized = (window_placement[1] == win32con.SW_SHOWMINIMIZED)
        
        # 2. 强制置顶并还原窗口
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) # 还原窗口（如果最小化）
        win32gui.SetForegroundWindow(hwnd) # 将窗口置于前台
        # 这一行是关键，确保窗口在所有其他窗口之上，可以被 pyautogui 看到和操作
        win32gui.BringWindowToTop(hwnd) # 确保窗口在 Z 序的顶部
        time.sleep(0.3) # 给予窗口足够的还原和置顶时间

        # 3. 计算新的窗口坐标并移动 (保持不变)
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

        # 4. 更新下一个窗口的偏移量
        offset_x += increment_x
        offset_y += increment_y

        textbox_rel = (50, 450)
        sendbtn_rel = (450, 466)
        click_textbox_x = new_x + textbox_rel[0]
        click_textbox_y = new_y + textbox_rel[1]
        click_sendbtn_x = new_x + sendbtn_rel[0]
        click_sendbtn_y = new_y + sendbtn_rel[1]

        # 5. 输入文本内容
        if enable_send_text:
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
        else:
            if log_func: log_func(f"🚫 已禁用向「{title}」发送文字。")

        # 6. 发送图片 
        if enable_send_images:
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
            time.sleep(0.1)
        else:
            if log_func: log_func(f"🚫 已禁用向「{title}」发送图片。")

        # 7. 恢复窗口原始状态 (如果之前是最小化的，则最小化回去)
        if was_minimized:
            if log_func: log_func(f"将窗口「{title}」重新最小化。")
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            time.sleep(0.2) # 给予时间让窗口最小化



class FileWatcherApp:
    def get_current_config(self):
        return {
            "oldqq_exe_path": self.qq_exe_path_var.get(),
            "target_txt_path": self.target_txt_path_var.get(),
            "qq_window_titles": self.qq_window_titles_var.get().strip(),
            "count_text_entries": int(self.count_text_entries_var.get()),
            "count_hot_warm_cold": int(self.count_hot_warm_cold_var.get()),
            "enable_send": self.enable_send_var.get(),
            "prefix_text": self.prefix_text_var.get().strip(),
            "enable_tag": self.enable_tag_var.get(),
            "tag_style": self.tag_style_var.get(),
            "show_span_sum": self.show_span_sum_var.get(),
            "span_sum_use_circle_style": self.span_sum_use_circle_style_var.get(),
            "img_server_url": self.img_server_url_var.get().strip(),
            "enable_send_text": self.enable_send_text_var.get(),
            "enable_send_images": self.enable_send_images_var.get(),
        }

    def __init__(self, root):

        self.root = root
        version, date = load_version_info()
        self.root.title(f"[{date}{version}][VincentZyu]监控txt文件+发送QQ")

        # 设置窗口图标
        try:
            icon_path = get_resource_path("gui/assets/logo.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"设置窗口图标失败: {e}")

        self.last_mtime = None  # 这里初始化
        
        self.qq_exe_path_var = tk.StringVar(value=CONFIG_JSON.get("oldqq_exe_path"))
        self.target_txt_path_var = tk.StringVar(value=CONFIG_JSON.get("target_txt_path"))

        # 顶部标题区域
        header_frame = tk.Frame(root)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))

        # 加载并显示 logo
        try:
            logo_path = get_resource_path("gui/assets/logo.png")
            logo_image = Image.open(logo_path)
            # 调整图片大小
            logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            logo_label = tk.Label(header_frame, image=self.logo_photo)
            logo_label.pack(side='left', padx=(0, 10))
        except Exception as e:
            print(f"加载 logo 失败: {e}")
            print(f"请确保 gui/assets/logo.png 文件存在。")

        # 标题文字
        title_label = tk.Label(header_frame, text="监控txt 控制旧版qq发消息 工具", 
                              font=("Microsoft YaHei", 16, "bold"), 
                              fg="#2E86AB")
        title_label.pack(side='left', anchor='w')

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


        tk.Label(param_frame, text="发送最新多少期文本：").grid(row=1, column=0, sticky='w')
        self.count_text_entries_var = tk.StringVar(value=str(CONFIG_JSON.get("count_text_entries")))
        self.count_hot_warm_cold_var = tk.StringVar(value=str(CONFIG_JSON.get("count_hot_warm_cold")))
        ttk.Entry(param_frame, textvariable=self.count_text_entries_var, width=8).grid(row=1, column=1, sticky='w', padx=(0, 10))

        tk.Label(param_frame, text="热温冷统计期数:").grid(row=5, column=0, sticky='w')
        ttk.Entry(param_frame, textvariable=self.count_hot_warm_cold_var, width=8).grid(row=5, column=1, sticky='w', padx=(0, 10))

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
        tk.Label(param_frame, text="图片服务器地址:").grid(row=8, column=0, sticky='w')
        self.img_server_url_var = tk.StringVar(value=CONFIG_JSON.get("img_server_url"))
        ttk.Entry(param_frame, textvariable=self.img_server_url_var, width=40).grid(row=8, column=1, columnspan=2, sticky='we', pady=2)

        # 在图片服务器地址输入框下方添加说明文字
        tk.Label(param_frame, text="格式是 http(s)://ip:port，末尾没有斜杠", fg="red").grid(row=9, column=0, columnspan=3, sticky='w')

        self.enable_send_text_var = tk.BooleanVar(value=CONFIG_JSON.get("enable_send_text", True)) # Default to True
        self.enable_send_images_var = tk.BooleanVar(value=CONFIG_JSON.get("enable_send_images", True)) # Default to True

        self.enable_send_text_checkbox = ttk.Checkbutton(param_frame, text="是否发送文字", variable=self.enable_send_text_var)
        self.enable_send_text_checkbox.grid(row=10, column=0, sticky='w', pady=(5, 0)) # Adjust row number as needed

        self.enable_send_images_checkbox = ttk.Checkbutton(param_frame, text="是否发送图片", variable=self.enable_send_images_var)
        self.enable_send_images_checkbox.grid(row=10, column=1, sticky='w', pady=(5, 0), columnspan=2) # Adjust row and column as needed


        # 操作按钮区
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', padx=10, pady=(0, 5))
        ttk.Button(btn_frame, text="点我手动发送", command=self.trigger_send).pack(anchor='w')

        # Console输出区
        tk.Label(root, text="Console 输出:").pack(anchor='w', padx=10, pady=(5, 0))
        self.console = ScrolledText(root, height=15, state='disabled')
        self.console.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.console.tag_config("info", foreground="blue")       # 信息消息
        self.console.tag_config("warning", foreground="orange")  # 警告消息
        self.console.tag_config("error", foreground="red", font=("TkDefaultFont", 9, "bold")) # 错误消息，加粗
        self.console.tag_config("success", foreground="green")   # 成功消息
        self.console.tag_config("normal", foreground="black")    # 默认黑色文本
    
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

    def log(self, message, level="INFO"): # Added a 'level' parameter with default 'INFO'
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine the tag based on the message content or provided level
        tag = "normal" # Default tag
        if "❌ 错误" in message or "Error" in message or level == "ERROR":
            tag = "error"
            formatted_level = "ERROR"
        elif "⚠️" in message or "Warning" in message or level == "WARNING":
            tag = "warning"
            formatted_level = "WARN"
        elif "✅" in message or "Success" in message or level == "SUCCESS":
            tag = "success"
            formatted_level = "SUCCESS"
        elif "🔍" in message or level == "DEBUG":
            tag = "info" # Use info color for debug/search messages
            formatted_level = "DEBUG"
        else: # Default for regular info messages
            tag = "info"
            formatted_level = "INFO"

        full_message = f"[{formatted_level}] {timestamp} {message}\n"
        self.console.configure(state='normal')
        # Insert the message with the determined tag
        self.console.insert(tk.END, full_message, tag) 
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
        count_text_entries = int(self.count_text_entries_var.get())
        count_hot_warm_cold = int(self.count_hot_warm_cold_var.get())
        enable_send = self.enable_send_var.get()
        prefix_text = self.prefix_text_var.get().strip()
        enable_tag = self.enable_tag_var.get()
        tag_style = self.tag_style_var.get()
        show_span_sum = self.show_span_sum_var.get()
        span_sum_use_circle_style = self.span_sum_use_circle_style_var.get()
        enable_send_text = self.enable_send_text_var.get()
        enable_send_images = self.enable_send_images_var.get()
        enable_send_text = self.enable_send_text_var.get()
        enable_send_images = self.enable_send_images_var.get()

        extracted, latest_code = extract_codes(
            self.log, 
            file_path, 
            count_text_entries, count_hot_warm_cold,
            enable_tag, tag_style, show_span_sum, span_sum_use_circle_style
        )
        if prefix_text:
            extracted = prefix_text + "\n" + extracted

        self.log(f"提取前 {count_text_entries} 行 code：\n 最新一期: {latest_code}")

        if not enable_send:
            self.log("发送已禁用，仅输出日志")
            return
        
        img_server_url = self.img_server_url_var.get().strip()
        def do_send():
            send_message_and_images(
                log_func = self.log, 
                code_from_txt=extracted, 
                exe_path=qq_exe_path, 
                target_titles=target_titles, 
                img_server_url = img_server_url,
                enable_send_text = enable_send_text, 
                enable_send_images = enable_send_images
            )

        threading.Thread(target=do_send, daemon=True).start()

    def stop(self):
        self.running = False



if __name__ == "__main__":
    # 如果是打包环境，首次运行时释放assets文件夹
    extract_assets_if_needed()
    
    CONFIG_JSON = load_config()
    style = Style("flatly")  # 你可以换成 'superhero', 'cyborg', 'journal' 等等
    root = style.master 
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
