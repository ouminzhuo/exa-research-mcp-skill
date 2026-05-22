# Exa Research MCP Skills

面向 **Codex、OpenClaw、Claude Code** 等 `SKILL.md` 兼容智能体的 Exa 企业与市场研究技能包。

本仓库最初基于 Claude Code + Exa MCP 构建，现在新增了可移植的 `skills/` 目录：每个技能都使用标准 `SKILL.md`（仅 `name` + `description` frontmatter）和可选的 `agents/openai.yaml`，便于 Codex/OpenAI 界面识别，也便于 OpenClaw 按技能目录加载。

## 项目定位

这不是传统软件应用，而是一组可复用研究工作流：通过 Exa 高级搜索、网页检索和智能体分析，完成公司情报、竞争对手分析、外贸市场调研，以及长任务进度追踪。

核心目标：

- **跨智能体复用**：同一套技能可复制到 Codex、OpenClaw、Claude Code 或其他支持 `SKILL.md` 的代理环境。
- **研究可追溯**：输出报告要求保留来源、区分事实与推断、标注不确定性。
- **上下文节省**：搜索结果先提炼再综合，避免把大量原始网页噪声塞入主对话。
- **长任务可恢复**：通过 `feature_list.json` / `agent-progress.md` 等文件记录阶段成果。

## 目录结构

```text
.
├── skills/                         # Codex/OpenClaw 可移植技能
│   ├── company-research/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── foreign-trade-research/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── renewable-market-research/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── agents/openai.yaml
│   └── effective-harnesses/
│       ├── SKILL.md
│       └── agents/openai.yaml
├── .claude/skills/                 # 原 Claude Code 技能，保留兼容
├── research-output/                # 示例研究报告
├── feature_list.json               # 长任务/研究 feature 追踪示例
├── AGENTS.md                       # Codex/OpenClaw 读项目时的仓库级说明
└── CLAUDE.md                       # Claude Code 仓库级说明
```

## 技能列表

### `company-research`

用于公司情报、竞争对手分析、公司列表发现、市场格局速览。

适合请求：

- “研究一下 Tesla 的竞争对手”
- “帮我找到东南亚做仓储机器人的公司”
- “分析某公司的融资、营收、员工规模、新闻动态”

输出可为公司快照、竞争对手表格、市场简报或带来源的结构化 JSON。

### `foreign-trade-research`

用于“目标国家 + 产品/品类”的外贸市场深度调研，尤其适合中国出口商、制造商、跨境团队。

默认五步法：

1. 识别目标市场 TOP20 公司（品牌商 7 + 制造商 7 + 经销商/进口商 6）
2. 逐个拆解竞品背景、产品线、价格、渠道、客户、优劣势
3. 生成竞争对手对比矩阵与市场空白分析
4. 多源验证官网、电商、新闻、社交媒体、评论数据
5. 输出 5000-8000 字中文商务报告

### `renewable-market-research`

用于“任意国家 + 任意新能源技术”的深度市场情报采集，采用 effective-harnesses 风格的文件模式：多维度搜索写入 `data/renewable-market/depth/*.json`，主会话汇总为主 JSON、CSV、index，并输出完整版/交付版两套 MD/PDF 报告。

适合请求：

- “帮我调研乌兹别克斯坦风电市场，输出完整版和交付版报告”
- “调研沙特储能项目管道、融资和中国企业机会”
- “更新越南光伏市场数据，基于已有 JSON 做增量采集”

### `effective-harnesses`

用于长时间运行的开发或研究任务管理。

维护这些可恢复文件：

- `feature_list.json`：功能/研究任务清单、优先级、测试状态
- `agent-progress.md`：进度日志、决策、阻塞、下一步
- `init.sh`：可选启动脚本
- `CODING_STANDARDS.md`：可选项目规范

## 安装到 Codex

把需要的技能目录复制或软链接到 Codex 技能目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/company-research "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/foreign-trade-research "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/renewable-market-research "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/effective-harnesses "${CODEX_HOME:-$HOME/.codex}/skills/"
```

也可以在项目内保留 `skills/`，让支持项目级技能发现的 Codex 环境读取。

## 安装到 OpenClaw

把技能复制到 OpenClaw 的技能目录或工作区技能目录：

```bash
mkdir -p "$HOME/.openclaw/skills"
cp -R skills/company-research "$HOME/.openclaw/skills/"
cp -R skills/foreign-trade-research "$HOME/.openclaw/skills/"
cp -R skills/renewable-market-research "$HOME/.openclaw/skills/"
cp -R skills/effective-harnesses "$HOME/.openclaw/skills/"
```

如果你的 OpenClaw 使用工作区级技能目录，请把 `skills/<skill-name>` 复制到对应 workspace 的 `skills/` 下。

## 配置 Exa MCP

推荐配置 Exa MCP，以获得更好的公司、新闻、人物和网页搜索能力。若你已经配置并脱敏 Chrome-mcp，也可以把它作为真人浏览器 fallback，用于动态网页、PDF 下载、电商页面、地图/表格和人工核验。

### Claude Code 示例

```bash
claude mcp add --transport http exa https://mcp.exa.ai/mcp
```

### Codex / OpenClaw

在宿主工具中添加 Exa MCP server，URL 使用：

```text
https://mcp.exa.ai/mcp
```

不同宿主的 MCP 配置文件位置和命令可能不同；技能中不会硬编码 Claude 专属工具名，而是要求优先使用“当前环境可用的 Exa advanced search / web search MCP 工具”。

## Windows native 使用建议

如果在 Windows native 环境运行，不要假设有 Bash/WSL。优先使用 PowerShell 或 Python：

```powershell
New-Item -ItemType Directory -Force data/renewable-market/depth | Out-Null
py -3 -m json.tool feature_list.json > $env:TEMP\feature_list.validated.json
.\skills\renewable-market-research\scripts\export_projects_csv.ps1 -InputJson .\data\renewable-market\uzbekistan-wind.json -OutputCsv .\data\renewable-market\uzbekistan-wind.csv
```

需要启动项目时，优先提供 `init.ps1` 或 `init.py`；不要强依赖 `make.sh`、`chmod`、`sed/awk` 等 Bash/Unix 工具。

## 使用示例

```text
使用 $company-research 调研 Cursor、Windsurf、Continue 的竞品格局，输出表格并标注来源。
```

```text
使用 $foreign-trade-research 调研巴西太阳能逆变器市场，排除中国公司，输出中文市场进入报告。
```

```text
使用 $renewable-market-research 调研乌兹别克斯坦风电市场，采用文件模式采集，生成完整版和交付版报告。
```

```text
使用 $effective-harnesses 初始化这个研究项目，把任务拆成 6 个 feature 并创建 feature_list.json。
```

## 技能开发约定

- 可移植技能放在 `skills/<skill-name>/SKILL.md`。
- `SKILL.md` frontmatter 仅保留 `name` 和 `description`，提升 Codex/OpenClaw 兼容性。
- Codex UI 元数据放在 `agents/openai.yaml`。
- Claude Code 专属版本继续保留在 `.claude/skills/`，不要依赖它们实现跨平台兼容。
- 研究型技能应保持来源引用、置信度、事实/推断分离。


## 许可

本项目用于合法、授权的企业研究、市场分析、教育和自动化工作流实践。请遵守目标网站条款、数据隐私要求和所在地区法律法规。
