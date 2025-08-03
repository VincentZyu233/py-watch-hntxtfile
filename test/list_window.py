import pygetwindow as gw
import psutil
import win32process

# 获取所有窗口
all_windows = gw.getAllWindows()

print(f"共找到 {len(all_windows)} 个窗口：\n")

for i, win in enumerate(all_windows, start=1):
    print(f"窗口 {i}:")
    print(f"  标题(title): {win.title}")
    print(f"  坐标(left, top): ({win.left}, {win.top})")
    print(f"  大小(width x height): {win.width} x {win.height}")
    print(f"  是否可见(visible): {win.visible}")
    print(f"  是否激活(activated): {win.isActive}")
    print(f"  是否最大化(maximized): {win.isMaximized}")
    print(f"  是否最小化(minimized): {win.isMinimized}")
    
    hwnd = win._hWnd
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    p = psutil.Process(pid)

    exe_path = p.exe()
    exe_name = p.name()

    print(f"  Process ID: {pid}")
    print(f"  Executable Path: {exe_path}")
    print(f"  Executable Name: {exe_name}")
    print()

