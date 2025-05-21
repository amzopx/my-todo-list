# todo_app_gui.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QListWidget, QPushButton,
    QLabel # 我们可能需要一个标签来显示状态或标题
)
from PyQt6.QtGui import QFont # For setting font properties
from PyQt6.QtCore import Qt # 主要用于对齐等标志

import core_logic # 导入我们的核心逻辑模块

class TodoAppGUI(QMainWindow): # 继承 QMainWindow 以便将来添加菜单栏、状态栏等
    def __init__(self):
        super().__init__() # 调用父类的构造函数

        self.tasks_data_list = [] # 用于存储从 core_logic 加载的任务字典列表

        self.setWindowTitle('我的任务清单 - PyQt GUI V0.9')
        self.setGeometry(150, 150, 600, 450) # x, y, width, height

        # 创建中心控件和主布局
        central_widget = QWidget() # QMainWindow 需要一个中心控件
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout() # 主垂直布局
        central_widget.setLayout(main_layout)

        # --- UI 控件 ---
        # 标题标签
        title_label = QLabel('任务列表')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # 居中对齐
        
        # 任务列表控件
        self.task_list_widget = QListWidget()
        self.task_list_widget.setStyleSheet("""
            QListWidget {
                font-size: 14px;
            }
            QListWidget::item { 
                padding: 6px; 
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)

        # 按钮
        self.load_button = QPushButton('加载 / 刷新任务')
        self.load_button.setFont(QFont("Arial", 10))
        
        # --- 将控件添加到布局 ---
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.task_list_widget) # 占据大部分空间
        main_layout.addWidget(self.load_button)

        # --- 设置布局的外边距和控件间距 (可选) ---
        main_layout.setContentsMargins(10, 10, 10, 10) # left, top, right, bottom
        main_layout.setSpacing(10) # Spacing between widgets

        # --- 连接信号与槽 ---
        self.load_button.clicked.connect(self.populate_task_list_gui) # 点击按钮时调用

        # --- 初始加载数据 ---
        self.populate_task_list_gui() # 程序启动时自动加载并显示任务

    def populate_task_list_gui(self):
        """从 core_logic 加载任务并填充到 QListWidget 中。"""
        # print("GUI: 正在加载任务...") # 调试信息，可以打印到控制台
        self.tasks_data_list = core_logic.load_tasks_data() # 从核心逻辑加载数据
        
        self.task_list_widget.clear() # 清空列表，防止重复添加

        if not self.tasks_data_list:
            self.task_list_widget.addItem("当前没有任务。")
            # print("GUI: 没有任务数据。")
            return

        # print(f"GUI: 加载了 {len(self.tasks_data_list)} 个任务。")
        for task_item_data in self.tasks_data_list:
            # 构建要在列表项中显示的文本
            status_char = "[x]" if task_item_data.get('completed', False) else "[ ]"
            description = task_item_data.get('description', '无描述')
            
            # 截止日期和优先级 (如果存在)
            due_date_str = task_item_data.get('due_date')
            priority_str = task_item_data.get('priority')

            display_text = f"{status_char} {description}"
            if due_date_str:
                display_text += f" (截止: {due_date_str})"
            if priority_str:
                display_text += f" [优先级: {priority_str.capitalize()}]"
            
            self.task_list_widget.addItem(display_text)
        
        # 后续版本可以考虑根据任务状态给条目设置不同颜色或图标
        # 例如，使用 QListWidgetItem 并设置其 setForeground 或 setIcon

def main_gui():
    app = QApplication(sys.argv) # 创建 QApplication 实例
    main_window = TodoAppGUI()   # 创建我们自定义的主窗口实例
    main_window.show()           # 显示主窗口
    sys.exit(app.exec())         # 启动事件循环

if __name__ == '__main__':
    main_gui()