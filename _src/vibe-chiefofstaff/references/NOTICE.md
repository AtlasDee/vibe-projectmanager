# 来源与许可

本 skill 译写、改编自以下两个开源来源，均为 MIT 许可：

| # | 来源 | 版本 / 取得方式 | 版权 |
|---|---|---|---|
| 1 | **alirezarezvani/claude-skills** 的 `c-level-advisor/skills/` · https://github.com/alirezarezvani/claude-skills | 提交 `91a1dda`（2026-11-10）：chief-of-staff（SKILL.md、routing-matrix、synthesis-framework）、board-meeting、decision-logger（SKILL.md 与 decision-entry 模板）、context-engine、cs-onboard、agent-protocol 的相关小节；各 SKILL.md 标 1.0.0 | Copyright (c) 2025 Alireza Rezvani |
| 2 | **Ability.ai 的 abilityai/abilities** 中 `plugins/create-agent/skills/chief-of-staff`（向导名 install-chiefofstaff，1.10）· https://github.com/abilityai/abilities | 该向导在 create-agent 2.0.0（提交 `f84bbce`）中退役，取自其父提交 `7090c8b` 的 SKILL.md | Copyright (c) 2026 Ability.ai |

另：据称 borghei/Claude-Skills 里有同一架构的幕僚长，本 skill 未参考其内容。

## 取用与改动：来源 1（决策参谋）

| 上游内容 | 去向 | 改动 |
|---|---|---|
| chief-of-staff 的会话流程（读背景 → 打分 → 路由 → 汇总 → 记决定） | `council.md` 第 0～2 节 | 在打分前加**背景门槛**（目标、关键数字、硬约束、可选方案、拍板人五项三档），缺关键项先问、最多 3 问；照开时置信度封顶为低、汇总首行写明缺口。上游只有「缺数据时按阶段和人数推断、标注缺口」，正是用户指出的空泛来源 |
| 复杂度打分（1～5，五个加分项）、何时多叫角色、何时不要 | `council.md` 第 2 节 | 原文 |
| 路由矩阵（14 个领域 80 余条问题）与角色登记 | `roles.md` 第 2、3 节 | 压成一张话题表；每个角色补「开口前要的数」一列，作为背景门槛的问题来源 |
| 15 个角色 | `roles.md` 第 2 节 | 保留 14 个发言角色 + 高管教练（唱反调）；加自定义角色，适配非创业公司的团队 |
| 各角色的推理方式（思维树、写出算式等） | `roles.md` 第 2 节（看问题的方法一列） | 改写成一句可执行的做法，不用方法名 |
| 调用语法 `[INVOKE:role\|question]`、防循环四条 | SKILL.md 第 4 节第 2 条 | 只保留「角色之间不互相调用、只有一层」；语法不取 |
| board-meeting 六阶段（背景 → 独立发言 → 唱反调 → 汇总 → 用户审阅 → 提取决定） | `council.md` 第 3～8 节 | 独立发言改为：能起子代理就每角色一个并行，不能就顺序生成并在汇总标「独立性偏弱」；上游没有这条兜底 |
| 议题与上场角色表 | `roles.md` 第 4 节 | 原文翻译 |
| 发言格式（最多 5 点、已核实 / 假设、置信度、来源、什么会让我改主意） | `council.md` 第 4 节 | 每条要点加【依据】，指到背景档案的具体数字；加「出了自己的领域」 |
| 唱反调清单 | `council.md` 第 5 节 | 加一条：哪条建议换了公司名也成立 |
| 汇总框架（三条共识、四类冲突、五条行动、一个拍板问题、僵局处理、常见失败） | `council.md` 第 6 节 | 原文为主；行动项的负责人和期限拿不到写待定，不编 |
| 推荐与否 | SKILL.md 第 4 节第 4 条、`council.md` 第 6 节 | 上游自相矛盾：synthesis-framework 写「不给推荐」，chief-of-staff 质量清单和 board-meeting 第 4 阶段写「给推荐的决定」。按用户要的「摆分歧、不裁决」取前者；用户要推荐时单列为幕僚长的倾向 |
| 用户审阅（批准 / 修改 / 否决 / 追问，用户改动直接覆盖、不反驳） | `council.md` 第 7 节 | 30 分钟无响应自动关闭不取（对话里无法计时），改为记为待拍板、下次简报提醒 |
| 两层决策记忆（讨论记录不自动读、只读已拍板的） | `decision-log.md` 第 1 节 | 存放位置从 `~/.claude/decisions/` 改到工作目录的 `幕僚/决策/`，便于按项目分开、随项目备份；第一层 90 天归档改为先问用户 |
| 决策条目字段与字段规则、不再提起（DO_NOT_RESURFACE）、取代 | `decision-log.md` 第 2、4 节 | 改为表格字段，便于脚本读；**截止日拿不到时上游默认填 14 天，这里改为写待定**（与「不编」一致）；加「项目指针」 |
| 写入前冲突检查（不再提起、同主题矛盾、负责人冲突） | `decision-log.md` 第 5 节 | 原文；脚本只列清单，同一件事与否由人判断 |
| decision_tracker.py（汇总、逾期、冲突、按负责人筛选、搜索） | `scripts/decision_scan.py` | 重写，未使用上游代码：读本 skill 的表格格式，输出逾期、即将到期、复核到期、待定、本周新增与完成、不再提起清单、索引核对、读不准；不做关键词冲突检测（误报多，改由人读） |
| 开场检查复核日已过的决定 | `council.md` 第 0 节、`operations.md` 第 2 节 | 由脚本算出，简报里提一句，不自行复核 |
| context-engine：背景档案、90 天过期、可信度分级、对话中补充先问再写、隐私与去标识 | `background.md` 第 3 节、SKILL.md 第 6 节「隐私」 | 补充时旧值留痕；去标识规则压成一条 |
| cs-onboard：七维访谈、关键追问、红旗、季度更新 | `background.md` 第 1、2、4 节 | 维度与追问翻译改写；加「最少几项」的当场建档做法；模板加关键数字表 |
| agent-protocol 的统一输出格式（结论先行、每节最多 5 条） | SKILL.md 第 6 节「结论先行」 | 只取原则，不取分隔线与表情符号版式 |
| 主动提醒格式、广播模式、同行互验 | 不取 | 与本 skill 的两条路线关系不大；同行互验与唱反调重复 |
| 各角色自己的技能（ceo-advisor 等）与其余横向技能（董事会材料、情景推演、竞品、并购等） | 不取 | 角色只取路由矩阵与 board-meeting 里的定义；本 skill 只做幕僚长的编排，需要某个角色的深度时可单独装原技能 |

