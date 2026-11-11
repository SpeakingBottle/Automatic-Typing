"""
自动打字软件入口。
启动 Windows GUI 应用。
"""

import sys
import os

# 确保项目根目录在 sys.path 中（打包后也能正确导入）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
