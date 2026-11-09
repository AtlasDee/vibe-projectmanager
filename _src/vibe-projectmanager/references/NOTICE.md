# 来源与许可

本 skill 译写、改编自以下三个开源技能，均为 MIT 许可：

| # | 来源 | 版本 / 取得方式 | 版权 |
|---|---|---|---|
| 1 | **igmarin/agnostic-planning-skills** · https://github.com/igmarin/agnostic-planning-skills | v5.1.0 | Copyright (c) 2026 Ismael G Marin Cabrera |
| 2 | **san-npm/skills-ws** 的 `skills/project-management/SKILL.md` · https://github.com/san-npm/skills-ws | npm 包 skills-ws 1.12.0 对应的 main 分支 | Copyright (c) 2025 Commit Media SARL |
| 3 | **AbsolutelySkilled** 的 `project-execution`（v0.1.0，维护者 maddhruv）· 原仓库现为 https://github.com/dhruvjainin/absolute | 该目录在 2026-06-05 的提交 `1ad2c4b`（cleanup & introduce AbsoluteWork）中被删除，取自其父提交 `2f13162` 的 `skills/project-execution/`：SKILL.md 与 3 份 references（risk-management、dependency-tracking、stakeholder-communication）；NeverSight/learn-skills.dev 的镜像缺 SKILL.md 的常见坑一节 | Copyright (c) 2026 AbsolutelySkilled（取自父提交 `2f13162` 的 LICENSE；原仓库现行 LICENSE 的版权行为 Absolute） |

## 取用与改动：来源 1

| 上游 skill | 去向 | 主要改动 |
|---|---|---|
| `create-prd` | 不取 | 写 PRD 交给 vibe-designing 套件（团队模板），不另设 PRD 模板 |
| `requirements-clarifier` | 不取 | 由 vibe-designing 的访谈与体检分件覆盖 |
| `review-prd` | `prd-review-gate.md` | 清单改成可回答的是非问题，并按团队 PRD 结构补问；严重度改为阻塞项 / 小问题 / 备注，🔵 按是否卡主流程分级；结论改为通过 / 不通过 / 升级；删去「明确写出不做的范围」一项，因团队规范 PRD 正文不写不做什么；保留证据脱敏 |
| `judgment-gate` | `prd-review-gate.md`、SKILL.md 第 2 节 | 取冻结目标、窄问题、独立评审、每问给判断与置信度、不接受半份评审、存疑与矛盾的处理、两轮修改上限后升级、人来拍板；冻结版本加 md5 并在下游开工前比对；加没有子代理时的兜底做法 |
| `plan-tickets` | `breakdown-and-estimate.md`、`tickets.md` | 取「可独立验证再拆」「只出草稿」「不编团队政策」与建单就绪检查；加 PRD 出处与任务台账 |
| `estimate-tasks` | `breakdown-and-estimate.md` | 取三种框架、置信度、需拆分与 spike、不给占位值；加依赖 🔵 时置信度上限 |
| `identify-risks` | `risk-and-priority.md` | 取六类模式、概率 / 影响 / 临近度三维判断、证据与缓解；加门禁遗留项作为输入、状态列 |
| `prioritize-backlog` | `risk-and-priority.md` | 取四种框架、强制全序、写理由；加依赖压过得分、风险前置 |
| `github-issue` | `tickets.md` | 改为不绑定工单系统的写法，保留「只在明确授权时写」「不假设字段与凭证」；上游自带的标签规范不取，改为仓库已有规范才打标签 |
| `plan-sprint` | `sprint-status-retro.md` | 取单一目标、速率下滑时以最近一轮为准；「承诺 ≤ 80%」与人天容量公式在加入来源 2 后改为：有历史数据按历史区间，无历史数据时才用公式 × 0.6 作基线，并注明公式得到的是工时（见下方来源 2） |
| `generate-status-report` | `sprint-status-retro.md` | 取不编进度、不藏阻塞；模板与来源 2、3 合并 |
| `create-retrospective` | `sprint-status-retro.md` | 取不编反馈、每条没做好对应行动项、模板；加计划对实际与回流 |
| `work-router` | SKILL.md 第 4 节 | 改为按「用户手上有什么」决定从哪一段进入，并检查该段输入 |
| `task-complexity-classifier` | 不取 | 依赖外部付费接口 |
| `llm-judgment-layer` | 不取 | 面向应用内的模型集成，与本链路无关 |

## 取用与改动：来源 2（skills-ws project-management）

