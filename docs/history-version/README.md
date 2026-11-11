# 版本归档

> 本目录保存已发布版本的实现指南和测试报告，归档后不再修改。

## 目录约定

开发中的版本文档放在 `docs/` 根目录：

```text
docs/vX.Y.Z-implementation-guide.md
docs/vX.Y.Z-test-report.md
```

发布后移动到本目录：

```text
docs/history-version/vX.Y.Z-implementation-guide.md
docs/history-version/vX.Y.Z-test-report.md
```

模板：

- [implementation-guide.md](templates/implementation-guide.md)
- [test-report.md](templates/test-report.md)

## 归档时机

满足以下条件后归档：

1. 本版需求已实现，测试报告结论为通过。
2. `CHANGELOG.md` 已记录本版变更。
3. `pyinstaller build.spec` 打包验证完成。
4. Git tag `vX.Y.Z` 已创建并推送（如适用）。
5. 文档中的路径、链接和命令与当前仓库一致。

## 归档步骤

1. 将 `docs/vX.Y.Z-implementation-guide.md` 和 `docs/vX.Y.Z-test-report.md` 移入本目录。
2. 更新本文件的“归档索引”。
3. 更新 `CHANGELOG.md` 的版本条目。
4. 全仓搜索旧路径，确认没有指向开发中位置的有效链接。
5. 执行 `git diff --check`，提交归档变更。

## 归档索引

| 版本 | 日期 | 实现指南 | 测试报告 |
|---|---|---|---|
| 1.0.0 | 2026-11-11 | 初始开源基线，未单独归档 | 初始开源基线，未单独归档 |

> 从下一个版本开始，每个版本都应同时归档实现指南和测试报告。
