import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import os
import random
import ctypes
import win32gui
import win32process
import win32con
import win32api
import time
import threading

# 添加全局变量存储历史记录
history = []
hidden = False  # 窗口隐藏状态
password = "123456"  # 默认解锁密码

# 修改进程名为普通系统进程名
def disguise_process():
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.SetConsoleTitleW("svchost.exe")
        except:
            pass

# 窗口扰动技术 - 防止截图/录屏
def disturb_window():
    while True:
        if not hidden:
            # 随机改变窗口位置
            x = random.randint(0, win32api.GetSystemMetrics(0) - 500)
            y = random.randint(0, win32api.GetSystemMetrics(1) - 400)
            root.geometry(f"+{x}+{y}")
        time.sleep(0.1)  # 每0.1秒移动一次

# 隐藏/显示窗口的热键处理
def register_hotkey():
    if sys.platform == "win32":
        try:
            # 注册Ctrl+Alt+Shift+H作为切换键
            if not ctypes.windll.user32.RegisterHotKey(None, 1, win32con.MOD_CONTROL | win32con.MOD_ALT | win32con.MOD_SHIFT, win32con.VK_H):
                messagebox.showwarning("警告", "热键注册失败")
            
            # 创建消息循环
            msg = win32gui.GetMessage(None, 0, 0)
            while True:
                if win32gui.PeekMessage(msg, 0, 0, win32con.PM_REMOVE):
                    if msg.message == win32con.WM_HOTKEY:
                        toggle_window()
                time.sleep(0.1)
        except Exception as e:
            print(f"热键错误: {e}")

# 切换窗口可见性
def toggle_window():
    global hidden
    hidden = not hidden
    
    if hidden:
        root.withdraw()  # 隐藏窗口
    else:
        # 解锁后才显示窗口
        if check_password():
            root.deiconify()  # 显示窗口
            # 窗口置顶
            root.attributes('-topmost', True)
            root.after_idle(root.attributes, '-topmost', False)
        else:
            hidden = True  # 密码错误保持隐藏

# 检查密码
def check_password():
    # 简化版密码检查，实际应用中应使用更安全的方法
    pwd = simpledialog.askstring("解锁", "输入解锁密码:", show='*')
    return pwd == password

# 修改窗口样式属性
def modify_window_style():
    if sys.platform == "win32":
        try:
            hwnd = win32gui.FindWindow(None, "一个简单的计算器")
            # 移除窗口边框
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~win32con.WS_BORDER
            style &= ~win32con.WS_DLGFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
            
            # 设置窗口透明
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                  win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                                  win32con.WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        except:
            pass

def calculate():
    """执行计算并显示结果，并保存到历史记录"""
    try:
        expression = entry.get()
        if not expression:
            return
            
        # 安全评估表达式
        if any(char not in '0123456789.+-*/() ' for char in expression):
            messagebox.showerror("错误", "包含无效字符！")
            return
            
        result = eval(expression)
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
        
        # 添加到历史记录并更新显示
        history.append(f"{expression} = {result}")
        update_history_display()
        
    except ZeroDivisionError:
        messagebox.showerror("错误", "不能除以零！")
    except Exception as e:
        messagebox.showerror("错误", f"计算错误: {str(e)}")

def add_to_expression(char):
    """向表达式添加字符"""
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + char)

def clear_expression():
    """清空输入框"""
    entry.delete(0, tk.END)

def delete_last_char():
    """删除最后一个字符"""
    current = entry.get()
    if current:
        entry.delete(len(current)-1, tk.END)

def clear_history():
    """清空历史记录"""
    global history
    history = []
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    history_text.config(state=tk.DISABLED)

def update_history_display():
    """更新历史记录显示"""
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    
    # 只显示最近的10条记录
    for item in history[-10:]:
        history_text.insert(tk.END, item + "\n")
    
    history_text.config(state=tk.DISABLED)
    history_text.see(tk.END)  # 滚动到底部

