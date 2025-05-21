# todo_app_cli.py
# Command-Line Interface for the To-Do application.
# Uses core_logic.py for data management.

import json # Though json direct use might be minimal now
from colorama import Fore, init as colorama_init
import datetime
import core_logic # Import the refactored core logic

# --- 初始化 Colorama ---
colorama_init(autoreset=True)

# CLI specific constants for user choices (derived from core_logic)
CLI_VALID_PRIORITY_CHOICES = [p for p in core_logic.VALID_PRIORITIES_CORE if p is not None] # "high", "medium", "low"
CLI_PRIORITY_DISPLAY_OPTIONS = '/'.join(CLI_VALID_PRIORITY_CHOICES)


# --- CLI: 输入获取与验证辅助函数 ---
def get_validated_description_input_cli(current_description=None):
    prompt = "请输入任务描述"
    if current_description is not None:
        prompt += f" (当前: '{current_description}', 直接回车保留): "
    else:
        prompt += ": "
    while True:
        description = input(prompt).strip()
        if current_description is not None and not description: # Edit mode, user pressed Enter
            return current_description
        if description: # Add mode, or Edit mode with new value
            return description
        if current_description is None and not description: # Add mode, description is mandatory
            print(Fore.RED + "错误：任务描述不能为空！")
        # If in edit mode and user enters empty string (and current_description was not None),
        # the first 'if' handles it by returning current_description.

def get_validated_due_date_input_cli(current_due_date=None):
    prompt = "请输入截止日期 (YYYY-MM-DD，可留空"
    current_display_val = "无"
    if current_due_date:
        current_display_val = current_due_date
    
    if current_due_date is not None: # Only show current value in edit mode
        prompt += f", 当前: {current_display_val}, 直接回车保留): "
    else:
        prompt += "): "

    while True:
        due_date_str = input(prompt).strip()
        if current_due_date is not None and not due_date_str: # Edit mode, user pressed Enter
            return current_due_date # Return original value (could be None or date string)
        
        if not due_date_str: # User explicitly wants no date (add mode or clearing in edit mode)
            return None

        if core_logic.is_valid_date_format_core(due_date_str): # Use validation from core_logic
            return due_date_str
        else:
            print(Fore.RED + "错误：日期格式无效，请输入YYYY-MM-DD 格式或留空。")

def get_validated_priority_input_cli(current_priority=None):
    prompt = f"请输入优先级 ({CLI_PRIORITY_DISPLAY_OPTIONS}，可留空"
    current_display_val = "无"
    if current_priority:
        current_display_val = current_priority.capitalize()

    if current_priority is not None: # Only show current value in edit mode
        prompt += f", 当前: {current_display_val}, 直接回车保留): "
    else:
        prompt += "): "
    
    while True:
        priority_input = input(prompt).strip().lower()
        if current_priority is not None and not priority_input: # Edit mode, user pressed Enter
            return current_priority # Return original value (could be None or priority string)

        if not priority_input: # User explicitly wants no priority
            return None
        
        if priority_input in CLI_VALID_PRIORITY_CHOICES: # "high", "medium", "low"
            return priority_input
        else:
            print(Fore.RED + f"错误：无效的优先级。请输入 {', '.join(CLI_VALID_PRIORITY_CHOICES)} 或留空。")

# --- CLI: 日期和优先级格式化显示函数 ---
def format_priority_display_cli(priority_str):
    if priority_str:
        return priority_str.capitalize()
    return "N/A"

def format_date_display_cli(date_str):
    if date_str:
        # We trust core_logic.is_valid_date_format_core was used for input.
        # A quick check here before display is also fine.
        if core_logic.is_valid_date_format_core(date_str):
            return date_str
        else:
            return Fore.RED + "日期损坏" # Should not happen if data integrity is maintained
    return "N/A"

# --- CLI: 文件操作包装器 (调用 core_logic) ---
def load_tasks_cli():
    # print(Fore.BLUE + "正在加载任务...") # Optional CLI feedback
    tasks = core_logic.load_tasks_data()
    # load_tasks_data now always returns a list, even if empty or error
    return tasks

