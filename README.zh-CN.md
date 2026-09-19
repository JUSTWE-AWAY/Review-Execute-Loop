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
- 重大决策可以暂停并进入可选的 Pro 深度审查，但不能绕过用户批准。

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
执行窗口 -> 单步平铺审阅压缩包 -> 用户 -> Web 审阅窗口
执行窗口 <- 审阅结论和已批准 prompt <- 用户 <- Web 审阅窗口
```

每个完成步骤都会在 `.workflow/review_packets/` 下形成一个自包含、平铺的审阅包。Web 审阅窗口只读取这个包，先和用户讨论，再在确认后返回 `REVIEW_RETURN.md` 与一个完整的下一步 prompt。本地执行窗口原样归档这两个文件，使外部审阅结论仍进入项目日志。两种模式使用同一套 prompt 和结果格式，只改变传输方法。

## 五分钟开始

先获取工具包：

```bash
git clone https://github.com/JUSTWE-AWAY/Review-Execute-Loop.git
cd Review-Execute-Loop
```

也可以在 GitHub 页面选择 **Code > Download ZIP**，解压后在该目录打开终端。

### 方法 A：初始化脚本

只需要 Python 3.9 及以上版本，不需要第三方库。

Windows：

```powershell
py -3 tools/init.py E:/path/to/project --profile research --mode direct
```

macOS 或 Linux：

```bash
python3 tools/init.py /path/to/project --profile research --mode direct
```

可选 Profile：`generic`、`research`、`software`、`writing`。可选模式：`direct`、`manual`。

初始化程序不会覆盖已有 `.workflow/`、`AGENTS.md`、`incoming/` 或 `deliverables/` 目录。如果项目已有 `AGENTS.md`，它会保持原文件不变，并把建议加入的 Codex 规则写到 `.workflow/` 中供人工合并。

把旧论文、既有记录、数据、模型、代码等外部起始材料放入项目根目录 `incoming/`。其中内容是不可变源材料：工作流可以读取和复制，但不能编辑、重命名、移动、隔离或删除。派生文件必须写到其他位置。

### 方法 B：手动复制

1. 把 `starter/.workflow/` 复制到项目根目录。
2. 只有在项目尚无 `incoming/` 时，才把 `starter/incoming/` 复制到项目根目录。
3. 只有在项目尚无正式产物目录时，才把 `starter/deliverables/` 复制到项目根目录。
4. 把 `templates/` 复制为 `.workflow/templates/`。
5. 从 `profiles/` 选择一个文件，复制为 `.workflow/PROFILE.md`。
6. 使用 Codex 时，把 `starter/AGENTS.md.example` 的相关内容合并到项目根目录 `AGENTS.md`，不要覆盖已有项目规则。
7. 把 `.workflow/templates/PROJECT_SETUP_START.md` 交给第一个项目任务。
8. Brief 和 Step 0 范围获批后，在同一任务运行 `.workflow/templates/STEP0_START.md`。
9. Step 0 结果存在后，再把 `.workflow/templates/REVIEWER_START.md` 交给独立审阅窗口。

Direct 模式在常规派发前需要两个不同且真实的任务 ID；平台支持时还要记录双方深度链接。Manual 模式可以把任务 ID 和链接保持为 `NOT_APPLICABLE`。

## 第一个完整循环

1. 把起始材料放入 `incoming/`，再把 `PROJECT_SETUP_START.md` 交给第一个任务。
2. 该任务此时是“启动协调者 / 执行候选者”，负责讨论 Brief、可选参考计划、产物结构、传输模式和 Step 0 范围，不做实质项目工作。
3. 用户明确同意后，同一候选任务运行固定的 `STEP0_START.md` 盘点并停止。
4. Direct 模式新建独立本地审阅窗口；Manual 模式生成一个平铺 Web 审阅包。
5. 独立审阅者检查 Step 0，并和用户讨论修正。只有审阅通过且用户确认，候选任务才晋升为正式执行窗口。
6. 用户同意后，审阅窗口生成一个完整 `EXECUTION_PROMPT.md`。Direct 模式直接派发；Manual 模式通过 `REVIEW_RETURN.md` 与 prompt 原样导回项目。
7. 执行窗口只执行该 prompt，生成一个 `STEP_RESULT.md`、追加一次完成事件，然后停止。
8. 审阅窗口检查结果；只有再次得到用户确认才推进下一项任务。

真正空白且简单的项目只有在用户明确同意、独立审阅者也接受启动记录时才可跳过 Step 0。第一个任务不能审阅或晋升自己。

## 项目中长期保留的文件

四个文件构成人工阅读的核心：

| 文件 | 作用 |
|---|---|
| `.workflow/WORKFLOW.md` | 稳定角色、安全规则、恢复方式和循环规则 |
| `.workflow/PROJECT_BRIEF.md` | 当前目标、范围、约束和验收标准 |
| `.workflow/WORKFLOW_STATE.md` | 模式、窗口绑定、当前 prompt 和返回目标 |
| `.workflow/STEP_LOG.md` | 只增不改的简短步骤日志 |

`.workflow/REFERENCE_PLAN.md` 是可选文件，用来记录暂定路线、决策点、回退方向和假设；它不冻结探索路线，也不授权执行。

`.workflow/INSTALL_MANIFEST.json` 只记录由 toolkit 管理的文件及哈希，供安全升级使用，不接管项目文件。`incoming/` 保存用户传入的起始材料，`deliverables/` 保存已经批准的最终产物。

每项任务只新增一个完整 prompt、一个结果记录以及真正的任务产物。Direct 模式不强制生成 handoff 包；Manual 模式因为外部审阅者不能直接读取项目，所以每步额外生成一个平铺审阅包。不强制生成独立 status flags、证据台账，也不要求重读全部历史。

## 步骤、重试与计划修改

- `step0`：执行窗口晋升前的固定启动盘点；
- `step1`、`step2`：主推进步骤；
- `step2a`、`step2b`：并列子步骤；
- `step2a.1`：更深一级子步骤；
- `step2a.1-r1`：经过审阅的重试或恢复；
- 结构化编号后可以附一个简短说明后缀。

技术错误可以在 Prompt 批准的修复额度内处理；后续重试使用新的 Prompt 和 ID。新证据只改变优选路线而不改变最终目标和边界时，新建参考计划版本；目标或保护边界变化时，新建 Project Brief 版本。失败结果和旧计划都应保留，不能改写历史。

## Web 审阅包

Manual 模式的执行结果完成后，在项目根目录运行：

```bash
python /path/to/Review-Execute-Loop/tools/review_packet.py create . --result .workflow/step_records/<step>/STEP_RESULT.md --include <重要项目文件>
```

把生成的 ZIP 交给 Web 审阅窗口。讨论并确认后，保存它返回的两个文件，再导入项目：

```bash
python /path/to/Review-Execute-Loop/tools/review_packet.py import . --packet .workflow/review_packets/<审阅包目录> --review-return /path/to/REVIEW_RETURN.md --prompt /path/to/NEXT_EXECUTION_PROMPT.md
```

附件必须来自项目内部，并会用编号复制到同一个平铺目录。不要附带整个项目、秘密信息或无关历史。

## 更新已有项目

toolkit 仓库与项目保持分离。拉取新版后，可让本地执行窗口读取 `WORKFLOW_UPDATE_START.md`，或依次运行：

```bash
python /path/to/Review-Execute-Loop/tools/update_project.py /path/to/project --check
python /path/to/Review-Execute-Loop/tools/update_project.py /path/to/project --prepare
python /path/to/Review-Execute-Loop/tools/update_project.py /path/to/project --apply <已批准的升级ID>
```

`--check` 只读；`--prepare` 只生成升级计划；`--apply` 只安装未被修改的 toolkit 管理文件和安全新增项，并备份被替换文件。冲突项保持不动。它不会覆盖 Project Brief、计划、日志、prompt、结果、审阅包、`AGENTS.md`、`incoming/`、`deliverables/`、代码、数据或用户产物。

## 可选 Pro 审查

Pro Review 指一个临时的深度审查角色，使用更多思考时间处理重大决策或独立冷审，不代表特定模型或产品。对于重大路线、架构、方法、结论、发布、高成本投入、证据冲突，或者用户主动要求冷审的情况，Reviewer 可以建议介入。

用户确认后，Reviewer 在 `.workflow/pro_reviews/` 下生成一个小型平铺审查包。Pro 返回 `PRO_FEEDBACK.md`，正常 Reviewer 再和用户讨论采纳、部分采纳、暂缓或拒绝。`PRO_DRAFT_PROMPT` 只是建议，不能直接交给 Executor 执行。

## 最终产物

经过用户确认的论文、发布包、交付物或其他正式产物统一放在 `deliverables/`：

```text
deliverables/
├─ 001_<主要产物>/
├─ 002_<辅助产物>/
└─ 003_<其他产物>/
```

候选结果和临时结果留在其他位置。已有编号不重新排序。每个编号目录可以根据任务使用 `source/`、`figures/`、`tables/`、`assets/`、`exports/`、`packages/` 或 `docs/` 等细分目录。

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

## 许可

MIT，见 [LICENSE](LICENSE)。
