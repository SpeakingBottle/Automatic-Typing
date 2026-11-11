# 变更日志

> 本项目使用语义化版本 `X.Y.Z`，格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。
> 每个公开版本应创建对应的 Git tag，并按 `docs/history-version/README.md` 归档版本文档。

## [Unreleased]

## [1.0.0] - 2026-11-11

首个公开开源版本。

### Added

- Windows 桌面自动打字工具，支持逐字模拟键盘输入
- 英文字母、数字、代码常用符号、中文、中文标点和 Unicode 字符输入
- 可调打字速度、随机延迟、启动倒计时和跳过行首缩进
- 暂停、继续、停止和读取剪贴板
- PyInstaller 单文件 exe 打包配置
- MIT 开源许可证和项目 README
- 三层文档体系：需求设计、开发参考、版本归档

### Changed

- 项目文件从 `automatic_typing/` 迁移到仓库根目录
- 启动脚本由 `启动自动打字.bat` 更名为 `start.bat`
- 开发文档统一迁移到 `docs/` 并按职责重组
- `CLAUDE.md` 改为 `AGENTS.md` 的入口指针
