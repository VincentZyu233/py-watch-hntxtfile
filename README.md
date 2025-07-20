# VincentZyu 的 QQ 消息自动发送工具
![logo](gui_program/assets/logo.png)


一个基于 Python 的小工具，用于监控 txt 文件内容变化，并自动将更新的内容以及图片发送到指定 QQ 窗口。

## 功能

*   **文件监控**: 实时监控指定 txt 文件的修改，一旦内容更新，立即触发发送。
*   **内容提取**: 可以指定从 txt 文件中提取前 N 行内容。
*   **自动发送**: 将提取的文本内容和预设的图片自动发送到指定的 QQ 窗口。
*   **灵活配置**: 提供图形界面，方便配置 QQ 可执行文件路径、监控文件路径、发送行数、是否启用发送、消息前缀、尾部 tag 样式等。
*   **尾部 Tag**: 可选择在发送的代码后自动添加尾部 Tag，支持多种样式（空心36_③⑥、罗马数字36_ⅢⅥ 等）。
*   **统计信息**: 可显示提取代码的数字热度统计（热/温/冷数字）。
*   **跨/和**: 可选择显示提取代码的跨度和和值。

## 使用方法

1.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
    (你需要创建一个 requirements.txt 文件，包含所需的第三方库，例如 `PyYAML`, `tkinter`, `Pillow`, `requests`, `psutil`, `pyautogui`, `pywin32`)
2.  运行 `main.py`。
3.  在 GUI 界面中配置相关参数，包括：
    *   QQ 可执行文件路径
    *   目标 txt 文件路径
    *   发送行数
    *   是否启用发送
    *   消息前缀
    *   是否添加尾部 tag 及 tag 样式
4.  程序会自动监控文件变化并发送消息。

## 注意事项

*   请确保已安装所有必要的 Python 库。
*   请正确配置 QQ 可执行文件路径和目标 txt 文件路径。
*   本工具基于 `pyautogui` 库模拟鼠标键盘操作，请确保电脑上已安装并配置好相关环境。
*   程序会将配置保存到 `config.yaml` 文件中，下次启动时自动加载。

## 开发

### 创建虚拟环境&写依赖
```bash
python -m venv venv
pip freeze > requirements.txt
```

### 打包

本项目使用 `PyInstaller` 打包成独立可执行文件：

```bash
./venv/Scripts/Activate # Powershell
./venv/bin/activate # Linux bash
cd gui_program
pyinstaller --onefile --windowed --icon=assets/logo.ico --add-data "assets/logo.png;assets" --name=20250720v3_检测txt变化发旧版qq河内五分彩 main.py
```

## 作者

VincentZyu