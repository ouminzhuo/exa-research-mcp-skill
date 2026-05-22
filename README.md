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

最可复用的一句话模板是：

```使用 effective-harnesses 管理任务状态，使用 renewable-market-research 文件模式执行研究，使用 company-research 支撑公司/竞品/合作方分析。采用多 agent 分工：worker 只写各自 depth JSON，主 agent 负责整合、判断、生成和校验。每条事实必须带来源、日期、语言、采集方式、置信度和不确定性。输出主 JSON、CSV、项目时间轴 CSV、完整版报告、交付版报告和 PDF，并用 uv run python 完成全量校验。```

## 使用建议

1. 先明确使用哪些 skill
你指定了：

effective-harnesses：管理长任务、进度、恢复点、测试状态。
renewable-market-research：主研究流程，负责文件模式、depth JSON、主 JSON、CSV、完整版/交付版、PDF。
company-research：补强业主、竞品、EPC、吊装公司、金融机构、合作伙伴分析。
关键点是你后来补了一句：“我在 skill 中也要求不同 agent 做不一样的内容，主 agent 做整合和思考。”
这句话让任务从“单 agent 研究”升级成了真正的多 agent 文件模式。

2. 再明确主 agent / worker 分工
你给的核心结构是：

主 Agent：初始化 harness、重写生成脚本、定义 schema、分派任务、整合 depth、生成 JSON/CSV/MD/PDF、做明阳机会判断。
Worker Agent：只负责自己的一组 depth/*.json，不改主 JSON、报告、PDF、生成脚本和 harness 文件。
这个分工非常关键，因为它避免了多个 agent 抢写同一个文件。

3. 明确 worker 文件所有权
你把任务拆成 A-H：

A：用电需求、电力缺口、电源结构
B/C：电网、消纳、储能、政策、PPA、电价
D/E/F：项目管线、业主、竞品、EPC、O&M
G/H：物流吊装、本地化、ESG、碳/绿氢、中国金融、区域对比
并且给每个 agent 指定了明确文件路径。这是本次最有效的部分。

4. 明确证据字段
你要求每条事实必须有：

url
title
publisher
accessedAt
sourceLanguage
collectionMethod
confidence
uncertainty
这让后续聚合、报告、校验都能自动化。

5. 明确验收命令
你指定：

uv run python scripts/build_kazakhstan_wind_outputs.py
uv run python -m json.tool data/renewable-market/index.json
uv run python -m json.tool data/renewable-market/kazakhstan-wind.json
以及全量 depth JSON 校验。这让任务有了“完成标准”，不是只靠主观感觉。

后续迭代 skill 时最需要注意：

在 skill 里写死 worker 输出 schema
这次出现了一个问题：不同 worker 写的 facts[] 有的直接是字符串，有的是 {claim, sources} 或 {statement, sources} 对象。虽然最后修好了，但 skill 应该明确规定统一格式，例如：
{
  "topic": "...",
  "facts": [
    {
      "statement": "...",
      "sources": [],
      "confidence": "...",
      "uncertainty": "..."
    }
  ]
}
明确“报告不能直接渲染 JSON 对象”
skill 里应加一条质量门：
Markdown / CSV / PDF 是人读文件，不允许出现 {"claim": ...}、{"sources": ...} 这种原始结构。
JSON/depth 才保留结构化证据。
项目管线必须单独有 timeline schema
这次你后来指出 COD 更重要，这是对的。skill 里建议固定加：
{
  "project": "...",
  "stage": "...",
  "auctionDate": "...",
  "ppaDate": "...",
  "fidDate": "...",
  "constructionStart": "...",
  "codOrTargetCod": "...",
  "timingConfidence": "...",
  "timingUncertainty": "..."
}
并输出单独的 project-timeline.csv。

多 agent 必须有“文件所有权规则”
推荐写进 skill：
worker 只能写自己的 depth 文件。
主 agent 只能整合，不手动改 worker 结论，除非做格式规范化。
worker 不生成报告，不改主 JSON，不改脚本。
主 agent 要有“归一化层”
因为不同 agent 输出风格一定会有差异，生成脚本必须内置：
normalize_sources
normalize_facts
humanize_value
dedupe_projects
project_timeline_records
这样 worker 写得稍微不一致也不会污染报告。

页数不应该是硬目标，信息完整性优先
这次经验是：详版 20-30 页更合理。skill 里可以写：
详版优先保证项目管线、时间、来源和判断完整，PDF 20-30 页可接受。
交付版控制在 4-6 页。
不通过删关键信息来满足页数。

## 技能开发约定

- 可移植技能放在 `skills/<skill-name>/SKILL.md`。
- `SKILL.md` frontmatter 仅保留 `name` 和 `description`，提升 Codex/OpenClaw 兼容性。
- Codex UI 元数据放在 `agents/openai.yaml`。
- Claude Code 专属版本继续保留在 `.claude/skills/`，不要依赖它们实现跨平台兼容。
- 研究型技能应保持来源引用、置信度、事实/推断分离。


## 许可

本项目用于合法、授权的企业研究、市场分析、教育和自动化工作流实践。请遵守目标网站条款、数据隐私要求和所在地区法律法规。
