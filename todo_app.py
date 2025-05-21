# todo_app.py
# Author: 你的名字
# Version: 0.8 - Implemented task sorting and filtering
# Recommended to run within a Python virtual environment.

import json
from colorama import Fore, init as colorama_init
import datetime

# --- 初始化 Colorama ---
colorama_init(autoreset=True)

DATA_FILE = "tasks.json"
VALID_PRIORITIES = ["high", "medium", "low", ""] # 允许的优先级输入 (空字符串表示无优先级)
# 定义优先级的排序顺序，值越小，优先级越高（用于排序）
PRIORITY_ORDER_MAP = {
    "high": 0,
    "medium": 1,
    "low": 2,
    None: 3 # None 或空字符串代表的无优先级排在最后
}

# --- 输入获取与验证辅助函数 (来自 V0.7，保持不变) ---
def get_validated_description_input(current_description=None):
    prompt = "请输入任务描述"
    if current_description is not None:
        prompt += f" (当前: '{current_description}', 直接回车保留): "
    else:
        prompt += ": "
    while True:
        description = input(prompt).strip()
        if current_description is not None and not description:
            return current_description
        if description:
            return description
        if current_description is None and not description:
            print(Fore.RED + "错误：任务描述不能为空！")

def get_validated_due_date_input(current_due_date=None):
    prompt = "请输入截止日期 (YYYY-MM-DD，可留空"
    current_display_val = "无"
    if current_due_date:
        current_display_val = current_due_date
    if current_due_date is not None:
        prompt += f", 当前: {current_display_val}, 直接回车保留): "
    else:
        prompt += "): "
    while True:
        due_date_str = input(prompt).strip()
        if current_due_date is not None and not due_date_str:
            return current_due_date
        if not due_date_str:
            return None
        if is_valid_date_format(due_date_str):
            return due_date_str
        else:
            print(Fore.RED + "错误：日期格式无效，请输入YYYY-MM-DD 格式或留空。")

def get_validated_priority_input(current_priority=None):
    priority_options_display = '/'.join(p for p in VALID_PRIORITIES if p)
    prompt = f"请输入优先级 ({priority_options_display}，可留空"
    current_display_val = "无"
    if current_priority:
        current_display_val = current_priority.capitalize()
    if current_priority is not None:
        prompt += f", 当前: {current_display_val}, 直接回车保留): "
    else:
        prompt += "): "
    while True:
        priority_input = input(prompt).strip().lower()
        if current_priority is not None and not priority_input:
            return current_priority
        if priority_input in VALID_PRIORITIES:
            return priority_input if priority_input else None
        else:
            valid_options_text = ', '.join(p for p in VALID_PRIORITIES if p)
            print(Fore.RED + f"错误：无效的优先级。请输入 {valid_options_text} 或留空。")

# --- 日期和优先级格式化/验证函数 (来自 V0.6/V0.7，保持不变) ---
def is_valid_date_format(date_string):
    if not date_string:
        return True
    try:
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_priority_display(priority_str):
    if priority_str:
        return priority_str.capitalize()
    return "N/A"

def format_date_display(date_str):
    if date_str:
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return date_str
        except ValueError:
            return Fore.RED + "日期损坏"
    return "N/A"

# --- 文件操作函数 (来自 V0.7，保持不变) ---
def load_tasks():
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
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(Fore.RED + f"保存任务时发生错误: {e}")

# --- 任务管理核心函数 (add, edit, mark_complete, delete 来自 V0.7，保持不变) ---
def add_task(tasks):
    print(Fore.CYAN + "\n--- 添加新任务 ---")
    description = get_validated_description_input()
    if not description:
        return
    due_date = get_validated_due_date_input()
    priority = get_validated_priority_input()
    new_task = {
        'description': description,
        'completed': False,
        'due_date': due_date,
        'priority': priority
    }
    tasks.append(new_task)
    print(Fore.GREEN + f"任务 '{description}' 已添加。")

