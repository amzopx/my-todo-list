# hello_pyqt.py

import sys # 用于访问与 Python 解释器相关的变量和函数，如此处的退出状态。

# 从 PyQt6.QtWidgets 模块导入必要的类
# QApplication: 管理GUI应用程序的控制流和主要设置。
# QWidget: 所有用户界面对象的基类。我们用它作为主窗口。
# QLabel: 用于显示文本或图像。
# QVBoxLayout: 一种布局类，将子控件垂直排列。
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

# 1. 创建 QApplication 实例
# 每个 PyQt GUI 应用都需要一个 QApplication 实例。
# sys.argv 是一个传递给 Python 脚本的命令行参数列表。
# QApplication 可以使用一些系统相关的参数进行初始化。
app = QApplication(sys.argv)

# 2. 创建主窗口
# 我们创建一个 QWidget 对象作为我们的主窗口。
# QWidget 是一个没有任何特殊功能的空白窗口。
window = QWidget()
window.setWindowTitle('你好, PyQt6!') # 设置窗口标题
window.setGeometry(200, 200, 300, 100) # 设置窗口位置和大小 (x, y, width, height)

# 3. 创建一个控件 (例如，一个标签 QLabel)
# QLabel 用于显示文本。
hello_label = QLabel('Hello, World! 欢迎使用 PyQt6！')

# 4. 创建一个布局管理器
# QVBoxLayout 会将控件垂直排列。
layout = QVBoxLayout()

# 5. 将控件添加到布局中
layout.addWidget(hello_label) # 将标签添加到垂直布局中

# 6. 将布局应用到主窗口
window.setLayout(layout)


# 7. 显示窗口
# 调用 show() 方法使窗口可见。
window.show()

# 8. 运行应用程序的事件循环
# app.exec() 启动 Qt 的事件循环。
# 事件循环会等待用户操作（如点击、键盘输入等）并做出响应。
# 程序会一直在这个循环中运行，直到窗口被关闭。
# sys.exit() 确保程序在退出时能够干净地关闭，并返回退出状态码给操作系统。
sys.exit(app.exec())