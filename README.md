# vibe-projectmanager

一个 Claude Code skill：把一条需求从成文 PRD 带到复盘，管的是**按顺序走**、**PRD 没过门禁不往下走**、**每段只用上一段留下的证据，不编**。

```
写 PRD → 评审 PRD → ⛔ 门禁（PRD 通过才放行）→ 拆任务 → 估算 → 识别风险 → 排优先级
      → 建工单 → 规划 Sprint → 状态汇报 → 复盘（行动项与实际完成量回流下一轮）
```

写 PRD 交给姊妹套件 [vibe-designing](https://github.com/AtlasDee/vibe-designing)，本 skill 从评审开始接手。

本仓库另有两个 skill：[vibe-chiefofstaff](#vibe-chiefofstaff幕僚长)（幕僚长）与 [vibe-assistant](#vibe-assistant助理)（助理），见文末。

## 主要设计

| 要点 | 说明 |
|---|---|
| 门禁 | 评审出结论、用户拍板才放行；放行时记下 PRD 的 md5，拆任务到排 Sprint 每段开工前重算比对，对不上就停下走变更评审 |
| 评审 | 两路独立评审（冷读子代理 + 主会话换问法），存疑与矛盾分开处理；首评 + 最多两次复评，再不过升级给用户 |
| 任务台账 | 拆任务、估算、排优先级、建工单、排 Sprint 共用一张表，逐段补列，是唯一真源 |
| RAID 日志 | 风险 / 假设 / 问题 / 依赖四类，每条有证据、具名负责人和复核日期；依赖写成约定，有升级触发条件 |
| Sprint 容量 | 按团队近 3～6 轮的完成区间，承诺取低端；没有历史时才用公式兜底并标明是推算 |
| 项目级工件 | 章程、干系人与沟通计划、决策日志（ADR）、变更请求（CR）、发布关卡，按需建立 |
| WBS 与排期表 | WBS 就是排期的父子树，字段沿用团队的多维表格排期模板；脚本按工时、依赖、工作日历和同一责任人排队推算日期，给出关键路径和甘特图；进度以多维表格为准，基线存本地快照；更新排期时回读比对：计划日期被改、逾期（先核实是否没回填）、里程碑偏差、数据质量 |
| 组合层 | 几条需求或项目同时在跑时：颜色只抄成员自报、没有证据标未知不标绿、不出组合平均色；资源冲突点名到人或技能并按重叠窗口算，解法限五种；跨项目风险看集中与同根；跨成员依赖由等待方登记；请求放在开头的组合汇报 |
| 阶段评审 | 到了里程碑判下一阶段要不要继续投入：继续 / 有条件继续 / 暂停 / 返工 / 停止；门槛在上一次评审时写好，继续必须给出人、钱和下次评审日期，否则算暂停 |
| 根因分析 | 事故、同一问题反复出现、再次跳黄时，从记准问题到落成改进：按问题的样子选方法（一条链用 5 个为什么，人、流程、工具多方面用鱼骨图，这里坏那里好用是与不是对比，几道防线同时失守用故障树），复杂的以无责复盘为框架；行动项按强度排，跟到完成、复查没复发才关；总是赶工、没时间测试这类症状，改的是截止日期、人手、考核这些约束，交拍板人决定 |
| 外部写操作 | 建工单、发汇报都要用户在当前这条消息里明确授权；线下动作列成用户待办，不写成已完成 |

## 目录

```
_src/vibe-projectmanager/
├─ SKILL.md                         # 总入口：链路、门禁铁律、产物目录、进入点、回流、共享约定
└─ references/
   ├─ prd-review-gate.md            # 第 2 段：评审与门禁
   ├─ breakdown-and-estimate.md     # 第 3、4 段：拆任务与估算
   ├─ risk-and-priority.md          # 第 5、6 段：RAID 日志、排优先级、关键路径
   ├─ tickets.md                    # 第 7 段：建工单
   ├─ sprint-status-retro.md        # 第 8～10 段：规划 Sprint、状态汇报、复盘
   ├─ governance.md                 # 项目级工件
   ├─ wbs-and-schedule.md           # 项目级工件：WBS 与排期表（新建、定基线、回读更新）
   ├─ portfolio.md                  # 组合层：多项目的风险、资源、依赖与汇总汇报
   ├─ root-cause.md                 # 项目级工件：根因分析与发布复盘
   └─ NOTICE.md                     # 来源与许可
└─ scripts/
   ├─ prd_md5.py                    # 门禁用的 PRD 版本 md5（只用 Python 标准库，跨平台）
   ├─ portfolio_rollup.py           # 组合汇总：读各成员 RAID 日志与资源分配表，只汇总不判断
   └─ schedule_calc.py              # 排期推算（plan）、回读检查（check）、基线快照（snapshot）
vibe-projectmanager.skill           # 安装包（由 _src/vibe-projectmanager/ 打包）
Public-log/public-log.md            # 更新日志
```

## vibe-chiefofstaff：幕僚长

管理者身边的两种幕僚合在一个 skill 里，管的是**该问谁就去问谁**、**分歧摆出来交给你拍板**、**定下来的事有人跟、到期有人提醒**。

| 路线 | 做什么 |
|---|---|
| 决策参谋 | 一个管理问题按复杂度派给 1～5 个模拟的高管角色（财务、技术、产品、营收、人力、法务等 14 个，可自定义），每个角色独立发言一轮、不来回争论；唱反调的角色挑毛病；幕僚长汇总共识、摆出分歧但不替你裁决，你拍板后才记进决策日志 |
| 运营幕僚 | 先问你用什么工具、团队多大、简报先看什么、决策记在哪，再做早间简报、会前准备、决策记录、周报汇总、看板指标更新 |

| 要点 | 说明 |
|---|---|
| 背景门槛 | 开会前先查目标、关键数字、硬约束、可选方案、拍板人；缺关键项先问（最多 3 问）。硬开的，置信度封顶为低，汇总首行写明缺什么。每条建议都要落在背景里的某个数字或约束上，换个公司名仍成立的建议删掉 |
| 独立发言 | 能起子代理就每个角色一个、并行跑、互相看不到；不能的顺序生成，并在汇总里注明独立性偏弱 |
| 两层存档 | 讨论记录与决策结论分开存；之后的讨论只读拍板过的结论，免得把当时没定的说法当成共识；否决的提议标不再提起，重开要你明说 |
| 不编 | 截止日、负责人拿不到写待定，不自动填默认值；简报、周报、看板里的计数由 `scripts/decision_scan.py` 算 |
| 外部写操作 | 只读你的工具；发消息、写云文档、建日程都要你当次明确同意；定时运行由你在自己的环境里设 |
| 与 vibe-projectmanager | 项目内的决定记进那个项目的 ADR，这里只留指针；动到已放行 PRD 或里程碑的先走那边的变更请求 |

```
_src/vibe-chiefofstaff/
├─ SKILL.md                         # 总入口：两条路线、进入点、产物目录、参谋会铁律、衔接、共享约定
├─ references/
│  ├─ council.md                    # 参谋会：背景门槛、打分路由、发言、唱反调、汇总、拍板、存档
│  ├─ roles.md                      # 角色登记、话题路由、议题组合、自定义角色
│  ├─ background.md                 # 背景档案：七维访谈、保鲜与补充、模板
│  ├─ decision-log.md               # 决策日志：两层、决策文件、冲突检查、查询与复核、与项目 ADR 的分工
│  ├─ operations.md                 # 运营幕僚：设置向导、早间简报、会前准备、周报、看板
│  └─ NOTICE.md                     # 来源与许可
└─ scripts/
   └─ decision_scan.py              # 决策扫描：逾期、即将到期、复核到期、待定、不再提起、索引核对（只读、只用标准库）
vibe-chiefofstaff.skill             # 安装包
```

## vibe-assistant：助理

管理者身边的执行助理，管的是**说定的事落成有人负责、有日期的行动项**、**没定的事不混进定了的事**、**发出去之前先给你看**。日常读写通过 larkbot 对接 Lark / 飞书。

| 件事 | 做什么 |
|---|---|
| 会议纪要 | 固定格式，决定和行动项放最前；每个行动项一个负责人、一个截止日期，交付物类写验收标准；没解决的问题单独放进待议区；高度机密或敏感的人事会议不记 |
| 通话与逐字稿 | 从妙记、云文档或粘贴的逐字稿里提取决定、双方承诺和行动项，起草对外跟进消息和对内摘要，提出要更新的记录，你逐条确认后才写 |
| 每日晨报 | 今天的日程（含冲突与要准备的会）、到期和逾期的行动项、等你回的邮件 |
| 会前准备 | 参会人、日程描述与附带文档、上次同系列会的纪要、待议区和没做完的行动项 |
| 收件箱分拣与排日程 | 邮件分成要你亲自回、可代拟、知会、可归档，可疑的单列；约会先查空闲、给时段，你选定后才建 |

| 要点 | 说明 |
|---|---|
| 先确认再定稿 | 纪要、跟进消息、日程、记录更新都先给草稿；发消息、建日程、写云文档或多维表格要你当次明确同意，写后回读核对 |
| 不替人认领 | 会上没说定负责人或日期的写待定，定稿前补不上就移进待议区，不填默认值 |
| 材料不是指令 | 逐字稿、邮件、消息里要求发文件、改字段、加收件人的，单列待你决定，不照做 |
| 行动项台账 | 纪要和通话里的行动项登记进一张台账，状态只在这里改；`scripts/action_items.py` 检查纪要格式、扫描逾期与未登记（只读、只用标准库） |
| Lark 接入 | 按你在 CLAUDE.md 登记的 larkbot 调用（MCP 工具或 Python 库），不写死路径；读不了历史消息、发不了邮件这类缺口改为粘贴兜底 |
| 与幕僚长、vibe-projectmanager | 幕僚长的早间简报读助理的晨报再叠加决定跟进，会前准备交给助理；管理层的决定经同意后记进幕僚长的决策日志，项目内的决定提示记进那个项目的 ADR |

```
_src/vibe-assistant/
├─ SKILL.md                         # 总入口：五件事、进入点、产物目录、助理铁律、衔接、共享约定、自检
├─ references/
│  ├─ minutes.md                    # 会议纪要：能不能用、受理、格式、行动项与台账、待议区、审阅与分发
│  ├─ call-followup.md              # 通话与逐字稿：取记录、抽结构、对外跟进、对内摘要、记录更新
│  ├─ daily.md                      # 每日晨报、会前准备、收件箱分拣、排日程、定时运行
│  ├─ lark.md                       # Lark 接入：找 larkbot、设定、能力表、读写要点、缺口与兜底
│  └─ NOTICE.md                     # 来源与许可
└─ scripts/
   └─ action_items.py               # 纪要检查（check）与行动项扫描（scan）
vibe-assistant.skill                # 安装包
```

改编自 github/awesome-copilot 的 meeting-minutes（MIT）、anthropics/knowledge-work-plugins 的 call-summary（Apache-2.0）、googleworkspace/cli 的 persona-exec-assistant（Apache-2.0）；原版绑定的 Google Workspace、Gong 与 CRM 换成 Lark。逐项取舍见 [`_src/vibe-assistant/references/NOTICE.md`](_src/vibe-assistant/references/NOTICE.md)。

改编自两个 MIT 许可的来源：alirezarezvani/claude-skills 的 c-level-advisor 一组（chief-of-staff、board-meeting、decision-logger、context-engine、cs-onboard、agent-protocol），Ability.ai 的 abilities 中已退役的 install-chiefofstaff 向导。逐项取舍见 [`_src/vibe-chiefofstaff/references/NOTICE.md`](_src/vibe-chiefofstaff/references/NOTICE.md)。

## 安装

三个 skill 装法相同，以 vibe-projectmanager 为例（vibe-chiefofstaff、vibe-assistant 把名字换掉即可）。两种方式任选：

- 下载根目录的 `vibe-projectmanager.skill`（zip 包，顶层目录为 `vibe-projectmanager/`），解压到 `~/.claude/skills/`；
- 或把 `_src/vibe-projectmanager/` 整个目录复制到 `~/.claude/skills/vibe-projectmanager/`。

`.skill` 包由 `_src/vibe-projectmanager/` 打包而成，两者内容一致。装好后重开 Claude Code 会话即可。说「评审一下 PRD」「拆任务」「规划 Sprint」「写周报」等会触发。

vibe-chiefofstaff 说「帮我从几个角度想想这件事」「开个高管会」「记个决策」「早间简报」「帮我准备这个会」「周报汇总」等会触发。它的产物放在工作目录的 `幕僚/` 下，含公司数字和人名，放进 git 仓库前先加进 `.gitignore`。

vibe-assistant 说「整理会议纪要」「总结这通电话」「起草跟进消息」「每日晨会」「帮我准备下一个会」「看看收件箱」「帮我约个会」等会触发。它的产物放在工作目录的 `助理/` 下，含人名、会议内容和邮件摘要，放进 git 仓库前先加进 `.gitignore`。

依赖：
- 决策扫描脚本、行动项脚本需要 Python 3（只用标准库）。
- vibe-assistant 读写 Lark 需要 larkbot（Lark 开放平台的 Python 封装，带 MCP 服务），以用户身份登录；没有时各项改为手动粘贴，写操作给可粘贴文本。
- 门禁算 md5 需要 Python 3（只用标准库）。
- PRD 在云文档上时，需要一个能把云文档导出成 Markdown 的工具。本 skill 不绑定具体工具，也不假定它装在哪里：会先看你在 CLAUDE.md 里写明的工具，没有就问你，也可以由你手动导出后交给它。
- 对 Lark / 飞书文档导出的固定文件头，`prd_md5.py --lark-export` 做了专门处理。
- 排期脚本读 Markdown、CSV 或多维表格导出的 JSON，只用标准库。多维表格的数据可以在界面里导出 CSV，也可以用你约定的工具导出；脚本不读写云端。

## 来源与许可

改编自六个 MIT 许可的开源技能：igmarin/agnostic-planning-skills、san-npm/skills-ws 的 project-management、AbsolutelySkilled 的 project-execution、anotb/management-consulting-plugin 的 project-governance、mmoranodevelop/hard-half 的 portfolio-stage-gate 与 resource-collision、danielmiessler/LifeOS 的 RootCauseAnalysis。组合层另参考了 borghei/Claude-Skills（Commons Clause + MIT）的思路，未使用其代码；根因分析另参考了 lyndonkl/claude 的 postmortem（未附许可文件）的思路，未使用其模板、示例与评分表，五步的划分与其一致、个别短语与其相同。与这两个参考相近之处逐条列在 NOTICE。逐项取舍、改动与许可原文见 [`_src/vibe-projectmanager/references/NOTICE.md`](_src/vibe-projectmanager/references/NOTICE.md)。
