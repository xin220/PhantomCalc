import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import os
import threading
import time
import ctypes
import subprocess

# ====== 全局变量定义 ======
PROTECTION_ACTIVE = True

def protect_process():
    """后台进程保护线程 - 针对exe打包优化"""
    global PROTECTION_ACTIVE
    
    while PROTECTION_ACTIVE:
        try:
            # 获取当前exe路径
            exe_path = os.path.abspath(sys.executable if hasattr(sys, 'frozen') else sys.argv[0])
            
            # 检查前台进程是否运行
            foreground_running = False
            for proc in psutil.process_iter():
                try:
                    # 检查进程是否匹配
                    if proc.name() in ["pythonw.exe", "python.exe", os.path.basename(exe_path)]:
                        cmdline = " ".join(proc.cmdline()).lower()
                        if "calculator" in cmdline or os.path.basename(exe_path).lower() in cmdline:
                            foreground_running = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 如果前台进程没运行，则启动它
            if not foreground_running:
                # 打包后使用绝对路径启动
                if getattr(sys, 'frozen', False):
                    subprocess.Popen([exe_path, "--foreground"], creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen([exe_path, "--foreground"])
                
                print(f"启动前台进程: {exe_path}")
            
        except Exception as e:
            print(f"保护进程错误: {str(e)}")
        
        time.sleep(3)  # 每3秒检查一次

def disable_close_button(hwnd):
    """禁用关闭按钮 - 增加兼容性"""
    try:
        # 检查窗口句柄是否有效
        if not ctypes.windll.user32.IsWindow(hwnd):
            return False
            
        # 获取系统菜单
        h_menu = ctypes.windll.user32.GetSystemMenu(hwnd, 0)
        if h_menu:
            # 禁用关闭菜单项
            ctypes.windll.user32.EnableMenuItem(h_menu, 0xF060, 1)  # SC_CLOSE
            # 重绘菜单
            ctypes.windll.user32.DrawMenuBar(hwnd)
            return True
    except Exception as e:
        print(f"禁用关闭按钮错误: {str(e)}")
    return False

def hotkey_listener():
    """Alt+Esc热键监听线程 - 优化exe支持"""
    global PROTECTION_ACTIVE
    
    # 虚拟键码
    VK_ALT = 0x12
    VK_ESC = 0x1B
    
    while PROTECTION_ACTIVE:
        try:
            # 使用原生API检测按键
            alt_pressed = ctypes.windll.user32.GetAsyncKeyState(VK_ALT) & 0x8000 != 0
            esc_pressed = ctypes.windll.user32.GetAsyncKeyState(VK_ESC) & 0x8000 != 0
            
            if alt_pressed and esc_pressed:
                print("检测到Alt+Esc，终止所有进程")
                PROTECTION_ACTIVE = False
                
                # 终止所有相关进程
                exe_path = os.path.abspath(sys.executable if hasattr(sys, 'frozen') else sys.argv[0])
                current_pid = os.getpid()
                
                for proc in psutil.process_iter():
                    try:
                        cmdline = " ".join(proc.cmdline()).lower()
                        if ("calculator" in cmdline or 
                            os.path.basename(exe_path).lower() in cmdline or
                            (hasattr(proc, 'name') and proc.name() in ["pythonw.exe", "python.exe", os.path.basename(exe_path)])):
                            if proc.pid != current_pid:
                                print(f"终止进程: {proc.pid}")
                                proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                # 终止自身进程
                os._exit(0)
        
        except Exception as e:
            print(f"热键监听错误: {str(e)}")
        
        time.sleep(0.1)

# ====== 计算器功能代码 ======
def create_calculator_gui(root):
    """创建计算器界面 - 兼容exe打包"""
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
    btn_commands = {
        '=': calculate,
        'C': clear_expression,
        'DEL': delete_last_char
    }
    
    # 创建按钮
    row, col = 1, 0
    for button in buttons:
        if button in btn_commands:
            cmd = btn_commands[button]
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

    # 括号区域
    bracket_frame = tk.Frame(calc_frame)
    bracket_frame.grid(row=5, column=0, columnspan=4, sticky='nsew')
    tk.Button(bracket_frame, text='(', font=('Arial', 14),
             command=lambda: add_to_expression('(')).grid(row=0, column=0, sticky='nsew')
    tk.Button(bracket_frame, text=')', font=('Arial', 14),
             command=lambda: add_to_expression(')')).grid(row=0, column=1, sticky='nsew')
    tk.Button(bracket_frame, text='C', font=('Arial', 14), bg='#ffcccc',
             command=clear_expression).grid(row=0, column=2, sticky='nsew')
    tk.Button(bracket_frame, text='DEL', font=('Arial', 14), bg='#ffcc99',
             command=delete_last_char).grid(row=0, column=3, sticky='nsew')

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

# ====== 主要程序入口 ======
def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--foreground':
        # 前台计算器模式
        root = tk.Tk()
        root.title("高级计算器")
        root.geometry("600x400")
        
        # 设置窗口置顶
        root.attributes('-topmost', True)
        
        # 创建计算器界面
        create_calculator_gui(root)
        
        # 确保窗口创建后处理关闭按钮
        def init_window():
            try:
                # 获取窗口句柄
                hwnd = int(root.wm_frame(), 16)  # 更可靠的方式获取句柄
                if hwnd:
                    disable_success = disable_close_button(hwnd)
                    print(f"禁用关闭按钮: {'成功' if disable_success else '失败'}")
            except Exception as e:
                print(f"窗口初始化错误: {str(e)}")
                
            # 重写关闭行为
            def on_close():
                root.withdraw()
                root.after(1000, root.deiconify)
                
            root.protocol("WM_DELETE_WINDOW", on_close)
            
            # 显示调试信息（打包后可删除）
            print("计算器窗口已显示")
        
        root.after(300, init_window)  # 延迟初始化确保窗口创建完成
        
        # 运行主循环
        root.mainloop()
        
    else:
        # 后台保护模式
        print("后台保护进程启动")
        
        # 打包后隐藏控制台窗口
        if getattr(sys, 'frozen', False):
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        # 启动前台计算器
        exe_path = os.path.abspath(sys.executable if hasattr(sys, 'frozen') else sys.argv[0])
        try:
            # 使用正确的启动方式
            if getattr(sys, 'frozen', False):
                # 对于exe文件
                subprocess.Popen([exe_path, "--foreground"], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # 对于脚本
                subprocess.Popen([exe_path, "--foreground"])
        except Exception as e:
            print(f"启动前台进程失败: {str(e)}")
        
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
        finally:
            print("后台进程退出")

# 安全导入psutil
try:
    import psutil
except ImportError:
    # 提供psutil的功能替代
    print("警告: psutil未安装，某些功能可能受限")
    import ctypes.wintypes as wintypes
    
    # 简化的进程处理逻辑...

# 启动程序
if __name__ == "__main__":
    main()
