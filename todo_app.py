# todo_app.py
# Author: 你的名字
# Version: 0.5 - Added colorama for colored output and requirements.txt
# Recommended to run within a Python virtual environment.

import json
from colorama import Fore, Style, init as colorama_init # 导入 colorama 的特定成员

# --- 初始化 Colorama ---
# autoreset=True 确保颜色设置只对当前 print 生效，之后自动重置。
colorama_init(autoreset=True)

DATA_FILE = "tasks.json"

# --- 文件操作函数 ---
def load_tasks():
    """
    从 JSON 文件中加载任务。
    如果文件不存在或内容为空/无效，则返回一个空列表。
    """
    tasks = []
    try:
        # 'r' 表示以只读模式打开文件
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            # 使用 json.load() 从文件直接加载数据并解析为 Python 对象 (这里是列表)
            tasks_data = json.load(f)
            # 确保加载的数据是列表，并且列表中的每个元素都是字典
            if isinstance(tasks_data, list):
                for item in tasks_data:
                    if isinstance(item, dict) and 'description' in item and 'completed' in item:
                        tasks.append(item)
                    else:
                        print(Fore.YELLOW + "警告：任务文件中的某个条目格式不正确，已忽略。")
                if not tasks and tasks_data: # 如果过滤后tasks为空，但原始数据不为空，说明所有条目都有问题
                     print(Fore.YELLOW + "警告：任务文件格式不正确，将使用空任务列表。")
            else:
                print(Fore.YELLOW + "警告：任务文件顶层结构不是列表，将使用空任务列表。")
                return [] # 如果顶层不是列表，直接返回空
    except FileNotFoundError:
        # 如果文件不存在，说明还没有任务，返回空列表是正常的
        pass
    except json.JSONDecodeError:
        # 如果文件内容不是有效的 JSON (例如文件为空，或手动修改坏了)
        print(Fore.YELLOW + f"警告：'{DATA_FILE}' 内容不是有效的JSON格式或为空。将使用空任务列表。")
        return [] # 对于空文件或无效JSON，显式返回空列表
    except Exception as e:
        # 捕获其他可能的读取错误
        print(Fore.RED + f"加载任务时发生未知错误: {e}")
    return tasks

def save_tasks(tasks):
    """
    将任务列表以 JSON 格式保存到文件。
    """
    try:
        # 'w' 表示以写入模式打开文件（如果文件已存在，会覆盖内容）
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            # 使用 json.dump() 将 Python 列表 (tasks) 序列化为 JSON 字符串并写入文件
            # indent=4 参数会让 JSON 文件格式化输出，更易读（每个层级缩进4个空格）
            # ensure_ascii=False 确保中文字符能正确写入而不是被转义成 \uXXXX 形式
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        # 捕获可能的写入错误
        print(Fore.RED + f"保存任务时发生错误: {e}")


# --- 任务管理核心函数 ---
def add_task(tasks, description):
    """
    向任务列表中添加一个新任务。
    新任务默认为未完成状态。
    """
    if not description.strip(): # 检查描述是否为空或只包含空白字符
        # 使用 colorama 设置错误信息为红色
        print(Fore.RED + "错误：任务描述不能为空！")
        return
    # 创建一个新的任务字典
    new_task = {'description': description, 'completed': False}
    # 将新任务添加到任务列表
    tasks.append(new_task)
    # 使用 colorama 设置成功信息为绿色
    print(Fore.GREEN + f"任务 '{description}' 已添加。")

def view_tasks(tasks):
    """
    显示所有任务及其状态。
    """
    if not tasks:
        print(Fore.YELLOW + "当前没有任务。") # 给提示信息也加点颜色
        return

    print(Fore.CYAN + "\n--- 你的任务清单 ---") # 给标题加颜色
    # enumerate 函数可以同时获取索引和元素
    for index, task in enumerate(tasks):
        if task['completed']:
            # 已完成任务：绿色文字，标记为 [x]
            status_marker = Fore.GREEN + "[x]"
            task_text = Fore.GREEN + task['description']
        else:
            # 未完成任务：黄色文字（或者你可以选择其他颜色），标记为 [ ]
            status_marker = Fore.YELLOW + "[ ]"
            task_text = Fore.YELLOW + task['description']
        
        # 打印任务，索引从1开始，方便用户选择
        # Style.RESET_ALL 可以在这里确保后续的 print 不受影响，但因为我们用了 autoreset=True，所以不是严格必须
        print(f"{index + 1}. {status_marker} {task_text}")

    print(Fore.CYAN + "--------------------") # 给标题加颜色

def mark_task_completed(tasks, task_index_str):
    """
    将指定索引的任务标记为已完成。
    task_index_str 是用户看到的从1开始的索引字符串。
    """
    try:
        # 用户输入的索引是从1开始的，程序内部列表索引是从0开始，所以需要减1
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
        # 如果用户输入的不是数字
        print(Fore.RED + "错误：请输入有效的任务序号（数字）。")

def delete_task(tasks, task_index_str):
    """
    删除指定索引的任务。
    task_index_str 是用户看到的从1开始的索引字符串。
    """
    try:
        actual_index = int(task_index_str) - 1
        if 0 <= actual_index < len(tasks):
            # list.pop(index) 可以移除列表中指定索引的元素
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
    # 注意：load_tasks, save_tasks, add_task 等函数内部也使用了 Fore，
    # 所以 colorama_init(autoreset=True) 放在程序开始处是好的。
    tasks = load_tasks() # 程序启动时，首先从文件加载已有任务

    while True:
        print(Fore.CYAN + "\n请选择操作：") # 给菜单标题加颜色
        print("1. 添加任务")
        print("2. 查看任务")
        print("3. 标记任务为已完成")
        print("4. 删除任务")
        print("5. 退出")

        choice = input("请输入你的选择 (1-5): ")

        if choice == '1':
            description = input("请输入任务描述: ")
            add_task(tasks, description)
            save_tasks(tasks) # 每次修改后都保存任务
        elif choice == '2':
            view_tasks(tasks)
        elif choice == '3':
            view_tasks(tasks) # 先显示任务，方便用户选择
            if tasks: # 只有在有任务时才要求输入序号
                task_num_str = input("请输入要标记为完成的任务序号: ")
                mark_task_completed(tasks, task_num_str)
                save_tasks(tasks) # 每次修改后都保存任务
        elif choice == '4':
            view_tasks(tasks) # 先显示任务，方便用户选择
            if tasks: # 只有在有任务时才要求输入序号
                task_num_str = input("请输入要删除的任务序号: ")
                delete_task(tasks, task_num_str)
                save_tasks(tasks) # 每次修改后都保存任务
        elif choice == '5':
            print(Fore.GREEN + "感谢使用，任务已保存。再见！")
            break # 退出循环，结束程序
        else:
            print(Fore.RED + "无效的选择，请输入1到5之间的数字。")

# Python 程序的标准入口点
# 当这个 .py 文件被直接运行时，__name__ 的值是 "__main__"
# 如果它是被其他模块导入的，__name__ 的值就是模块名
if __name__ == "__main__":
    main()