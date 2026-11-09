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
   └─ NOTICE.md                     # 来源与许可
└─ scripts/
   └─ prd_md5.py                    # 门禁用的 PRD 版本 md5（只用 Python 标准库，跨平台）
Public-log/public-log.md            # 更新日志
```

## 安装

把 `_src/vibe-projectmanager/` 整个目录复制到 `~/.claude/skills/vibe-projectmanager/`，重开 Claude Code 会话即可。说「评审一下 PRD」「拆任务」「规划 Sprint」「写周报」等会触发。

依赖：
- 门禁算 md5 需要 Python 3（只用标准库）。
- PRD 在云文档上时，需要一个能把云文档导出成 Markdown 的工具。本 skill 不绑定具体工具，也不假定它装在哪里：会先看你在 CLAUDE.md 里写明的工具，没有就问你，也可以由你手动导出后交给它。
- 对 Lark / 飞书文档导出的固定文件头，`prd_md5.py --lark-export` 做了专门处理。

## 来源与许可

改编自三个 MIT 许可的开源技能：igmarin/agnostic-planning-skills、san-npm/skills-ws 的 project-management、AbsolutelySkilled 的 project-execution。逐项取舍、改动与许可原文见 [`_src/vibe-projectmanager/references/NOTICE.md`](_src/vibe-projectmanager/references/NOTICE.md)。
