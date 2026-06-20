# 原教程知识点覆盖矩阵

| 原始教程 | 重编后集数 | 覆盖方式 |
|---|---:|---|
| What is Claude Code | 01 | 用“让它随便看看，它已经开始干活”的场景讲清：它不是聊天框，而是能读文件、改代码、跑命令、调用工具的代理式编程工具。 |
| Installing Claude Code | 01 | 合并终端、IDE、Desktop、Web 四种入口，重点讲目录权限、首次登录、API Key / 账号、选择使用场景。 |
| How Claude Code Works | 01, 02, 03 | 拆进代理循环、工具调用、权限模式、上下文窗口、压缩和验证过程。 |
| Your first Claude Code prompt | 02 | 用“加个暗黑模式，结果改多了”的故事讲目标、范围、约束、验收标准和 Plan Mode。 |
| The CLAUDE.md file | 03 | 用“昨天会启动，今天又问一遍”的场景讲项目级记忆、用户级记忆、`/init`、团队共享和禁写内容。 |
| Explore Plan Code Commit workflow | 02 | 作为第二集主结构，讲探索、计划、编码、验证、提交。 |
| Context Management in Claude Code | 03 | 讲上下文窗口、自动压缩、文件引用、任务拆分、上下文冲突和开新会话时机。 |
| MCP in Claude Code | 06 | 放入最终工作流，解释如何让 Claude Code 接数据库、GitHub、浏览器、文档和内部工具。 |
| Hooks in Claude Code | 06 | 讲自动触发测试、lint、build、eval、通知和日志，强调自动化质量门。 |
| What are subagents | 04 | 用“派了三个 AI 同事，会议室更乱了”的事故讲子代理定义和独立上下文。 |
| Using subagents effectively | 04 | 强调适用场景：研究、独立任务、代码审查；不适用场景：强依赖连续任务。 |
| Designing effective subagents | 04 | 给出目标、边界、上下文、交付标准四要素。 |
| Creating a subagent | 04 | 给出可直接录屏使用的子代理任务模板。 |
| What are skills | 05 | 用“复制 27 次同一段提示词”讲 Skill 是可复用工作流，不是普通提示词收藏。 |
| Creating your first skill | 05 | 讲从高频任务出发创建第一个 Skill，并测试它是否稳定。 |
| Configuration and multi-file skills | 05 | 讲模板、配置、参考资料、多文件 Skill 的组织方式。 |
| Troubleshooting skills | 05 | 讲系统化排障 Skill：复现、日志、配置、假设、验证。 |
| Sharing skills | 05 | 讲团队共享、版本控制、评审和更新。 |
| How skills compare to other features | 05, 06 | 第五集讲 Skill 和提示词、`CLAUDE.md`、Subagent 的区别；第六集统一比较 MCP、Hooks、Subagents、Skills、`CLAUDE.md`。 |

## 项目实践弱化策略

| 项目元素 | 使用集数 | 使用方式 |
|---|---:|---|
| AI 导演工作台 | 01, 02, 03, 06 | 不讲产品全貌，只作为“复杂项目”的真实画面。 |
| 质量分 / 作品包 | 02, 05 | 用于解释验收标准和 Skill。 |
| Supabase / GitHub / 浏览器 | 06 | 用于解释 MCP 为什么有用。 |
| test / lint / build / eval | 02, 06 | 用于解释验证和 Hooks。 |
| Subagents / Skills 模板 | 04, 05 | 项目名可出现，但不是剧情主角。 |
