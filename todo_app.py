# todo_app.py
# Author: 你的名字
# Version: 0.3 - Integrated with Git and GitHub

import json # 导入 json 模块

# 定义存储任务数据的文件名，后缀改为 .json
DATA_FILE = "tasks.json"

# --- 文件操作函数 (使用 JSON) ---
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
            tasks = json.load(f)
            # 确保加载的数据是列表，如果不是（比如文件是空的或格式不对但json.load没报错），
            # 也应该返回空列表或进行更细致的错误处理。
            # json.load 在文件为空时会抛出 json.JSONDecodeError
            if not isinstance(tasks, list):
                print("警告：任务文件格式不正确，将使用空任务列表。")
                return [] # 或者可以尝试修复，但这里简单处理
    except FileNotFoundError:
        # 如果文件不存在，说明还没有任务，返回空列表是正常的
        pass
    except json.JSONDecodeError:
        # 如果文件内容不是有效的 JSON (例如文件为空，或手动修改坏了)
        print(f"警告：'{DATA_FILE}' 内容不是有效的JSON格式或为空。将使用空任务列表。")
        # 对于空文件，可以显式返回空列表，而不是让它可能因其他逻辑而出错
        return []
    except Exception as e:
        # 捕获其他可能的读取错误
        print(f"加载任务时发生错误: {e}")
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
        print(f"保存任务时发生错误: {e}")

# --- 任务管理核心函数 (与 v0.1 基本相同) ---
def add_task(tasks, description):
    """
    向任务列表中添加一个新任务。
    新任务默认为未完成状态。
    """
    if not description.strip():
        print("错误：任务描述不能为空！")
        return
    new_task = {'description': description, 'completed': False}
    tasks.append(new_task)
    print(f"任务 '{description}' 已添加。")

def view_tasks(tasks):
    """
    显示所有任务及其状态。
    """
    if not tasks:
        print("当前没有任务。")
        return

    print("\n--- 你的任务清单 ---")
    for index, task in enumerate(tasks):
        status_marker = "[x]" if task['completed'] else "[ ]"
        print(f"{index + 1}. {status_marker} {task['description']}")
    print("--------------------")

def mark_task_completed(tasks, task_index):
    """
    将指定索引的任务标记为已完成。
    task_index 是用户看到的从1开始的索引。
    """
    try:
        actual_index = int(task_index) - 1
        if 0 <= actual_index < len(tasks):
            if tasks[actual_index]['completed']:
                print(f"任务 '{tasks[actual_index]['description']}' 已经是完成状态。")
            else:
                tasks[actual_index]['completed'] = True
                print(f"任务 '{tasks[actual_index]['description']}' 已标记为完成。")
        else:
            print("错误：无效的任务序号。")
    except ValueError:
        print("错误：请输入有效的任务序号（数字）。")

def delete_task(tasks, task_index):
    """
    删除指定索引的任务。
    task_index 是用户看到的从1开始的索引。
    """
    try:
        actual_index = int(task_index) - 1
        if 0 <= actual_index < len(tasks):
            removed_task = tasks.pop(actual_index)
            print(f"任务 '{removed_task['description']}' 已删除。")
        else:
            print("错误：无效的任务序号。")
    except ValueError:
        print("错误：请输入有效的任务序号（数字）。")

# --- 主程序逻辑 (与 v0.1 基本相同) ---
def main():
    """
    程序的主入口和用户交互循环。
    """
    tasks = load_tasks()

    while True:
        print("\n请选择操作：")
        print("1. 添加任务")
        print("2. 查看任务")
        print("3. 标记任务为已完成")
        print("4. 删除任务")
        print("5. 退出")

        choice = input("请输入你的选择 (1-5): ")

        if choice == '1':
            description = input("请输入任务描述: ")
            add_task(tasks, description)
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
            print("感谢使用，任务已保存。再见！")
            break
        else:
            print("无效的选择，请输入1到5之间的数字。")

if __name__ == "__main__":
    main()