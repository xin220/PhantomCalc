import tkinter as tk
from tkinter import messagebox

def calculate():
    """执行计算并显示结果"""
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

# 创建主窗口
root = tk.Tk()
root.title("一个普通的计算器")
root.geometry("300x400")  # 设置窗口大小

# 设置字体
button_font = ('Arial', 14)
display_font = ('Arial', 18)

# 创建输入框
entry = tk.Entry(root, font=display_font, justify='right', bd=5)
entry.grid(row=0, column=0, columnspan=4, sticky='ew', padx=10, pady=10)

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
        btn = tk.Button(root, text=button, font=button_font, 
                        command=cmd, bg='#e0e0e0')
    else:
        btn = tk.Button(root, text=button, font=button_font,
                        command=lambda char=button: add_to_expression(char))
    
    btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
    col += 1
    if col > 3:
        col = 0
        row += 1

# 添加清除按钮
clear_btn = tk.Button(root, text='C', font=button_font, 
                      command=clear_expression, bg='#ffcccc')
clear_btn.grid(row=5, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

# 添加括号按钮
parentheses = tk.Frame(root)
parentheses.grid(row=5, column=2, columnspan=2, sticky='nsew')
tk.Button(parentheses, text='(', font=button_font, 
          command=lambda: add_to_expression('(')).grid(row=0, column=0, sticky='nsew', padx=5)
tk.Button(parentheses, text=')', font=button_font, 
          command=lambda: add_to_expression(')')).grid(row=0, column=1, sticky='nsew', padx=5)

# 设置网格行列权重
for i in range(7):
    root.grid_rowconfigure(i, weight=1)
for j in range(4):
    root.grid_columnconfigure(j, weight=1)

# 运行主循环
# 在计算器底部添加署名
signature = tk.Label(
    root, 
    text="by [星语心愿]",  
    font=('Arial', 8),
    fg='gray'
)
signature.grid(row=7, column=0, columnspan=4, sticky='se', padx=10, pady=5)
root.mainloop()
