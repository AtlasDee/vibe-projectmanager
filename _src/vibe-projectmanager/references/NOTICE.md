# 来源与许可

本 skill 译写、改编自以下六个开源技能，均为 MIT 许可：

| # | 来源 | 版本 / 取得方式 | 版权 |
|---|---|---|---|
| 1 | **igmarin/agnostic-planning-skills** · https://github.com/igmarin/agnostic-planning-skills | v5.1.0 | Copyright (c) 2026 Ismael G Marin Cabrera |
| 2 | **san-npm/skills-ws** 的 `skills/project-management/SKILL.md` · https://github.com/san-npm/skills-ws | npm 包 skills-ws 1.12.0 对应的 main 分支 | Copyright (c) 2025 Commit Media SARL |
| 3 | **AbsolutelySkilled** 的 `project-execution`（v0.1.0，维护者 maddhruv）· 原仓库现为 https://github.com/dhruvjainin/absolute | 该目录在 2026-06-05 的提交 `1ad2c4b`（cleanup & introduce AbsoluteWork）中被删除，取自其父提交 `2f13162` 的 `skills/project-execution/`：SKILL.md 与 3 份 references（risk-management、dependency-tracking、stakeholder-communication）；NeverSight/learn-skills.dev 的镜像缺 SKILL.md 的常见坑一节 | Copyright (c) 2026 AbsolutelySkilled（取自父提交 `2f13162` 的 LICENSE；原仓库现行 LICENSE 的版权行为 Absolute） |
| 4 | **anotb/management-consulting-plugin** 的 `skills/project-governance`（v2.3.1）· https://github.com/anotb/management-consulting-plugin | 提交 `1489e7e`：SKILL.md 与 `references/risk-and-reporting.md` | Copyright (c) 2026 Anot |
| 5 | **mmoranodevelop/hard-half** 的 `skills/management/portfolio-stage-gate` 与 `skills/delivery/resource-collision` · https://github.com/mmoranodevelop/hard-half | 提交 `1228fe2`：两份 SKILL.md 与 stage-gate 的 3 份模板 | Copyright (c) 2026 Manuel Morano |
| 6 | **danielmiessler/LifeOS** 的 `LifeOS/install/skills/RootCauseAnalysis`（v1.1.1）· https://github.com/danielmiessler/LifeOS | 提交 `f6ab5e0`：SKILL.md、MethodSelection.md、Foundation.md 与 5 份 Intents（FiveWhys、Fishbone、KepnerTregoe、FaultTree、Postmortem） | Copyright (c) 2025-2026 Daniel Miessler |

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
| 复盘行动项 ≤ 3、先看上轮行动项 | `sprint-status-retro.md` 第 3 节 | — |
| 无责复盘与 5 个为什么 | 先在 `sprint-status-retro.md` 第 3 节，(16) 起并入 `root-cause.md` | 与来源 6 合并，见下方来源 6 |
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
| 发布 Go / 有条件 Go / No-Go | `governance.md` 第 6 节 | 与来源 2 的发布就绪清单合并；里程碑上要不要继续投入，改由第 7 节阶段评审管（来源 4、5） |
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

## 取用与改动：来源 4（project-governance）

| 内容 | 去向 | 改动 |
|---|---|---|
| 没有证据标未知、不把缺信息当成绿；颜色附定义与趋势 | `sprint-status-retro.md` 2.1、`portfolio.md` 第 1 节 | 加 ⚪ 未知；连续两期未知本身记为风险 |
| 基线、当前预测、已批准变更分开；进度按已交付而非花费 | `sprint-status-retro.md` 2.2、2.3，`portfolio.md` 第 6 节 | — |
| 打开的风险条数不代表健康 | `portfolio.md` 第 1 节 | — |
| 阶段评审的结论：继续、有条件继续、返工、停止；条件落到具名角色和日期；过了评审不等于风险消失 | `governance.md` 第 7 节 | 与来源 5 合并，加暂停一种；与 PRD 门禁、发布关卡分工列表 |
| 影响压过概率（安全、合规、业务连续性，低概率也升级）；未知影响先调查 | `risk-and-priority.md` 1.2、`portfolio.md` 第 3 节 | 来源列的范围还有偿付能力，本 skill 面向交付团队，未列；来源写的是可能需要升级，本 skill 改为一律按严重处理、直接升级给发起人或组合拍板人，并优先于未确认依赖的例外 |
| 决策要写拖延的后果 | `portfolio.md` 第 6 节汇报开头 | — |
| 咨询项目的治理论坛设计、挣值、成本预测、合同与咨询交付语境 | 不取 | 本 skill 面向内部交付团队；成本口径由章程约定 |

