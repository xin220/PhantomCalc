import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import os

# 添加全局变量存储历史记录
history = []

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

# 运行主循环
root.mainloop()
