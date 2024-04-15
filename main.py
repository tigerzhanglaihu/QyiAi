# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
from flask import Flask
import simple
import api
import standard
# 创建 Flask 应用
main = Flask(__name__)

@main.route('/')
def index():
    return simple

@main.route('/api')
def api():
    return api

@main.route('/standard')
def standard():
    return standard

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 运行应用，监听 5000 端口
    main.run(debug=True)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