def save_tasks_cli(tasks):
    if not core_logic.save_tasks_data(tasks):
        print(Fore.RED + "错误：保存任务失败！")
    # else: print(Fore.GREEN + "任务已保存。") # Usually too verbose for CLI

# --- CLI: 任务管理核心函数 ---
def add_task_cli(tasks_list):
    print(Fore.CYAN + "\n--- 添加新任务 (CLI) ---")
    description = get_validated_description_input_cli()
    # description is already validated to be non-empty here by the helper
    
    due_date = get_validated_due_date_input_cli() # Can return None
    priority = get_validated_priority_input_cli() # Can return None
    
    new_task = core_logic.add_task_data(tasks_list, description, due_date, priority)
    if new_task:
        print(Fore.GREEN + f"任务 '{new_task['description']}' 已添加。")
    else:
        # This case should ideally not be reached if description is mandatory and validated by get_validated_description_input_cli
        print(Fore.RED + "添加任务失败。请确保描述不为空。")

def view_tasks_cli(tasks_to_display, title="--- 你的任务清单 ---"):
    if not tasks_to_display:
        print(Fore.YELLOW + "当前没有符合条件的任务，或列表为空。")
        return

    print(Fore.CYAN + f"\n{title}")
    header = f"{'序号':<5} | {'状态':<7} | {'任务描述':<40} | {'截止日期':<12} | {'优先级':<8}"
    print(header)
    print("-" * len(header))

    for index, task in enumerate(tasks_to_display):
        status_char = "[x]" if task.get('completed') else "[ ]" # Use .get for safety
        status_color = Fore.GREEN if task.get('completed') else Fore.YELLOW
        status_marker = status_color + status_char
        
        desc_color = Fore.GREEN if task.get('completed') else Fore.WHITE 
        
        due_date_display = format_date_display_cli(task.get('due_date'))
        priority_display = format_priority_display_cli(task.get('priority'))
        
        description_str = task.get('description', '') # Use .get for safety
        max_desc_len = 38 
        description_display = description_str[:max_desc_len] + ".." if len(description_str) > max_desc_len else description_str
        
        print(f"{index + 1:<5} | {status_marker:<13} | {desc_color + description_display:<40} | {due_date_display:<12} | {priority_display:<8}")
    
    print(Fore.CYAN + "-" * len(header))

def edit_task_cli(tasks_list):
    print(Fore.MAGENTA +"\n请参考以下原始任务列表选择要编辑的序号：")
    view_tasks_cli(tasks_list, title="--- 原始任务列表 (供编辑选择) ---")
    if not tasks_list:
        return

    try:
        task_num_str = input("请输入要编辑的任务序号 (基于上方原始列表): ")
        task_index = int(task_num_str) - 1
        
        task_to_edit = core_logic.get_task_by_original_index(tasks_list, task_index) # Get from original list
        
        if task_to_edit:
            print(Fore.CYAN + f"\n--- 正在编辑任务: '{task_to_edit['description']}' ---")
            
            new_description = get_validated_description_input_cli(current_description=task_to_edit['description'])
            new_due_date = get_validated_due_date_input_cli(current_due_date=task_to_edit.get('due_date'))
            new_priority = get_validated_priority_input_cli(current_priority=task_to_edit.get('priority'))

            if core_logic.update_task_data(task_to_edit, new_description, new_due_date, new_priority):
                print(Fore.GREEN + f"任务 '{task_to_edit['description']}' 已成功更新。")
            else:
                # This else might be hit if core_logic.update_task_data returns False (e.g., empty new_description)
                print(Fore.RED + "任务更新失败。描述不能为空。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")
    except Exception as e:
        print(Fore.RED + f"编辑任务时发生错误: {e}")