def view_tasks(tasks_to_display, title="--- 你的任务清单 ---"): # 添加 title 参数
    """
    显示给定的任务列表。
    tasks_to_display: 要显示的任务列表 (可能是原始列表，也可能是排序/过滤后的副本)
    title: 显示列表时的标题
    """
    if not tasks_to_display:
        print(Fore.YELLOW + "当前没有符合条件的任务，或列表为空。")
        return

    print(Fore.CYAN + f"\n{title}")
    header = f"{'序号':<5} | {'状态':<7} | {'任务描述':<40} | {'截止日期':<12} | {'优先级':<8}"
    print(header)
    print("-" * len(header))

    for index, task in enumerate(tasks_to_display):
        status_char = "[x]" if task['completed'] else "[ ]"
        status_color = Fore.GREEN if task['completed'] else Fore.YELLOW
        status_marker = status_color + status_char
        
        desc_color = Fore.GREEN if task['completed'] else Fore.WHITE 
        
        due_date_display = format_date_display(task.get('due_date'))
        priority_display = format_priority_display(task.get('priority'))
        
        description_str = task['description']
        max_desc_len = 38 
        description_display = description_str[:max_desc_len] + ".." if len(description_str) > max_desc_len else description_str
        
        # 注意：这里显示的序号是基于 tasks_to_display 的，如果它是原列表的副本，
        # 这个序号不能直接用于原始 tasks 列表的编辑/删除等操作，除非有 ID 映射。
        # 在当前版本，我们只用这个 view_tasks 来显示，操作还是基于原始列表的 view。
        print(f"{index + 1:<5} | {status_marker:<13} | {desc_color + description_display:<40} | {due_date_display:<12} | {priority_display:<8}")
    
    print(Fore.CYAN + "-" * len(header))

def edit_task(tasks):
    # 先显示原始列表供用户选择序号
    print(Fore.MAGENTA +"请参考以下原始任务列表选择要编辑的序号：")
    view_tasks(tasks, title="--- 原始任务列表 (供编辑选择) ---") # 使用原始列表进行选择
    if not tasks:
        return

    try:
        task_num_str = input("请输入要编辑的任务序号 (基于上方原始列表): ")
        task_index = int(task_num_str) - 1

        if 0 <= task_index < len(tasks): # 验证序号是否在原始 tasks 列表的范围内
            task_to_edit = tasks[task_index] # 直接修改原始列表中的任务
            print(Fore.CYAN + f"\n--- 正在编辑任务: '{task_to_edit['description']}' ---")

            new_description = get_validated_description_input(current_description=task_to_edit['description'])
            task_to_edit['description'] = new_description
            
            new_due_date = get_validated_due_date_input(current_due_date=task_to_edit.get('due_date'))
            task_to_edit['due_date'] = new_due_date

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
    try:
        actual_index = int(task_index_str) - 1
        if 0 <= actual_index < len(tasks):
            removed_task = tasks.pop(actual_index)
            print(Fore.GREEN + f"任务 '{removed_task['description']}' 已删除。")
        else:
            print(Fore.RED + "错误：无效的任务序号。")
    except ValueError:
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")