| 内容 | 去向 | 改动 |
|---|---|---|
| 按历史区间规划 Sprint（吞吐量、按已知变化调整、显式缓冲、承诺取区间低端） | `sprint-status-retro.md` 1.2 | 与来源 1 的冲突按本节处理：历史数据优先，公式只在没有历史时兜底并标 🔶；缓冲与取低端原文是叠加的，改为按历史数据是否已含计划外工作二选一 |
| 准入标准 DoR、完成标准 DoD、验收标准质量要求 | `sprint-status-retro.md` 1.3、`governance.md` 第 5 节、`breakdown-and-estimate.md` | DoR 加「来自已放行 PRD」一条 |
| 三点估算、估算分歧处理 | `breakdown-and-estimate.md` 第 2 节 | — |
| 看板：WIP 上限、周期时间、在制时长、吞吐量预测 | `sprint-status-retro.md` 1.4 | 压缩为看板团队的替代做法 |
| 状态更新模板（先结论、写结果、求助写成动作、不在截止日第一次变红） | `sprint-status-retro.md` 第 2 节 | 与来源 3 的模板合并 |
| RAID 日志、概率×影响矩阵、触发条件、假设要尽早验证 | `risk-and-priority.md` 第 1 节 | 原「风险登记」升级为 RAID 日志，保留来源 1 的六类模式与证据要求 |
| 依赖约定 | `risk-and-priority.md` 1.3 | 与来源 3 的「未确认依赖」合并 |
| 章程与启动清单、RACI、沟通计划、DACI 与 ADR、变更请求、发布就绪清单、OKR | `governance.md` | 章程的「Out（明确不做）」一栏不取：与团队「只写要做什么」的规范保持一致，需求级排除项按 vibe-designing 写进 PRD 备注文档，难撤回的范围取舍才记 ADR；没有发起人时批准人默认为用户 |
| 无责复盘与 5 个为什么、复盘行动项 ≤ 3、先看上轮行动项 | `sprint-status-retro.md` 第 3 节 | — |
| 反模式（速率当绩效、只有产出的 OKR、没有唯一负责人、悄悄扩范围等） | SKILL.md 第 6 节、各规程 | 化入规则，不单列表 |
| 工具选型（Linear / Jira / GitHub Projects / Asana / Notion）与价格提示 | 不取 | 时效性强，且工单系统由用户指定 |
| 受监管行业、远程团队的调整 | `governance.md` 第 2、6 节各一句 | — |

## 取用与改动：来源 3（project-execution）

