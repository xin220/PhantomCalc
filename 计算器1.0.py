# 简易命令行计算器
while True:
    print("\n--- Python简易计算器 by 星语心愿 ---")
    print("可用操作: +, -, *, /")
    print("输入 'exit' 退出程序")
    
    # 获取用户输入
    user_input = input("请输入表达式 (例如: 5 + 3): ")
    
    # 退出检查
    if user_input.lower() == 'exit':
        print("感谢使用计算器，再见！")
        break
    
    try:
        # 分割输入的表达式
        parts = user_input.split()
        
        # 确保输入有三个部分（数字 运算符 数字）
        if len(parts) != 3:
            print("错误：请输入有效的表达式（如：5 + 3）")
            continue
            
        num1 = float(parts[0])
        operator = parts[1]
        num2 = float(parts[2])
        
        # 执行计算
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            # 处理除以零的情况
            if num2 == 0:
                print("错误：除数不能为零！")
                continue
            result = num1 / num2
        else:
            print(f"错误：不支持的运算符 '{operator}'")
            continue
            
        # 显示结果
        print(f"结果: {user_input} = {result}")
        
    except ValueError:
        print("错误：请确保输入有效的数字")
    except Exception as e:
        print(f"发生错误: {str(e)}")