# --- 新增：排序与过滤功能 ---
def sort_tasks(tasks_list, sort_key, reverse_order=False):
    """根据指定的键对任务列表进行排序。返回一个新的排序后的列表。"""
    if not tasks_list:
        return []

    if sort_key == "description":
        # 按描述字母顺序排序，忽略大小写
        return sorted(tasks_list, key=lambda task: task['description'].lower(), reverse=reverse_order)
    
    elif sort_key == "due_date":
        # 按截止日期排序。None 值（无截止日期）被视为“最大”，所以会排在最后（升序时）。
        # 为了正确排序含 None 的日期，我们用一个 lambda 返回一个元组。
        # Python在排序元组时，会逐个比较元组的元素。
        # (due_date is None, due_date_object_or_original_string)
        # 如果 due_date is None 为 True (1)，则它比 False (0) 大，所以 None 会排在后面。
        # 如果两个都是日期，则比较日期对象。
        return sorted(tasks_list, key=lambda task: (
            task.get('due_date') is None, # True (1) if None, False (0) if has date
            # 如果日期存在，尝试解析为datetime对象进行比较，否则使用原始字符串或一个极大/小值
            # 为了简单起见，如果 due_date 存在，我们直接用字符串 "YYYY-MM-DD" 比较，它本身就有序
            # 如果 due_date 是 None，我们让它在元组的第二部分保持 None (或一个标记值)
            task.get('due_date') if task.get('due_date') else "" # 使用空字符串让None排在有日期的前面（如果元组第一项相同）
                                                                # 或使用一个极大值字符串，让None排在有日期的后面
                                                                # e.g. task.get('due_date') if task.get('due_date') else "9999-99-99" for None last
        ), reverse=reverse_order)

    elif sort_key == "priority":
        # 按优先级排序：High (0) > Medium (1) > Low (2) > None (3)
        # PRIORITY_ORDER_MAP 预定义了顺序
        return sorted(tasks_list, key=lambda task: PRIORITY_ORDER_MAP.get(task.get('priority')), reverse=reverse_order)
    
    else:
        print(Fore.RED + "错误：无效的排序键。")
        return tasks_list # 返回原列表副本

def filter_tasks(tasks_list, filter_type, filter_value=None):
    """根据指定的类型和值过滤任务列表。返回一个新的过滤后的列表。"""
    if not tasks_list:
        return []

    if filter_type == "status":
        # filter_value 应该是 True (已完成) 或 False (未完成)
        return [task for task in tasks_list if task['completed'] == filter_value]
    
    elif filter_type == "priority":
        # filter_value 应该是 "high", "medium", "low", 或 None (代表无优先级)
        # .get('priority') 会返回 None 如果键不存在或值为 None
        # 我们要匹配用户输入的 filter_value (可能是 None)
        return [task for task in tasks_list if task.get('priority') == filter_value]
    
    else:
        print(Fore.RED + "错误：无效的过滤类型。")
        return tasks_list # 返回原列表副本