| 内容 | 去向 | 改动 |
|---|---|---|
| RAID 定义、3×3 风险矩阵、每周复核 | `risk-and-priority.md` 第 1 节 | 与来源 2 合并 |
| 事前验尸 | `risk-and-priority.md` 1.1 | 由 AI 模拟的条目一律标 🔶，等团队确认 |
| 依赖五要素、未确认依赖按最高风险处理、经发起人和对方上级升级 | `risk-and-priority.md` 1.3 | 未确认依赖同时登记一条风险：概率记高，影响按强度和是否在关键路径照实判；加需要日期以便倒推升级时间 |
| 关键路径、浮动时间、快速跟进与赶工 | `risk-and-priority.md` 2.2 | 压缩工期只列选项和代价，由用户决定 |
| RAG 定义且在开工时约定口径 | `sprint-status-retro.md` 2.1、`governance.md` 第 1 节 | — |
| 干系人地图与沟通节奏 | `governance.md` 第 2 节 | 发起人同步频率两源冲突（来源 2 每两周，来源 3 每周），取每周，与坏消息早说一致 |
| SKILL 正文的反模式表（风险只在开工时登记、依赖一视同仁、一直绿突然红、不带选项升级、悄悄扩范围、依赖只有一个联系人） | `risk-and-priority.md` 第 1 节与 1.3，`sprint-status-retro.md` 2.1、2.5，SKILL.md 第 6 节「范围是第一个调节杆」 | 化入对应规则，不单列；依赖一视同仁一条落为按强度和关键路径分轻重，未确认依赖的影响照实判 |
| 升级五段式、先私下通气 | `sprint-status-retro.md` 2.5 | 私下通气等线下动作改为列给用户的待办 |
| 里程碑 Go / 有条件 Go / No-Go | `governance.md` 第 6 节 | 与来源 2 的发布就绪清单合并 |
| 「范围是第一个调节杆」「坏消息早说」 | SKILL.md 第 6 节 | — |
| 常见坑（依赖只是假定为已确认、为回避难谈的话把黄报成绿、不带选项升级、跳过事前验尸、关卡走过场） | `risk-and-priority.md` 1.1、1.3，`sprint-status-retro.md` 2.1、2.5，`governance.md` 第 6 节 | 化入对应规则，不单列 |
| `risk-management`：事前验尸各自独立写、假设盘点、往期复盘与按项目类型的常见风险 | `risk-and-priority.md` 1.1 | 上游四种识别技术中的依赖风险扫描，由来源 1 的六类模式顶替其位置，内容挪到 1.3 改称延误推演，范围从外部依赖扩大到每条依赖；假设盘点把大概率一档也登记进假设表（上游只把不确定、未验证两档列为风险候选），以便到期验证；常见风险只作提示，要落到本项目证据才登记 |
| `risk-management`：3×3 矩阵与按等级的处理和复核频率、按阶段的复核节奏 | `risk-and-priority.md` 第 1 节开头、1.2 | 矩阵与来源 2 的定性表结果一致，保留定性表；低级的每季度复核去掉，只在里程碑时看；按阶段的节奏压缩为收尾冲刺期整份日志每周两遍；复核分每周过一遍和逐条细看两层，假设、问题、依赖另给复核口径；未确认依赖带来的严重风险，升级时点按依赖的触发条件 |
| `risk-management`：期望延误 = 概率 × 影响天数 | `risk-and-priority.md` 2.2 | 概率换算比例由用户给出，标 🔶，按共享约定不编的例外处理 |
| `risk-management`：规避 / 转移 / 减轻 / 接受；登记册维护规则 | `risk-and-priority.md` 1.4 | 接受须写明决定与应急预案的触发条件；关闭条目保留并写原因；讨论到就更新复核日期，指的是更新四张表新增的上次复核列（上游的最近复核日），不顺延下次复核 |
| `risk-management`：缓冲策略（中等以上风险的任务加 20%，高风险且有外部依赖的加 40%） | 不取 | 与来源 2 反对固定百分比的立场冲突；三点估算与 Sprint 缓冲已覆盖不确定性，再按任务加会重复计算 |
| `dependency-tracking`：硬 / 软 / 外部 / 内部依赖、依赖模板（主备联系人、确认日期、状态）、依赖握手、每周三问、升级触发条件、依赖健康度、受阻处理、反模式 | `risk-and-priority.md` 1.3、1.4 | 依赖表加强度、备用联系人、浮动、上次复核四列：上游的 Buffer 取为浮动列，定义为需要日期减承诺日期；Last checked 取为上次复核列，并记每周三问的要点。状态加进行中、延误、受阻（上游的 Blocked），上游的 DONE 取为健康度 ✅，并给出状态与颜色的对应；对外沟通改为用户待办；触发条件作默认值，可在章程改 |
| `dependency-tracking`：文本依赖链图示 | 不取 | `risk-and-priority.md` 第 2.2 节的关键路径已覆盖 |
| `stakeholder-communication`：RAG 加完成、转色时限、不跳黄 | `sprint-status-retro.md` 2.1 | 不跳黄改为照实报红并说明预警为何失灵，不为好看先报黄；🟡 的定义放宽为应对措施已有或在 48 小时内给出，与转色时限对齐；汇报的风险与阻塞表补了按等级、严重度和健康度上色的口径 |
| `stakeholder-communication`：周报模板 | 不取 | 与来源 2 的模板合并后已覆盖 |
| `stakeholder-communication`：升级模板、里程碑完成通报 | `sprint-status-retro.md` 2.2、2.3、2.5 | 升级的影响按进度、成本、质量量化；里程碑通报并入状态汇报的进展一节，不另设产物 |
| `stakeholder-communication`：干系人档案、按阶段的沟通节奏、难谈的话（报坏消息、谈范围变更、处理分歧） | `governance.md` 第 2 节 | 只起草要点，谈话列为用户待办；范围变更落到变更请求，分歧结论落到决策日志 |
| `evals.json`（14 条评测场景） | 不取 | 本 skill 不带评测文件；留作日后实跑金标准的参考 |
| 「激活后首条回复以 🧢 开头」「检查并推荐安装配套 skill」 | 不取 | 来源自身的品牌与推广指令，与本 skill 无关 |

上游各文件为英文，本 skill 全部改写为中文，未逐字照搬。

## MIT License（上游原文）

三个来源使用同一份 MIT 许可正文，版权行分别为：

- Copyright (c) 2026 Ismael G Marin Cabrera（来源 1）
- Copyright (c) 2025 Commit Media SARL（来源 2）
- Copyright (c) 2026 AbsolutelySkilled（来源 3）

```
MIT License

Copyright (c) <见上方各来源的版权行>

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
