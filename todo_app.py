# todo_app.py
# Author: amzopx
# Version: 0.6 - Added due dates and priorities to tasks
# Recommended to run within a Python virtual environment.

import json
from colorama import Fore, init as colorama_init
import datetime # 导入 datetime 模块

# --- 初始化 Colorama ---
colorama_init(autoreset=True)

DATA_FILE = "tasks.json"
VALID_PRIORITIES = ["high", "medium", "low", ""] # 允许的优先级输入 (空字符串表示无优先级)

# --- 日期和优先级辅助函数 ---
def is_valid_date_format(date_string):
    """检查日期字符串是否符合 YYYY-MM-DD 格式，并且是有效日期。"""
    if not date_string: # 允许截止日期为空
        return True
    try:
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_priority_display(priority_str):
    """格式化优先级的显示，首字母大写。"""
    if priority_str:
        return priority_str.capitalize()
    return "N/A" # 如果没有优先级

def format_date_display(date_str):
    """格式化日期的显示。"""
    if date_str:
        try:
            # 尝试将存储的日期字符串解析为日期对象，再格式化，以确保其有效性
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            # 你可以在这里添加更友好的日期显示，比如 "May 21, 2025"
            # return date_obj.strftime("%b %d, %Y")
            return date_str # 目前保持 YYYY-MM-DD
        except ValueError:
            return "Invalid Date" # 如果存储的日期格式损坏
    return "N/A" # 如果没有截止日期

# --- 文件操作函数 ---
def load_tasks():
    """
    从 JSON 文件中加载任务。
    会兼容旧格式的任务（没有 due_date 和 priority）。
    """
    tasks = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            if isinstance(tasks_data, list):
                for item in tasks_data:
                    if isinstance(item, dict) and 'description' in item and 'completed' in item:
                        # 为旧任务提供默认的 due_date 和 priority
                        task = {
                            'description': item['description'],
                            'completed': item['completed'],
                            'due_date': item.get('due_date', None), # 使用 .get() 获取，若不存在则为 None
                            'priority': item.get('priority', None)  # 使用 .get() 获取，若不存在则为 None
                        }
                        tasks.append(task)
                    else:
                        print(Fore.YELLOW + "警告：任务文件中的某个条目格式不正确，已忽略。")
                if not tasks and tasks_data:
                     print(Fore.YELLOW + "警告：所有任务条目格式均不正确，将使用空任务列表。")
            else:
                print(Fore.YELLOW + "警告：任务文件顶层结构不是列表，将使用空任务列表。")
                return []
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print(Fore.YELLOW + f"警告：'{DATA_FILE}' 内容不是有效的JSON格式或为空。将使用空任务列表。")
        return []
    except Exception as e:
        print(Fore.RED + f"加载任务时发生未知错误: {e}")
    return tasks

def save_tasks(tasks):
    """
    将任务列表以 JSON 格式保存到文件。
    """
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(Fore.RED + f"保存任务时发生错误: {e}")

# --- 任务管理核心函数 ---
def add_task(tasks):
    """
    向任务列表中添加一个新任务，包含截止日期和优先级。
    """
    description = input("请输入任务描述: ").strip()
    if not description:
        print(Fore.RED + "错误：任务描述不能为空！")
        return

    # 获取并验证截止日期
    while True:
        due_date_str = input("请输入截止日期 (YYYY-MM-DD，可留空): ").strip()
        if is_valid_date_format(due_date_str):
            # 如果用户留空，due_date_str 就是空字符串，我们将存储 None
            due_date_to_store = due_date_str if due_date_str else None
            break
        else:
            print(Fore.RED + "错误：日期格式无效，请输入 YYYY-MM-DD 格式或留空。")

    # 获取并验证优先级
    while True:
        priority_input = input(f"请输入优先级 ({'/'.join(p for p in VALID_PRIORITIES if p)}, 可留空): ").strip().lower()
        if priority_input in VALID_PRIORITIES:
            priority_to_store = priority_input if priority_input else None
            break
        else:
            valid_options = [p for p in VALID_PRIORITIES if p] # 获取非空选项
            print(Fore.RED + f"错误：无效的优先级。请输入 {', '.join(valid_options)} 或留空。")
    
    new_task = {
        'description': description,
        'completed': False,
        'due_date': due_date_to_store,
        'priority': priority_to_store
    }
    tasks.append(new_task)
    print(Fore.GREEN + f"任务 '{description}' 已添加。")