def mark_task_completed_cli(tasks_list):
    print(Fore.MAGENTA +"\n请参考以下原始任务列表选择要操作的序号：")
    view_tasks_cli(tasks_list, title="--- 原始任务列表 (供操作选择) ---")
    if not tasks_list: return

    try:
        task_num_str = input("请输入要标记为完成的任务序号: ")
        task_index = int(task_num_str) - 1
        
        task_to_mark = core_logic.get_task_by_original_index(tasks_list, task_index)
        if task_to_mark:
            if task_to_mark.get('completed'):
                print(Fore.YELLOW + f"任务 '{task_to_mark['description']}' 已经是完成状态。")
            else:
                if core_logic.toggle_task_completion_data(task_to_mark): # Core logic handles the toggle
                    print(Fore.GREEN + f"任务 '{task_to_mark['description']}' 已标记为完成。")
                else: # Should not happen if task_to_mark is valid
                    print(Fore.RED + "标记任务完成失败。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")

def delete_task_cli(tasks_list):
    print(Fore.MAGENTA +"\n请参考以下原始任务列表选择要操作的序号：")
    view_tasks_cli(tasks_list, title="--- 原始任务列表 (供操作选择) ---")
    if not tasks_list: return

    try:
        task_num_str = input("请输入要删除的任务序号: ")
        task_index = int(task_num_str) - 1
        
        # We need the description before deleting for the message
        task_to_delete = core_logic.get_task_by_original_index(tasks_list, task_index)
        
        if task_to_delete:
            description_of_deleted_task = task_to_delete['description']
            if core_logic.delete_task_data(tasks_list, task_index): # Core logic handles deletion
                print(Fore.GREEN + f"任务 '{description_of_deleted_task}' 已删除。")
            else: # Should not happen if index is valid before call
                print(Fore.RED + "删除任务失败。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")

# --- CLI: 排序与过滤功能 ---
def sort_tasks_cli(tasks_list_original, sort_key, reverse_order=False):
    """Sorts a copy of the task list for CLI display."""
    if not tasks_list_original: return []
    
    # Work on a copy
    tasks_to_sort = list(tasks_list_original) 

    if sort_key == "description":
        return sorted(tasks_to_sort, key=lambda task: task.get('description', '').lower(), reverse=reverse_order)
    elif sort_key == "due_date":
        return sorted(tasks_to_sort, key=lambda task: (
            task.get('due_date') is None, # Sorts None (True) after non-None (False)
            task.get('due_date') if task.get('due_date') else "9999-99-99" # Actual date or late placeholder
        ), reverse=reverse_order)
    elif sort_key == "priority":
        # Use the map from core_logic for consistent sorting
        return sorted(tasks_to_sort, key=lambda task: core_logic.PRIORITY_ORDER_MAP_CORE.get(task.get('priority'), 99), reverse=reverse_order)
    else:
        # print(Fore.RED + "错误：无效的排序键。") # Feedback handled by caller
        return tasks_to_sort

def filter_tasks_cli(tasks_list_original, filter_type, filter_value=None):
    """Filters a copy of the task list for CLI display."""
    if not tasks_list_original: return []

    tasks_to_filter = list(tasks_list_original)

    if filter_type == "status":
        return [task for task in tasks_to_filter if task.get('completed') == filter_value]
    elif filter_type == "priority":
        return [task for task in tasks_to_filter if task.get('priority') == filter_value]
    else:
        # print(Fore.RED + "错误：无效的过滤类型。") # Feedback handled by caller
        return tasks_to_filter