## 取用与改动：来源 5（hard-half）

| 内容 | 去向 | 改动 |
|---|---|---|
| portfolio-stage-gate：评审是资源决定不是状态会；一次只评一个；门槛与停止标准在上一次评审写好、不临场挪；无门槛只能返工；继续而无人、钱、下次日期即空头继续，改判暂停；不计沉没成本；证据随投入加码；评审人是下一阶段资源的拥有者；说不出何时叫停则不开评审；证据对照表与空缺；本阶段要验证的假设 | `governance.md` 第 7 节，`portfolio.md` 第 5 节 | 结论用中文五选一（继续、有条件继续、暂停、返工、停止），来源的 Go / Kill / Hold / Recycle 分别对应继续、停止、暂停、返工，有条件继续取自来源 4；Stage-Gate 是注册商标，本 skill 称阶段评审，不使用该商标；来源的商业论证、期权费等投资语境不取；另取：安全类门槛未达到只能返工或停止、评审次数与投入相称、从不叫停的组合要追问一句；阶段评审模板的结构（证据对照四列、要验证的假设四列、若继续一节）取自来源的 gate-paper 模板并译写；在来源之外加了唯一拍板人、首个阶段评审写进章程、缺门槛不开正式评审、有条件继续的条件登记 RAID |
| resource-collision：冲突的定义（同一稀缺的人或技能、两个以上项目、窗口重叠）；点名到人或技能而非团队；需求与可用量要有来源，没有就留空缺；先写排序规则再解；五种解法（排先后、换人、推迟、放弃或停启、外采）；两边兼顾不算解法，除非双方同意并写明日期；关键技能无替补不对半分；只提一个请求；已确认与意向预订分开 | `portfolio.md` 第 2 节，`scripts/portfolio_rollup.py` 资源部分 | 冲突加上需求合计超过可用量的条件；资源分配表加起止日期、类型、预订列，脚本按日期重叠取峰值；改到里程碑的先走变更请求；计划外缓冲只在 Sprint 层扣；来源的不对半分限于安全关键技能，本 skill 扩大到没有替补的关键技能；在来源之外加了可用量列与单个成员内部超出不算组合冲突 |
| 两个技能的拒答与转交其他技能的路由、利用率不作为决定依据的立场 | 部分取 | 不取路由；利用率只作线索，组合台账不出总分 |

## 取用与改动：来源 6（LifeOS RootCauseAnalysis）

| 内容 | 去向 | 改动 |
|---|---|---|
| 按问题的样子选方法的对照表；事故类以复盘为框架、每条线索内套用其他方法；方法之间何时切换 | `root-cause.md` 第 3 节 | 改为交付团队的问题情境，并给出从上往下取第一条的先后；事故以外，跨团队、有几条独立线索的也用复盘做框架；去掉来源的领域对照表与按可用时长选方法的表 |
| 5 个为什么：层数不固定、分叉成树、收敛点、倒读检验、不停在操作失误或改不了的抽象、缺环不编 | `root-cause.md` 4.1 | 停止条件写成改得动且有人管得着，团队管不着的组织层原因也算并转交拍板人；加不停在人手不够这类笼统说法 |
| 鱼骨图：候选原因是假设、每条配验证方法、空的类别可能是缺了那方面的人、不编帕累托比例 | `root-cause.md` 4.2 | 来源默认的 6M 分类改为六类（人、流程、工具与环境、需求与输入、外部依赖、组织），其中几类与参考来源 lyndonkl 的根因类别相近，见下文；排先后只用真实计数 |
| 是与不是对比：四个维度、变化窗口、没发版不等于没变化、留下的原因要解释所有的是且不跟不是矛盾、共同条件不能单独当原因、最好在测试环境回退确认、没有基准不编对比、不适用的情形 | `root-cause.md` 第 3 节、4.3 | 变化举例沿用来源的列表（数据量、定时任务、节假日、排班、外部依赖），加了人员轮换与配置；确认限定在测试环境，做不到写局限 |
| 故障树：与或门、最小割集、单点优先、共因、有数据才写概率、割集阶数高不能单独当作安全的证据、不独立时不套公式、无冗余时用更简单的方法 | `root-cause.md` 4.4 | 以定性分析为主，有真实数据时才写概率；来源的优先与门、抑制门、异或门，独立事件的概率公式与计算工具不取；共因与组合层的资源冲突、同根对上 |
| 无责复盘：先有时间线再排原因、按当时能拿到的信息评价决定、直接原因 / 系统因素 / 发现慢 / 恢复慢分开、防线表、做得好照写、经验、行动项要有具体负责人与核实方式、主要行动项只有培训和提醒时回头重查诊断、复查行动项完成与同类问题是否再现、不和绩效混在一起 | `root-cause.md` 第 2、4.5、5、7 节 | 来源要求至少 3 条系统因素，改为有证据的有几条写几条（来源自己也要求不为凑数编）；来源的 30 天复查改为按同类机会的次数定窗口、30 天作下限，写成算式；组织层原因在系统因素里单独标出；来源的 UTC 时间、事件单链接、密级字段不取 |
| 行动项强度：消除 > 强制或自动化 > 简化或标准化 > 培训 > 提醒或文档 | `root-cause.md` 5.1 | 例子换成交付流程里的 |
| 不把用户的猜测当事实、证据不足写成缺口、交付的分析已做完 | `root-cause.md` 第 2、7 节 | — |
| Apollo / RealityCharting、FMEA、跨服务日志与时钟偏差、转交 SystemsThinking 等其他技能的路由、用户自定义配置目录 | 不取 | 本 skill 面向交付团队的项目管理，不做工程级故障诊断（`root-cause.md` 第 1 节写明不适用）；不依赖来源的其他技能 |

