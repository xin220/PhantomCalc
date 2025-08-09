import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import os
import threading
import time
import ctypes

# ====== 全局变量定义 ======
PROTECTION_ACTIVE = True
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def protect_process():
    """后台进程保护线程"""
    global PROTECTION_ACTIVE
    
    while PROTECTION_ACTIVE:
        # 直接启动前台计算器
        try:
            exe_path = os.path.abspath(sys.argv[0])
            # 使用新的启动方式确保前台进程可见
            os.system(f'start pythonw "{exe_path}" --foreground')
        except Exception as e:
            print(f"重启失败: {e}")
        
        time.sleep(5)  # 每5秒检查一次

def disable_close_button(hwnd):
    """禁用关闭按钮 - 添加更多错误处理"""
    try:
        # 检查窗口句柄是否有效
        if not user32.IsWindow(hwnd):
            print(f"无效窗口句柄: {hwnd}")
            return
            
        # 获取系统菜单
        h_menu = user32.GetSystemMenu(hwnd, 0)
        if h_menu:
            # 禁用关闭菜单项
            user32.EnableMenuItem(h_menu, 0xF060, 1)  # SC_CLOSE
            # 重绘菜单
            user32.DrawMenuBar(hwnd)
    except Exception as e:
        print(f"禁用关闭按钮时出错: {e}")

def hotkey_listener():
    """Alt+Esc热键监听线程 - 使用原生API"""
    global PROTECTION_ACTIVE
    
    VK_MENU = 0x12  # Alt键
    VK_ESCAPE = 0x1B  # Esc键
    
    while PROTECTION_ACTIVE:
        # 检查Alt和Esc键是否被按下
        alt_pressed = user32.GetAsyncKeyState(VK_MENU) & 0x8000 != 0
        esc_pressed = user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000 != 0
        
        if alt_pressed and esc_pressed:
            PROTECTION_ACTIVE = False
            print("检测到Alt+Esc，退出程序")
            os._exit(0)
        
        time.sleep(0.1)