def handle_advanced_view_options(tasks):
    """处理高级查看选项的子菜单。"""
    if not tasks:
        print(Fore.YELLOW + "当前没有任务可供排序或过滤。")
        return

    while True:
        print(Fore.CYAN + "\n--- 高级查看选项 ---")
        print("1. 按描述排序")
        print("2. 按截止日期排序")
        print("3. 按优先级排序")
        print("4. 过滤已完成任务")
        print("5. 过滤未完成任务")
        print("6. 按优先级过滤")
        print("0. 返回主菜单")
        
        sub_choice = input("请选择操作 (0-6): ")
        
        # 创建任务列表的副本进行操作，以免修改原始列表
        tasks_copy_for_display = list(tasks) # 或者 tasks[:]

        if sub_choice == '1':
            rev = input("升序 (a) 还是降序 (d)? [a]: ").lower() == 'd'
            sorted_list = sort_tasks(tasks_copy_for_display, "description", reverse_order=rev)
            view_tasks(sorted_list, title="--- 按描述排序后 ---")
        elif sub_choice == '2':
            rev = input("升序 (a) 还是降序 (d)? [a]: ").lower() == 'd'
            sorted_list = sort_tasks(tasks_copy_for_display, "due_date", reverse_order=rev)
            view_tasks(sorted_list, title="--- 按截止日期排序后 ---")
        elif sub_choice == '3':
            rev = input("升序 (高->低 a) 还是降序 (低->高 d)? [a]: ").lower() == 'd'
            # 注意：PRIORITY_ORDER_MAP 中 High=0, Medium=1, Low=2, None=3
            # 所以升序 (reverse=False) 会是 High, Medium, Low, None
            # 如果用户选 'a' (高->低)，对应 PRIORITY_ORDER_MAP 的升序，所以 reverse_order=False
            # 如果用户选 'd' (低->高)，对应 PRIORITY_ORDER_MAP 的降序，所以 reverse_order=True
            actual_reverse = rev 
            sorted_list = sort_tasks(tasks_copy_for_display, "priority", reverse_order=actual_reverse)
            view_tasks(sorted_list, title="--- 按优先级排序后 ---")
        elif sub_choice == '4': # 过滤已完成
            filtered_list = filter_tasks(tasks_copy_for_display, "status", filter_value=True)
            view_tasks(filtered_list, title="--- 已完成的任务 ---")
        elif sub_choice == '5': # 过滤未完成
            filtered_list = filter_tasks(tasks_copy_for_display, "status", filter_value=False)
            view_tasks(filtered_list, title="--- 未完成的任务 ---")
        elif sub_choice == '6':
            priority_to_filter = input(f"请输入要查看的优先级 ({'/'.join(p for p in VALID_PRIORITIES if p)}, 或留空代表'无优先级'): ").strip().lower()
            if priority_to_filter in VALID_PRIORITIES:
                actual_filter_value = priority_to_filter if priority_to_filter else None
                filtered_list = filter_tasks(tasks_copy_for_display, "priority", filter_value=actual_filter_value)
                view_tasks(filtered_list, title=f"--- 优先级为 '{format_priority_display(actual_filter_value)}' 的任务 ---")
            else:
                print(Fore.RED + "无效的优先级输入。")
        elif sub_choice == '0':
            break
        else:
            print(Fore.RED + "无效的选择，请输入0到6之间的数字。")

# --- 主程序逻辑 ---
def main():
    """
    程序的主入口和用户交互循环。
    """
    tasks = load_tasks()

    while True:
        print(Fore.BLUE + "\n请选择操作：")
        print("1. 添加任务")
        print("2. 查看所有任务 (原始顺序)") # 强调原始顺序
        print("3. 编辑任务")
        print("4. 标记任务为已完成")
        print("5. 删除任务")
        print("6. 高级查看 (排序/过滤)") # 新增选项
        print("7. 退出")              # 退出选项序号顺延

        choice = input(f"请输入你的选择 (1-{7}): ") # 更新选项范围

        if choice == '1':
            add_task(tasks)
            save_tasks(tasks)
        elif choice == '2':
            view_tasks(tasks, title="--- 所有任务 (原始顺序) ---") # 默认查看原始列表
        elif choice == '3':
            # edit_task 内部会调用 view_tasks(tasks, title="--- 原始任务列表 (供编辑选择) ---")
            # 所以这里不需要先 view_tasks
            edit_task(tasks)
            save_tasks(tasks) 
        elif choice == '4':
            print(Fore.MAGENTA +"请参考以下原始任务列表选择要操作的序号：")
            view_tasks(tasks, title="--- 原始任务列表 (供操作选择) ---")
            if tasks:
                task_num_str = input("请输入要标记为完成的任务序号: ")
                mark_task_completed(tasks, task_num_str)
                save_tasks(tasks)
        elif choice == '5':
            print(Fore.MAGENTA +"请参考以下原始任务列表选择要操作的序号：")
            view_tasks(tasks, title="--- 原始任务列表 (供操作选择) ---")
            if tasks:
                task_num_str = input("请输入要删除的任务序号: ")
                delete_task(tasks, task_num_str)
                save_tasks(tasks)
        elif choice == '6': # 新增：高级查看
            handle_advanced_view_options(tasks)
        elif choice == '7': # 更新：退出程序
            print(Fore.GREEN + "感谢使用，任务已保存。再见！")
            break
        else:
            print(Fore.RED + f"无效的选择，请输入1到{7}之间的数字。")

if __name__ == "__main__":
    main()