## 取用与改动：来源 2（运营幕僚）

| 上游内容 | 去向 | 改动 |
|---|---|---|
| 向导的四个问题（工具、团队规模、简报优先、决策记在哪）及每个答案影响哪些产物 | `operations.md` 第 1 节 | 工具选项改为通用的几类（办公套件、即时消息、文档、工单，或手动贴），不绑定具体产品；只登记读取方式，不登记凭证 |
| 早间简报（取数步骤、按团队规模调深度、优先项放最前、读决策日志、存档） | `operations.md` 第 2 节 | 读不到的写待更新；装了 vibe-projectmanager 的读现成的汇报和 RAID，健康度照抄；计数改由脚本算 |
| 会前准备（参会人、背景、悬着的事、对方可能想谈的、建议提的、要定的） | `operations.md` 第 3 节 | 搜外部对象只看公开职务与公司信息、搜索词不带我方内部信息；要当场定大事时提示先开参谋会；会后提醒记决定 |
| track-decision（问决定、问跟进、按目标格式输出、查逾期） | `decision-log.md` 第 3 节 | 与来源 1 的决策日志合并成一个；外部格式只生成可粘贴的文字，写到外部要当次授权；本地文件始终是唯一真源 |
| 周报汇总（本周决定、跟进统计、主线、下周预览、建议） | `operations.md` 第 4 节 | 不补写本周没记的决定 |
| update-dashboard（从决策、简报、会前文件算指标） | `operations.md` 第 5 节 | 加用户指定的业务指标；每个数写来源和截至时间，取不到不沿用旧值 |
| 推荐的定时（工作日早 7 点简报、周五下午周报） | `operations.md` 第 1 节（末段定时） | 改为提示用户在自己的环境里设置、同意后才建；本 skill 不自行建定时 |
| 「像一流的幕僚长一样：有主见、能等的说能等」 | `operations.md` 开头 | 限定为注意力的先后，决定本身仍由用户拍板 |
| 搭建独立的智能体目录、CLAUDE.md、请求分派表、Trinity 部署与报告、template.yaml、dashboard.yaml、onboarding.json、.env 模板、git 初始化、建 GitHub 仓库 | 不取 | 本 skill 是装在现有 Claude Code 里的一个 skill，不另建智能体；部署平台相关的内容与此无关 |

## 本 skill 新增

- 背景门槛（`council.md` 第 1 节）与「换了公司名仍成立的建议删掉」的检验
- 子代理不可用时的独立性兜底与标注
- 角色是模拟视角、真人意见替代模拟角色的规则
- 两条路线共用一个背景档案与一个决策日志，以及两者之间的衔接（SKILL.md 第 5 节）
- 与 vibe-projectmanager 的分工（`decision-log.md` 第 7 节）
- `scripts/decision_scan.py`

## MIT 许可原文

### 来源 1

```
MIT License

Copyright (c) 2025 Alireza Rezvani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 来源 2

```
MIT License

Copyright (c) 2026 Ability.ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