def view_tasks(tasks):
    """
    显示所有任务及其状态、截止日期和优先级。
    """
    if not tasks:
        print(Fore.YELLOW + "当前没有任务。")
        return

    print(Fore.CYAN + "\n--- 你的任务清单 ---")
    # 打印表头
    print(f"{'序号':<5} | {'状态':<7} | {'任务描述':<40} | {'截止日期':<12} | {'优先级':<8}")
    print("-" * 80) # 分隔线

    for index, task in enumerate(tasks):
        status_marker = Fore.GREEN + "[x]" if task['completed'] else Fore.YELLOW + "[ ]"
        
        # 根据完成状态决定任务描述的颜色
        task_desc_color = Fore.GREEN if task['completed'] else Fore.WHITE # 未完成用默认白色或黄色
        
        # 截止日期和优先级的显示处理
        due_date_display = format_date_display(task.get('due_date'))
        priority_display = format_priority_display(task.get('priority'))

        # 考虑任务描述长度，进行截断或换行（此处简单截断）
        description_display = task['description'][:38] + ".." if len(task['description']) > 40 else task['description']
        
        # 打印格式化后的任务行
        # 使用 f-string 和对齐：< 左对齐, > 右对齐, ^ 居中, 后跟数字表示宽度
        print(f"{index + 1:<5} | {status_marker:<13} | {task_desc_color + description_display:<40} | {due_date_display:<12} | {priority_display:<8}")
        # Fore.RESET or Style.RESET_ALL is handled by colorama_init(autoreset=True)
        # The color escape codes count towards string length for alignment, so Fore.GREEN + "[x]" is longer than "[x]"
        # A more robust alignment would calculate actual visible length. For now, this is an approximation.
        # To fix the above alignment issue with color codes, we can print parts separately or strip ansi codes for length calculation.
        # For simplicity here, the alignment might be slightly off due to color codes.
        # A more precise way for status_marker:
        # status_str = "[x]" if task['completed'] else "[ ]"
        # colored_status_marker = (Fore.GREEN if task['completed'] else Fore.YELLOW) + status_str
        # print(f"{index + 1:<5} | {colored_status_marker} {Style.RESET_ALL} | ...")
        # But with autoreset=True, we only need to add color before the string.
        # The main issue is that f-string alignment sees e.g. `\x1b[32m[x]\x1b[0m` as much longer than `[x]`

    print(Fore.CYAN + "--------------------------------------------------------------------------------")

def mark_task_completed(tasks, task_index_str):
    """
    将指定索引的任务标记为已完成。
    """
    try:
        actual_index = int(task_index_str) - 1
        if 0 <= actual_index < len(tasks):
            if tasks[actual_index]['completed']:
                print(Fore.YELLOW + f"任务 '{tasks[actual_index]['description']}' 已经是完成状态。")
            else:
                tasks[actual_index]['completed'] = True
                print(Fore.GREEN + f"任务 '{tasks[actual_index]['description']}' 已标记为完成。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")

def delete_task(tasks, task_index_str):
    """
    删除指定索引的任务。
    """
    try:
        actual_index = int(task_index_str) - 1
        if 0 <= actual_index < len(tasks):
            removed_task = tasks.pop(actual_index)
            print(Fore.GREEN + f"任务 '{removed_task['description']}' 已删除。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")

# --- 主程序逻辑 ---
def main():
    """
    程序的主入口和用户交互循环。
    """
    tasks = load_tasks()

    while True:
        print(Fore.BLUE + "\n请选择操作：")
        print("1. 添加任务")
        print("2. 查看任务")
        print("3. 标记任务为已完成")
        print("4. 删除任务")
        print("5. 退出")

        choice = input("请输入你的选择 (1-5): ")

        if choice == '1':
            add_task(tasks) # add_task 现在不需要 description 参数，它会自己获取
            save_tasks(tasks)
        elif choice == '2':
            view_tasks(tasks)
        elif choice == '3':
            view_tasks(tasks)
            if tasks:
                task_num_str = input("请输入要标记为完成的任务序号: ")
                mark_task_completed(tasks, task_num_str)
                save_tasks(tasks)
        elif choice == '4':
            view_tasks(tasks)
            if tasks:
                task_num_str = input("请输入要删除的任务序号: ")
                delete_task(tasks, task_num_str)
                save_tasks(tasks)
        elif choice == '5':
            print(Fore.GREEN + "感谢使用，任务已保存。再见！")
            break
        else:
            print(Fore.RED + "无效的选择，请输入1到5之间的数字。")

if __name__ == "__main__":
    main()