在来源之外加了：验证待办与待验证状态、行动项的放弃与不采纳出口、复发先核对机理与第二次重开转交拍板人、行动项去向（台账、RAID、变更请求、拍板人的决定）与 RAID 问题的复核衔接、顺利发布的简版复盘。

Kepner-Tregoe 是 Kepner-Tregoe, Inc. 的商标，本 skill 只用它指明是与不是对比这一思路的出处，方法本身称是与不是对比。来源各文件为英文，本 skill 全部改写为中文，未逐字照搬。

## 本 skill 自撰：WBS 与排期表

`wbs-and-schedule.md` 与 `scripts/schedule_calc.py` 不取自上面六个来源，也没有参考 borghei。其中的通用做法属于项目管理常识，按本 skill 的链路自行写成：WBS 的 100% 规则，正推、逆推求浮动与关键路径，同一责任人不并行的资源排队。关键路径的用法沿用 `risk-and-priority.md` 第 2.2 节（来源 3）。
字段名和阶段骨架按团队现行的多维表格排期模板整理，示例与夹具全部使用通用名称。

## 参考：borghei/Claude-Skills（非 MIT，只取思路）

| 参考 | 版本 | 许可 |
|---|---|---|
| **borghei/Claude-Skills** 的 `project-management/program-manager` 与 `project-management/senior-pm` · https://github.com/borghei/Claude-Skills | 提交 `25bf86b` | Commons Clause License Condition v1.0 + MIT，Copyright (c) 2025-2026 Amin Borghei |

该许可在 MIT 之上附加 Commons Clause：不得售卖该软件，也不得以它的功能为全部或主要价值提供收费产品或服务（包括托管、咨询、支持类收费服务）；分发其副本或实质部分时，须附带许可与该声明。

本 skill 没有使用它的代码：`scripts/portfolio_rollup.py` 读本 skill 自己的 Markdown 格式，与它读 JSON 的脚本无关。组合层的正文是本 skill 自己的写法，2026-11-10 复核后又改写了一遍：删除了几处近乎逐句意译的句子和沿用来源结构的表格；成员健康度不再分维度上色，改为只抄成员自报；资源冲突与阶段评审改以来源 4、5（MIT）为主。改写后仍保留、与它的思路相近的规则如下，如实列出：

