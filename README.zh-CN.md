# Review-Execute Loop

一个面向长任务的轻量、平台中立双窗口工作流。

它把 AI 协作分为三种职责：

- **审阅者 / 调度者（Reviewer）**：检查结果、和用户讨论、准备下一项已批准任务；
- **执行者（Executor）**：只完成一个已经批准的任务，记录结果后停止；
- **用户（User）**：决定继续、调整目标、暂停或结束。

它既可用于科研，也可用于软件、写作、分析和其他多步骤任务，不依赖特定模型、付费服务、本地 skill 或任务通信 API。

## 为什么需要双窗口

长任务常见的问题是：同一个窗口同时规划、执行并审查自己，随后自行扩大范围；上下文压缩后又会反复读取大量历史文件。

本工具包只保留几条稳定边界：

- 执行者不能批准下一项任务；
- 审阅者不能执行自己正在审阅的任务；
- 每个新范围都由用户确认；
- 每个 prompt 和结果都有稳定 ID；
- 恢复上下文时先读当前任务和最近状态，不扫描全部历史；
- 支持自动直接发送，也始终保留人工复制回退。

## 两种模式

### Direct Loop，直接闭环

适用于支持任务之间直接发送消息的 AI 应用：

```text
用户 <-> 审阅窗口 --已批准 prompt--> 执行窗口
             ^                         |
             +--------结果回执---------+
```

用户通常只和审阅窗口交流。审阅窗口在用户批准后生成一个完整 prompt，只派发一次；执行窗口完成后只返回一次结果。

### Manual Relay，人工转交

适用于 Web Chat、不同 AI 产品、不同机器，或者不支持直接通信的环境：

```text
审阅 prompt -> 用户复制 -> 执行窗口
执行结果 -> 用户复制 -> 审阅窗口
```

两种模式使用同一套 prompt 和结果格式，只改变传输方法。

## 五分钟开始

### 方法 A：初始化脚本

只需要 Python 3.9 及以上版本，不需要第三方库。

```bash
python tools/init.py E:/path/to/project --profile research --mode direct
```

可选 Profile：`generic`、`research`、`software`、`writing`。可选模式：`direct`、`manual`。

初始化程序不会覆盖已有 `.workflow/` 或 `AGENTS.md`。如果项目已有 `AGENTS.md`，它会保持原文件不变，并把建议加入的 Codex 规则写到 `.workflow/` 中供人工合并。

### 方法 B：手动复制

1. 把 `starter/.workflow/` 复制到项目根目录。
2. 把 `templates/` 复制为 `.workflow/templates/`。
3. 从 `profiles/` 选择一个文件，复制为 `.workflow/PROFILE.md`。
4. 使用 Codex 时，把 `starter/AGENTS.md.example` 的相关内容合并到项目根目录 `AGENTS.md`，不要覆盖已有项目规则。
5. 填写 `PROJECT_BRIEF.md` 和 `WORKFLOW_STATE.md`。
6. 把 `.workflow/templates/EXECUTOR_START.md` 交给执行窗口。
7. 把 `.workflow/templates/REVIEWER_START.md` 交给审阅窗口。

Direct 模式在常规派发前需要两个不同且真实的任务 ID。Manual 模式可以把任务 ID 保持为 `NOT_APPLICABLE`。

## 第一个完整循环

1. 在第一个窗口讨论目标，先不执行任务。
2. 和用户确认 `PROJECT_BRIEF.md`。
3. 第一个窗口成为执行窗口，只完成初始化。
4. 新建一个独立审阅窗口，或者在 Manual 模式使用 Web 审阅。
5. 审阅窗口查看最近结果，先和用户讨论下一项范围。
6. 用户同意后，审阅窗口填写一个 `EXECUTION_PROMPT.md`。
7. 执行窗口执行任务，生成一个 `STEP_RESULT.md`，追加一条完成事件并停止。
8. 审阅窗口审查结果；只有再次得到用户确认才推进下一项任务。

## 项目中长期保留的文件

只要求四个文件：

| 文件 | 作用 |
|---|---|
| `.workflow/WORKFLOW.md` | 稳定角色、安全规则、恢复方式和循环规则 |
| `.workflow/PROJECT_BRIEF.md` | 当前目标、范围、约束和验收标准 |
| `.workflow/WORKFLOW_STATE.md` | 模式、窗口绑定、当前 prompt 和返回目标 |
| `.workflow/STEP_LOG.md` | 只增不改的简短步骤日志 |

每项任务只新增一个完整 prompt、一个结果记录以及真正的任务产物。不强制生成独立 summary、status flags、handoff 包或证据台账。

## 上下文恢复

- 正常执行：当前 prompt、与它对应的最近日志状态、prompt 点名文件；
- 新窗口或上下文压缩：额外读取 `WORKFLOW.md` 并确认角色；
- 深度恢复：只有缺少明确事实时，才读取旧结果。

日志中的路径只是索引，不代表需要递归读取所有文件。

## Profile

- `generic`：通用任务和产物管理；
- `research`：与任务规模相称的证据、来源和复现检查；
- `software`：范围受控的代码修改、测试和迁移安全；
- `writing`：来源忠实、版本保留和引用安全。

默认只选择最相关的一个，不要把所有 Profile 一起加载。

## 校验

检查工具包本身：

```bash
python tools/validate.py --distribution .
```

检查已经初始化的项目：

```bash
python tools/validate.py --project E:/path/to/project
```

校验程序只读，不修改项目。

## v0.1 有意不包含的功能

首版不包含服务器调度、论文投稿、复杂 Evidence 数据库、多执行窗口并行、自动 Pro 升级以及领域专用审批体系。真实项目需要这些能力时，应作为独立扩展加入，不改变双窗口核心。

## 许可

MIT，见 [LICENSE](LICENSE)。