# ====== 计算器功能代码 ======
def create_calculator_gui(root):
    """创建计算器界面"""
    # 历史记录存储
    history = []
    
    # 计算函数
    def calculate():
        try:
            expression = entry.get()
            if not expression:
                return
                
            # 检查无效字符
            valid_chars = "0123456789.+-*/() "
            if any(char not in valid_chars for char in expression):
                messagebox.showerror("错误", "包含无效字符！")
                return
                
            result = eval(expression)
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
            
            history.append(f"{expression} = {result}")
            update_history_display()
            
        except ZeroDivisionError:
            messagebox.showerror("错误", "不能除以零！")
        except Exception as e:
            messagebox.showerror("错误", f"计算错误: {str(e)}")
    
    # 其他UI函数
    def add_to_expression(char):
        current = entry.get()
        entry.delete(0, tk.END)
        entry.insert(tk.END, current + char)

    def clear_expression():
        entry.delete(0, tk.END)

    def delete_last_char():
        current = entry.get()
        if current:
            entry.delete(len(current)-1, tk.END)

    def clear_history():
        nonlocal history
        history = []
        history_text.config(state=tk.NORMAL)
        history_text.delete(1.0, tk.END)
        history_text.config(state=tk.DISABLED)

    def update_history_display():
        history_text.config(state=tk.NORMAL)
        history_text.delete(1.0, tk.END)
        
        for item in history[-10:]:
            history_text.insert(tk.END, item + "\n")
        
        history_text.config(state=tk.DISABLED)
        history_text.see(tk.END)

    # ====== 界面布局 ======
    # 主框架
    calc_frame = tk.Frame(root)
    calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 输入框
    entry = tk.Entry(calc_frame, font=('Arial', 18), justify='right', bd=5)
    entry.grid(row=0, column=0, columnspan=4, sticky='ew', padx=5, pady=5)

    # 按钮
    buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        '0', '.', '=', '+'
    ]
    
    # 按钮命令映射
    special_buttons = {
        '=': calculate,
        'C': clear_expression
    }
    
    # 创建按钮
    row, col = 1, 0
    for button in buttons:
        if button in special_buttons:
            cmd = special_buttons[button]
            btn = tk.Button(calc_frame, text=button, font=('Arial', 14), 
                           command=cmd, bg='#e0e0e0')
        else:
            btn = tk.Button(calc_frame, text=button, font=('Arial', 14),
                           command=lambda char=button: add_to_expression(char))
        
        btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        col += 1
        if col > 3:
            col = 0
            row += 1

    # 删除按钮
    delete_btn = tk.Button(calc_frame, text='DEL', font=('Arial', 14), 
                          command=delete_last_char, bg='#ffcc99')
    delete_btn.grid(row=5, column=0, sticky='nsew', padx=5, pady=5)
    
    # 清除按钮
    clear_btn = tk.Button(calc_frame, text='C', font=('Arial', 14), 
                         command=clear_expression, bg='#ffcccc')
    clear_btn.grid(row=5, column=1, sticky='nsew', padx=5, pady=5)
    
    # 括号区域
    bracket_frame = tk.Frame(calc_frame)
    bracket_frame.grid(row=5, column=2, columnspan=2, sticky='nsew')
    tk.Button(bracket_frame, text='(', font=('Arial', 14),
             command=lambda: add_to_expression('(')).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    tk.Button(bracket_frame, text=')', font=('Arial', 14),
             command=lambda: add_to_expression(')')).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 历史记录区域
    history_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
    history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

    # 历史记录标题
    history_label = tk.Label(history_frame, text="历史记录", font=('Arial', 10, 'bold'))
    history_label.pack(pady=(5, 0))

    # 历史记录文本框
    history_text = scrolledtext.ScrolledText(
        history_frame, 
        width=20, 
        height=15,
        font=('Arial', 10),
        state=tk.DISABLED
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
    
    # 署名
    signature = tk.Label(
        calc_frame, 
        text="by [星语心愿]",  
        font=('Arial', 8),
        fg='gray'
    )
    signature.grid(row=6, column=0, columnspan=4, sticky='se', padx=10, pady=5)

# ====== 主程序入口 ======
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--foreground':
        # 前台计算器模式
        root = tk.Tk()
        root.title("计算器")
        root.geometry("500x400")
        
        # 设置窗口置顶
        root.attributes('-topmost', True)
        
        # 创建计算器界面
        create_calculator_gui(root)
        
        # 确保窗口完全创建后再获取句柄
        def after_startup():
            # 获取窗口句柄 - 使用更可靠的方式
            hwnd = int(root.wm_frame(), 16)
            if hwnd:
                disable_close_button(hwnd)
                
                # 重写关闭行为
                def on_close():
                    # 只是隐藏窗口，而不是真正关闭
                    root.withdraw()
                    root.after(1000, root.deiconify)  # 1秒后重新显示
                
                root.protocol("WM_DELETE_WINDOW", on_close)
        
        root.after(500, after_startup)  # 延迟半秒确保窗口创建完成
        
        # 运行主循环
        root.mainloop()
        
    else:
        # 后台保护模式
        # 隐藏控制台窗口（仅Windows）
        if sys.platform == "win32":
            console_window = kernel32.GetConsoleWindow()
            if console_window:
                user32.ShowWindow(console_window, 0)  # 0 表示隐藏控制台
        
        # 启动前台计算器 - 使用新方式确保可见
        exe_path = os.path.abspath(sys.argv[0])
        os.system(f'start pythonw "{exe_path}" --foreground')
        
        # 启动保护线程
        protection_thread = threading.Thread(target=protect_process, daemon=True)
        protection_thread.start()
        
        # 启动热键监听线程
        hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
        hotkey_thread.start()
        
        # 保持主线程运行
        try:
            while PROTECTION_ACTIVE:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