| 与参考来源思路相近的规则 | 在本 skill 的位置 |
|---|---|
| 组合汇报不出一个平均的总颜色，红色成员逐个点名 | `portfolio.md` 第 1、6 节 |
| 按人合计跨项目的投入占比，超出可用量即冲突（另见来源 5） | `portfolio.md` 第 2 节 |
| 资源计划遇重大变化与按季度重定基线 | `portfolio.md` 第 2 节 |
| 组合级风险看集中，同一根因跨项目合并看 | `portfolio.md` 第 3 节 |
| 跨项目依赖的矩阵视图，开工前把跨团队依赖跟双方对上 | `portfolio.md` 第 4 节 |
| 定期对每个成员做继续与否的表态并记录资源调整（另见来源 5） | `portfolio.md` 第 5 节 |
| 汇报把需要的决定放在开头 | `portfolio.md` 第 6 节 |
| 汇总脚本只报告、不判定 | `scripts/portfolio_rollup.py` |
| 名单之外的人在干活时冲突会被漏掉，下结论前先问名单全不全 | `portfolio.md` 第 2 节 |
| 组合从没停止或暂停过成员时，追问继续的标准是否起作用（另见来源 5） | `portfolio.md` 第 5 节 |
| 依赖状态变化时重算跨成员关键路径 | `portfolio.md` 第 4 节 |
| 组合排序对着组合层统一的目标打分，各成员的指标不可比 | `portfolio.md` 第 5 节 |
| 组合约定里写升级层级与各级响应时限 | `portfolio.md` 第 0 节 |
| 拿不准：连续两期为 ⚪ 就登记一条问题，句式与其连续两期为红就升级相近 | `sprint-status-retro.md` 2.1 |

其中资源重定基线、跨成员依赖开工前对齐两条，2026-11-10 第二轮复核指出原写法近乎逐项意译，已改为本 skill 自己的机制：重定基线改由阶段评审、组合复盘、变更请求和 Sprint 计划这些事件驱动；跨成员依赖改为沿用依赖握手，并以在提供方台账里找到对应任务编号作为确认的证据。

以上是通行的项目组合管理做法，本 skill 按自己的规则重新组织和撰写，没有复制其文字、示例与代码，因此未附带 Commons Clause。若日后将本 skill 用于收费产品或服务，建议先复核这部分。

## 参考：lyndonkl/claude 的 postmortem（未附许可文件，只取思路）

| 参考 | 版本 | 许可 |
|---|---|---|
| **lyndonkl/claude** 的 `skills/postmortem` · https://github.com/lyndonkl/claude | 提交 `4acc337`：SKILL.md 与 resources | 仓库没有 LICENSE 文件；README 的许可一节只写了可以随 Claude Code 自由使用，各技能自带署名，不是一份标准的开源许可 |

因为没有明确的许可条款，本 skill 没有使用它的模板、示例与评分表，正文按本 skill 的链路自行撰写。但下面这些与它相同或相近，其中有几处是短语层面的相同，如实列出：

| 与参考来源相同或相近之处 | 在本 skill 的位置 |
|---|---|
| 无责复盘分五步，五步的划分与其工作流一致（立案含影响量化、查因、定改法、成文分享、跟踪行动项直到完成）；步骤名本 skill 自拟 | `root-cause.md` 4.5、5.3 |
| 症状短语总是赶工、没时间测试，以及要改的是不现实的截止日期、资源约束、激励错位，与其系统性问题一条的说法相同（这两句也是本 skill 用户提出需求时的原话）；查证方法、落在链路哪里、谁拍板、第四类范围不受控为本 skill 自撰 | `root-cause.md` 5.2，SKILL.md 第 6 节「对流程，不对人」，README，对外日志 (16) |
| 写环节放过了它、不写谁犯了错（其护栏一节的写法对照） | `root-cause.md` 第 7 节，SKILL.md 第 6 节「对流程，不对人」 |
| 不停在某人犯错，追问为什么可能犯错、为什么没拦住 | `root-cause.md` 4.1 |
| 行动项要具体，不写改进测试、改进沟通、更细心这类说法；要有具名负责人和期限 | `root-cause.md` 5.1、5.2 |
| 鱼骨图六类里的人、流程、外部依赖、组织，以及工具与环境，与其根因类别和鱼骨分类相近 | `root-cause.md` 4.2 |
| 影响要量化 | `root-cause.md` 第 2 节 |
| 事故还在进行时先处理事故；没有可学之处的小问题不做 | `root-cause.md` 第 1 节 |

以上都是通行的事故复盘做法，其中多条在来源 6（MIT）里也有。若日后对方补上许可条款，再按条款复核这部分。

## MIT License（上游原文）

六个来源均以 MIT 许可发布。下面是合并后的完整许可声明，各来源的版权行逐条列出：

```
MIT License

Copyright (c) 2026 Ismael G Marin Cabrera（来源 1）
Copyright (c) 2025 Commit Media SARL（来源 2）
Copyright (c) 2026 AbsolutelySkilled（来源 3）
Copyright (c) 2026 Anot（来源 4）
Copyright (c) 2026 Manuel Morano（来源 5）
Copyright (c) 2025-2026 Daniel Miessler（来源 6）

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