def handle_advanced_view_options_cli(current_tasks):
    if not current_tasks:
        print(Fore.YELLOW + "当前没有任务可供排序或过滤。")
        return

    while True:
        print(Fore.CYAN + "\n--- 高级查看选项 (CLI) ---")
        print("1. 按描述排序")
        print("2. 按截止日期排序")
        print("3. 按优先级排序")
        print("4. 过滤已完成任务")
        print("5. 过滤未完成任务")
        print("6. 按优先级过滤")
        print("0. 返回主菜单")
        
        sub_choice = input("请选择操作 (0-6): ")
        
        processed_list = None # To store the result of sort/filter

        if sub_choice == '1':
            rev = input("升序 (a) 还是降序 (d)? [a]: ").lower() == 'd'
            processed_list = sort_tasks_cli(current_tasks, "description", reverse_order=rev)
            view_tasks_cli(processed_list, title="--- 按描述排序后 ---")
        elif sub_choice == '2':
            rev = input("升序 (旧->新 a) 还是降序 (新->旧 d)? [a]: ").lower() == 'd'
            processed_list = sort_tasks_cli(current_tasks, "due_date", reverse_order=rev)
            view_tasks_cli(processed_list, title="--- 按截止日期排序后 ---")
        elif sub_choice == '3':
            rev_display = input("升序 (高->低 a) 还是降序 (低->高 d)? [a]: ").lower()
            # PRIORITY_ORDER_MAP_CORE: High=0, Medium=1, Low=2, None=3
            # User wants High->Low (ascending by map value) means reverse_order=False
            # User wants Low->High (descending by map value) means reverse_order=True
            actual_reverse_for_sort = (rev_display == 'd')
            processed_list = sort_tasks_cli(current_tasks, "priority", reverse_order=actual_reverse_for_sort)
            view_tasks_cli(processed_list, title="--- 按优先级排序后 ---")
        elif sub_choice == '4':
            processed_list = filter_tasks_cli(current_tasks, "status", filter_value=True)
            view_tasks_cli(processed_list, title="--- 已完成的任务 ---")
        elif sub_choice == '5':
            processed_list = filter_tasks_cli(current_tasks, "status", filter_value=False)
            view_tasks_cli(processed_list, title="--- 未完成的任务 ---")
        elif sub_choice == '6':
            priority_to_filter_input = input(f"请输入要查看的优先级 ({CLI_PRIORITY_DISPLAY_OPTIONS}, 或留空代表'无优先级'): ").strip().lower()
            if priority_to_filter_input == "" or priority_to_filter_input in CLI_VALID_PRIORITY_CHOICES:
                actual_filter_value_core = priority_to_filter_input if priority_to_filter_input else None
                processed_list = filter_tasks_cli(current_tasks, "priority", filter_value=actual_filter_value_core)
                display_prio = format_priority_display_cli(actual_filter_value_core)
                view_tasks_cli(processed_list, title=f"--- 优先级为 '{display_prio}' 的任务 ---")
            else:
                print(Fore.RED + "无效的优先级输入。")
        elif sub_choice == '0':
            break
        else:
            print(Fore.RED + "无效的选择，请输入0到6之间的数字。")

# --- CLI: 主程序逻辑 ---
def main_cli():
    tasks = load_tasks_cli() # Uses core_logic

    while True:
        print(Fore.BLUE + "\n请选择操作 (CLI)：")
        print("1. 添加任务")
        print("2. 查看所有任务 (原始顺序)")
        print("3. 编辑任务")
        print("4. 标记任务为已完成")
        print("5. 删除任务")
        print("6. 高级查看 (排序/过滤)")
        print("7. 退出")
        
        choice = input(f"请输入你的选择 (1-7): ")

        if choice == '1':
            add_task_cli(tasks)
            save_tasks_cli(tasks)
        elif choice == '2':
            view_tasks_cli(tasks, title="--- 所有任务 (原始顺序) ---")
        elif choice == '3':
            edit_task_cli(tasks)
            save_tasks_cli(tasks)
        elif choice == '4':
            mark_task_completed_cli(tasks)
            save_tasks_cli(tasks)
        elif choice == '5':
            delete_task_cli(tasks)
            save_tasks_cli(tasks)
        elif choice == '6':
            handle_advanced_view_options_cli(tasks)
        elif choice == '7':
            print(Fore.GREEN + "感谢使用CLI版本。任务数据已自动保存（如适用）。再见！")
            break
        else:
            print(Fore.RED + f"无效的选择，请输入1到7之间的数字。")

if __name__ == "__main__":
    main_cli()