# 隐藏命令行窗口
if sys.platform == "win32":
    # 如果是Windows系统，隐藏命令行窗口
    import ctypes
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        # 隐藏控制台窗口
        ctypes.windll.user32.ShowWindow(whnd, 0)
        # 或者使用FreeConsole()来脱离控制台
        # ctypes.windll.kernel32.FreeConsole()

# 伪装进程名
disguise_process()

# 创建主窗口
root = tk.Tk()
root.title("一个简单的计算器")
root.geometry("500x400")  # 增加窗口宽度以容纳历史记录

# 设置字体
button_font = ('Arial', 14)
display_font = ('Arial', 18)

# 创建主框架（左侧计算器区域）
calc_frame = tk.Frame(root)
calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# 创建输入框
entry = tk.Entry(calc_frame, font=display_font, justify='right', bd=5)
entry.grid(row=0, column=0, columnspan=4, sticky='ew', padx=5, pady=5)

# 创建按钮网格
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', '.', '=', '+'
]

# 特殊按钮的处理函数
special_buttons = {
    '=': calculate,
    'C': clear_expression
}

row, col = 1, 0
for button in buttons:
    if button in special_buttons:
        cmd = special_buttons[button]
        btn = tk.Button(calc_frame, text=button, font=button_font, 
                        command=cmd, bg='#e0e0e0')
    else:
        btn = tk.Button(calc_frame, text=button, font=button_font,
                        command=lambda char=button: add_to_expression(char))
    
    btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
    col += 1
    if col > 3:
        col = 0
        row += 1

# 添加删除按钮
delete_btn = tk.Button(calc_frame, text='DEL', font=button_font, 
                       command=delete_last_char, bg='#ffcc99')
delete_btn.grid(row=5, column=0, sticky='nsew', padx=5, pady=5)

# 添加清除按钮
clear_btn = tk.Button(calc_frame, text='C', font=button_font, 
                      command=clear_expression, bg='#ffcccc')
clear_btn.grid(row=5, column=1, sticky='nsew', padx=5, pady=5)

# 添加括号按钮
parentheses = tk.Frame(calc_frame)
parentheses.grid(row=5, column=2, columnspan=2, sticky='nsew')
tk.Button(parentheses, text='(', font=button_font, 
          command=lambda: add_to_expression('(')).grid(row=0, column=0, sticky='nsew', padx=5)
tk.Button(parentheses, text=')', font=button_font, 
          command=lambda: add_to_expression(')')).grid(row=0, column=1, sticky='nsew', padx=5)

# 设置计算器区域网格行列权重
for i in range(7):
    calc_frame.grid_rowconfigure(i, weight=1)
for j in range(4):
    calc_frame.grid_columnconfigure(j, weight=1)

# 在计算器底部添加署名
signature = tk.Label(
    calc_frame, 
    text="by [星语心愿]",  
    font=('Arial', 8),
    fg='gray'
)
signature.grid(row=6, column=0, columnspan=4, sticky='se', padx=10, pady=5)

# ===== 添加历史记录区域 =====
history_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

# 历史记录标题
history_label = tk.Label(history_frame, text="历史记录", font=('Arial', 10, 'bold'))
history_label.pack(pady=(5, 0))

# 历史记录显示区域
history_text = scrolledtext.ScrolledText(
    history_frame, 
    width=20, 
    height=15,
    font=('Arial', 10),
    state=tk.DISABLED  # 设置为只读
)
history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# 清空历史按钮
clear_history_btn = tk.Button(
    history_frame, 
    text="清空历史", 
    font=('Arial', 9),
    command=clear_history
)
clear_history_btn.pack(pady=(0, 5))

# 修改窗口样式
if sys.platform == "win32":
    root.after(100, modify_window_style)

# 启动窗口扰动线程
disturb_thread = threading.Thread(target=disturb_window, daemon=True)
disturb_thread.start()

# 启动热键线程
hotkey_thread = threading.Thread(target=register_hotkey, daemon=True)
hotkey_thread.start()

# 运行主循环
root.mainloop()
