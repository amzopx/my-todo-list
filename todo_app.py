# todo_app.py
# Author: amzopx
# Version: 0.7 - Implemented task editing functionality
# Recommended to run within a Python virtual environment.

import json
from colorama import Fore, init as colorama_init
import datetime # 导入 datetime 模块

# --- 初始化 Colorama ---
colorama_init(autoreset=True)

DATA_FILE = "tasks.json"
VALID_PRIORITIES = ["high", "medium", "low", ""] # 允许的优先级输入 (空字符串表示无优先级)

# --- 输入获取与验证辅助函数 ---
def get_validated_description_input(current_description=None):
    """获取并验证任务描述。允许在编辑时显示当前描述并保留。"""
    prompt = "请输入任务描述"
    if current_description is not None:
        prompt += f" (当前: '{current_description}', 直接回车保留): "
    else:
        prompt += ": "
    
    while True:
        description = input(prompt).strip()
        if current_description is not None and not description: # 用户在编辑时直接回车
            return current_description # 保留当前值
        if description: # 新增或编辑时输入了内容
            return description
        # 如果是新增模式 (current_description is None) 且没输入内容
        if current_description is None and not description: # 仅在新增时，描述才不能为空
            print(Fore.RED + "错误：任务描述不能为空！")
        # 注意：如果编辑时输入空字符串，会通过上面的逻辑保留原值，这里不需要额外处理

def get_validated_due_date_input(current_due_date=None):
    """获取并验证截止日期 (YYYY-MM-DD)。允许在编辑时显示当前日期并保留。"""
    prompt = "请输入截止日期 (YYYY-MM-DD，可留空"
    current_display_val = "无"
    if current_due_date: # current_due_date 可能是 None 或日期字符串
        current_display_val = current_due_date
    
    if current_due_date is not None: # 仅在编辑模式下（即 current_due_date 被传入时）显示当前值
        prompt += f", 当前: {current_display_val}, 直接回车保留): "
    else:
        prompt += "): "

    while True:
        due_date_str = input(prompt).strip()
        if current_due_date is not None and not due_date_str: # 用户在编辑时直接回车
            return current_due_date # 返回原始值，可能是 None 或日期字符串
        
        if not due_date_str: # 用户明确输入空（或在新增时留空）
            return None

        if is_valid_date_format(due_date_str):
            return due_date_str
        else:
            print(Fore.RED + "错误：日期格式无效，请输入 YYYY-MM-DD 格式或留空。")

def get_validated_priority_input(current_priority=None):
    """获取并验证优先级。允许在编辑时显示当前优先级并保留。"""
    priority_options_display = '/'.join(p for p in VALID_PRIORITIES if p) # "high/medium/low"
    prompt = f"请输入优先级 ({priority_options_display}，可留空"
    current_display_val = "无"
    if current_priority: # current_priority 可能是 None 或优先级字符串
        current_display_val = current_priority.capitalize()

    if current_priority is not None: # 仅在编辑模式下显示当前值
        prompt += f", 当前: {current_display_val}, 直接回车保留): "
    else:
        prompt += "): "

    while True:
        priority_input = input(prompt).strip().lower()
        if current_priority is not None and not priority_input: # 用户在编辑时直接回车
            return current_priority # 返回原始值，可能是 None 或优先级字符串

        if priority_input in VALID_PRIORITIES:
            return priority_input if priority_input else None # 如果输入是有效空字符串，则存 None
        else:
            valid_options_text = ', '.join(p for p in VALID_PRIORITIES if p)
            print(Fore.RED + f"错误：无效的优先级。请输入 {valid_options_text} 或留空。")

# --- 日期和优先级格式化显示函数 (来自 V0.6) ---
def is_valid_date_format(date_string):
    """检查日期字符串是否符合YYYY-MM-DD 格式，并且是有效日期。"""
    if not date_string: # 允许截止日期为空
        return True
    try:
        # 尝试解析日期，如果成功则格式和日期本身都有效
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
            # 确保存储的日期是有效的，然后再显示
            datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return date_str # 目前保持YYYY-MM-DD
        except ValueError:
            return Fore.RED + "日期损坏" # 如果存储的日期格式损坏
    return "N/A" # 如果没有截止日期

