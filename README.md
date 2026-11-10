# vibe-projectmanager

一个 Claude Code skill：把一条需求从成文 PRD 带到复盘，管的是**按顺序走**、**PRD 没过门禁不往下走**、**每段只用上一段留下的证据，不编**。

```
写 PRD → 评审 PRD → ⛔ 门禁（PRD 通过才放行）→ 拆任务 → 估算 → 识别风险 → 排优先级
      → 建工单 → 规划 Sprint → 状态汇报 → 复盘（行动项与实际完成量回流下一轮）
```

写 PRD 交给姊妹套件 [vibe-designing](https://github.com/AtlasDee/vibe-designing)，本 skill 从评审开始接手。

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

## 安装

两种方式任选：

- 下载根目录的 `vibe-projectmanager.skill`（zip 包，顶层目录为 `vibe-projectmanager/`），解压到 `~/.claude/skills/`；
- 或把 `_src/vibe-projectmanager/` 整个目录复制到 `~/.claude/skills/vibe-projectmanager/`。

`.skill` 包由 `_src/vibe-projectmanager/` 打包而成，两者内容一致。装好后重开 Claude Code 会话即可。说「评审一下 PRD」「拆任务」「规划 Sprint」「写周报」等会触发。

依赖：
- 门禁算 md5 需要 Python 3（只用标准库）。
- PRD 在云文档上时，需要一个能把云文档导出成 Markdown 的工具。本 skill 不绑定具体工具，也不假定它装在哪里：会先看你在 CLAUDE.md 里写明的工具，没有就问你，也可以由你手动导出后交给它。
- 对 Lark / 飞书文档导出的固定文件头，`prd_md5.py --lark-export` 做了专门处理。
- 排期脚本读 Markdown、CSV 或多维表格导出的 JSON，只用标准库。多维表格的数据可以在界面里导出 CSV，也可以用你约定的工具导出；脚本不读写云端。

## 来源与许可

改编自六个 MIT 许可的开源技能：igmarin/agnostic-planning-skills、san-npm/skills-ws 的 project-management、AbsolutelySkilled 的 project-execution、anotb/management-consulting-plugin 的 project-governance、mmoranodevelop/hard-half 的 portfolio-stage-gate 与 resource-collision、danielmiessler/LifeOS 的 RootCauseAnalysis。组合层另参考了 borghei/Claude-Skills（Commons Clause + MIT）的思路，未使用其代码；根因分析另参考了 lyndonkl/claude 的 postmortem（未附许可文件）的思路，未使用其模板、示例与评分表，五步的划分与其一致、个别短语与其相同。与这两个参考相近之处逐条列在 NOTICE。逐项取舍、改动与许可原文见 [`_src/vibe-projectmanager/references/NOTICE.md`](_src/vibe-projectmanager/references/NOTICE.md)。
