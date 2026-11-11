# 发布与打包指南

> 本文说明依赖管理、PyInstaller 打包、发布检查和版本归档流程。
> 测试要求见 [测试指南](testing.md)，版本记录见 [CHANGELOG](../../CHANGELOG.md)。

## 1. 版本约定

- 版本号使用 `X.Y.Z` 语义化版本。
- 每个公开版本在 `CHANGELOG.md` 中增加一条记录。
- 发布时创建 Git tag：`vX.Y.Z`。
- 开发中的版本文档使用 `docs/vX.Y.Z-implementation-guide.md` 和 `docs/vX.Y.Z-test-report.md`；发布后归档到 `docs/history-version/`。

## 2. 依赖管理

### 添加依赖

1. 在 `requirements.txt` 中添加依赖和版本范围。
2. 运行 `pip install -r requirements.txt`。
3. 如需打入 exe，确认 `build.spec` 的 `hiddenimports` 包含新模块。
4. 更新本文件或 `docs/analysis/technical-design.md` 中受影响的说明。

### 依赖审查

- 优先选择 MIT / Apache 2.0 / BSD 协议。
- 避免 GPL 协议依赖（PyInstaller 仅作为构建期工具，不进入分发包）。
- 关注依赖体积，避免引入不必要的大型框架。

## 3. 打包

```bash
# 在项目根目录执行
pip install -r requirements.txt
pyinstaller build.spec
# 输出：dist/自动打字.exe
```

打包配置要点：

- 入口：`main.py`
- 隐藏导入：`customtkinter`、`pyperclip`
- 资源：`datas=[('assets', 'assets')]`
- 应用图标：`icon=str(ROOT / 'assets' / 'app.ico')`
- 单文件 exe
- `console=False`，不显示控制台窗口
- `Pillow` 用于图标加载，已列入 `requirements.txt`
- `main.py` 设置 AppUserModelID，窗口同时使用 `app.ico` 和 `app.png`，确保任务栏图标不是 Python 默认图标
- `start.bat` 使用 `pythonw.exe`，源码启动同样不保留命令行窗口

## 4. 发布前检查清单

- [ ] 所有功能在 Windows 10/11 上测试通过
- [ ] 特殊字符、中文、Unicode、换行和 Tab 输入正常
- [ ] `skip_indent` 开启和关闭行为都验证通过
- [ ] 暂停 / 继续 / 停止正常
- [ ] `python -c "import main"` 通过
- [ ] `test_sendinput.py` 通过
- [ ] `git diff --check` 无输出
- [ ] `pyinstaller build.spec` 打包成功
- [ ] 在无 Python 环境运行 `dist/自动打字.exe` 成功
- [ ] `CHANGELOG.md` 已更新
- [ ] `docs/README.md`、`AGENTS.md`、`README.md` 中的文档链接有效
- [ ] 版本文档已归档到 `docs/history-version/`

## 5. 发布流程

1. 完成需求、实现和测试，确认测试报告结论为通过。
2. 更新 `CHANGELOG.md`，写明新增、变更、修复和已知问题。
3. 更新版本号相关文档；如果代码中新增版本声明，确保与 `CHANGELOG.md` 一致。
4. 执行完整回归和打包验证。
5. 提交变更，创建 `vX.Y.Z` tag，推送 `main` 和 tag。
6. 在 GitHub Release 中填写版本说明，可附上 `dist/自动打字.exe`。
7. 将本版实现指南和测试报告移入 `docs/history-version/`。
8. 更新 `docs/history-version/README.md` 的归档索引。

## 6. 产物与忽略规则

以下内容不提交到仓库：

- `build/`、`dist/`
- `*.spec` 生成的临时文件（`build.spec` 本身保留）
- `__pycache__/`、`*.pyc`
- 虚拟环境和日志

发布产物通过 GitHub Release 或交付渠道分发，不直接提交二进制文件到 `main`。