# --- 文件操作函数 (与 V0.6 相同) ---
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
                        task = {
                            'description': item['description'],
                            'completed': item['completed'],
                            'due_date': item.get('due_date', None),
                            'priority': item.get('priority', None)
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
    向任务列表中添加一个新任务，使用辅助函数获取输入。
    """
    print(Fore.CYAN + "\n--- 添加新任务 ---")
    description = get_validated_description_input() # 新增时 current_description 为 None
    if not description: # 如果描述在辅助函数中因某些原因未能获取（理论上已处理）
        return

    due_date = get_validated_due_date_input() # 新增时 current_due_date 为 None
    priority = get_validated_priority_input() # 新增时 current_priority 为 None
    
    new_task = {
        'description': description,
        'completed': False,
        'due_date': due_date,
        'priority': priority
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
    header = f"{'序号':<5} | {'状态':<7} | {'任务描述':<40} | {'截止日期':<12} | {'优先级':<8}"
    print(header)
    print("-" * len(header)) # 分隔线长度根据表头动态调整

    for index, task in enumerate(tasks):
        status_char = "[x]" if task['completed'] else "[ ]"
        status_color = Fore.GREEN if task['completed'] else Fore.YELLOW
        status_marker = status_color + status_char
        
        desc_color = Fore.GREEN if task['completed'] else Fore.WHITE 
        
        due_date_display = format_date_display(task.get('due_date'))
        priority_display = format_priority_display(task.get('priority'))

        # 任务描述截断逻辑
        description_str = task['description']
        # Max width for description in print, accounting for other columns and ANSI codes.
        # This is still an approximation. A truly robust solution is complex.
        # Let's target around 40 visible characters for description.
        max_desc_len = 38 
        description_display = description_str[:max_desc_len] + ".." if len(description_str) > max_desc_len else description_str
        
        # For alignment with color codes, it's tricky.
        # A simpler approach for now is to accept slight misalignments or ensure fixed-width for colored parts.
        # Example: status_marker fixed to 13 characters (ANSI codes make it longer)
        print(f"{index + 1:<5} | {status_marker:<13} | {desc_color + description_display:<40} | {due_date_display:<12} | {priority_display:<8}")
    
    print(Fore.CYAN + "-" * len(header))


def edit_task(tasks):
    """
    编辑现有任务的描述、截止日期或优先级。
    """
    view_tasks(tasks)
    if not tasks:
        return

    try:
        task_num_str = input("请输入要编辑的任务序号: ")
        task_index = int(task_num_str) - 1

        if 0 <= task_index < len(tasks):
            task_to_edit = tasks[task_index]
            print(Fore.CYAN + f"\n--- 正在编辑任务: '{task_to_edit['description']}' ---")

            # 编辑描述
            new_description = get_validated_description_input(current_description=task_to_edit['description'])
            task_to_edit['description'] = new_description
            
            # 编辑截止日期
            new_due_date = get_validated_due_date_input(current_due_date=task_to_edit.get('due_date'))
            task_to_edit['due_date'] = new_due_date

            # 编辑优先级
            new_priority = get_validated_priority_input(current_priority=task_to_edit.get('priority'))
            task_to_edit['priority'] = new_priority

            print(Fore.GREEN + f"任务 '{task_to_edit['description']}' 已成功更新。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")
    except Exception as e:
        print(Fore.RED + f"编辑任务时发生错误: {e}")


def mark_task_completed(tasks, task_index_str):
    """
    将指定索引的任务标记为已完成。 (与 V0.6 相同)
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
    删除指定索引的任务。 (与 V0.6 相同)
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
        print("3. 编辑任务")      # 新增选项
        print("4. 标记任务为已完成")
        print("5. 删除任务")
        print("6. 退出")        # 退出选项序号顺延

        choice = input(f"请输入你的选择 (1-{6}): ") # 更新选项范围

        if choice == '1':
            add_task(tasks)
            save_tasks(tasks)
        elif choice == '2':
            view_tasks(tasks)
        elif choice == '3': # 新增：编辑任务
            edit_task(tasks)
            save_tasks(tasks) # 编辑后保存
        elif choice == '4':
            view_tasks(tasks)
            if tasks:
                task_num_str = input("请输入要标记为完成的任务序号: ")
                mark_task_completed(tasks, task_num_str)
                save_tasks(tasks)
        elif choice == '5':
            view_tasks(tasks)
            if tasks:
                task_num_str = input("请输入要删除的任务序号: ")
                delete_task(tasks, task_num_str)
                save_tasks(tasks)
        elif choice == '6': # 更新：退出程序
            print(Fore.GREEN + "感谢使用，任务已保存。再见！")
            break
        else:
            print(Fore.RED + f"无效的选择，请输入1到{6}之间的数字。") # 更新选项范围

if __name__ == "__main__":
    main()