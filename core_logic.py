# core_logic.py
# This file contains the core data handling and business logic 
# for the To-Do application, to be shared by CLI and GUI.

import json
import datetime # datetime is used for date validation

DATA_FILE = "tasks.json"
# 定义核心逻辑层接受的优先级值，None 代表无优先级。
# UI 层在获取用户输入时，可以将空字符串或其他“无”的表示转换成 None 再传给核心逻辑。
VALID_PRIORITIES_CORE = ["high", "medium", "low", None] 

# 核心逻辑层使用的优先级排序映射
PRIORITY_ORDER_MAP_CORE = { 
    "high": 0,
    "medium": 1,
    "low": 2,
    None: 3 # None 或空字符串代表的无优先级排在最后
}

# --- 日期验证 ---
def is_valid_date_format_core(date_string):
    """Checks if the date string is YYYY-MM-DD format and a valid date."""
    if not date_string: # Allows due date to be None (empty string representing no date)
        return True
    try:
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# --- 数据加载与保存 ---
def load_tasks_data():
    """Loads tasks from the JSON data file."""
    tasks = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            if isinstance(tasks_data, list):
                for item in tasks_data:
                    # Ensure essential keys exist and have somewhat expected types before adding
                    if (isinstance(item, dict) and 
                            'description' in item and isinstance(item['description'], str) and
                            'completed' in item and isinstance(item['completed'], bool)):
                        
                        # Sanitize optional fields
                        due_date = item.get('due_date')
                        if due_date and not is_valid_date_format_core(due_date):
                            due_date = None # If stored date is invalid, treat as None

                        priority = item.get('priority')
                        if priority and str(priority).lower() not in [p for p in VALID_PRIORITIES_CORE if p is not None]:
                            priority = None # If stored priority is invalid, treat as None
                        elif priority: # Ensure stored priorities are lowercase if they are strings
                            priority = str(priority).lower()


                        task = {
                            'description': item['description'],
                            'completed': item['completed'],
                            'due_date': due_date, # Already sanitized or None
                            'priority': priority  # Already sanitized or None
                        }
                        tasks.append(task)
            # Silently ignore malformed files or entries for core logic
    except FileNotFoundError:
        pass 
    except json.JSONDecodeError:
        pass 
    except Exception: # Catch-all for other potential I/O or unexpected errors
        pass
    return tasks

def save_tasks_data(tasks):
    """Saves the list of tasks to the JSON data file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
        return True # Indicate success
    except Exception:
        return False # Indicate failure

# --- 核心任务操作函数 (只处理数据，不进行 print/input) ---
def add_task_data(tasks_list, description, due_date=None, priority=None):
    """
    Adds a new task to the tasks_list.
    Returns the new task dictionary if successful, None otherwise.
    """
    clean_description = description.strip() if description else ""
    if not clean_description:
        return None # Description is mandatory

    # Validate and normalize due_date
    valid_due_date = None
    if due_date:
        if is_valid_date_format_core(due_date):
            valid_due_date = due_date
        # else: due_date is invalid, so it remains None implicitly for new_task

    # Validate and normalize priority
    valid_priority = None
    if priority:
        normalized_priority = str(priority).lower()
        if normalized_priority in [p for p in VALID_PRIORITIES_CORE if p is not None]: # Check against "high", "medium", "low"
            valid_priority = normalized_priority
    
    new_task = {
        'description': clean_description,
        'completed': False,
        'due_date': valid_due_date,
        'priority': valid_priority 
    }
    tasks_list.append(new_task)
    return new_task

def update_task_data(task_dict, new_description, new_due_date=None, new_priority=None):
    """
    Updates an existing task dictionary.
    Returns True if updated, False if new_description is invalid.
    """
    clean_new_description = new_description.strip() if new_description else ""
    if not clean_new_description:
        return False # Cannot update to an empty description
    
    task_dict['description'] = clean_new_description
    
    # Validate and update due_date
    if new_due_date: # If a new due date string is provided
        if is_valid_date_format_core(new_due_date):
            task_dict['due_date'] = new_due_date
        else:
            # Option: raise error, return False, or keep old date.
            # For now, if invalid new date provided, we don't change it.
            # A better approach might be for this function to return a status/error.
            # Or, UI layer MUST pre-validate. Let's assume UI pre-validates or sends None.
            pass # If new_due_date is invalid, it's not updated from its current value
    elif new_due_date is None: # Explicitly setting to None (or empty string from UI meaning None)
         task_dict['due_date'] = None


    # Validate and update priority
    if new_priority: # If a new priority string is provided
        normalized_new_priority = str(new_priority).lower()
        if normalized_new_priority in [p for p in VALID_PRIORITIES_CORE if p is not None]:
            task_dict['priority'] = normalized_new_priority
        # else: invalid new priority string, do not change.
    elif new_priority is None: # Explicitly setting to None (or empty string from UI meaning None)
        task_dict['priority'] = None
    
    return True

def get_task_by_original_index(tasks_list, index):
    """Safely gets a task by its original index from a list."""
    if 0 <= index < len(tasks_list):
        return tasks_list[index]
    return None

def delete_task_data(tasks_list, task_index):
    """Deletes a task from the list by index. Returns True if successful."""
    if 0 <= task_index < len(tasks_list):
        tasks_list.pop(task_index)
        return True
    return False

def toggle_task_completion_data(task_dict):
    """Toggles the completion status of a task dictionary."""
    if task_dict:
        task_dict['completed'] = not task_dict.get('completed', False)
        return True
    return False

# Sorting and filtering logic can be added here later if complex
# For now, the main PRIORITY_ORDER_MAP_CORE is here for reference by UIs