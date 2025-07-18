import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import os
import time
import threading

DEFAULT_FILE_PATH = r"G:\GGames\Minecraft\shuyeyun\qq-bot\miao-qinghuitou\恒行5挂机软件\OpenCode\HN5FC.txt"

class FileWatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Txt 文件监控")

        # 路径选择
        self.path_var = tk.StringVar(value=DEFAULT_FILE_PATH)

        tk.Label(root, text="选择 txt 文件路径:").pack(anchor='w', padx=10, pady=(10, 0))

        path_frame = tk.Frame(root)
        path_frame.pack(fill='x', padx=10)

        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var, width=80)
        self.path_entry.pack(side='left', fill='x', expand=True)

        tk.Button(path_frame, text="浏览", command=self.select_file).pack(side='left', padx=5)

        # 只读 console
        tk.Label(root, text="Console 输出:").pack(anchor='w', padx=10, pady=(10, 0))

        self.console = ScrolledText(root, height=15, state='disabled')
        self.console.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 启动监控线程
        self.last_mtime = None
        self.running = True
        threading.Thread(target=self.watch_file, daemon=True).start()

        self.log(f"[INFO] 程序启动，正在监控文件变动。")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.path_var.set(path)
            self.last_mtime = None  # 重置上次修改时间
            self.log(f"[INFO] 已切换监控路径为：{path}")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[INFO] {timestamp} {message}\n"
        self.console.configure(state='normal')
        self.console.insert(tk.END, full_message)
        self.console.configure(state='disabled')
        self.console.see(tk.END)

    def watch_file(self):
        while self.running:
            path = self.path_var.get()
            if os.path.isfile(path):
                try:
                    mtime = os.path.getmtime(path)
                    if self.last_mtime is None:
                        self.last_mtime = mtime
                    elif mtime != self.last_mtime:
                        self.last_mtime = mtime
                        self.log("txt 被修改了！")
                except Exception as e:
                    self.log(f"监控文件时出错：{e}")
            time.sleep(1)  # 每秒检查一次

    def stop(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = FileWatcherApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()
