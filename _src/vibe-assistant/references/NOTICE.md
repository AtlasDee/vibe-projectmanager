# 来源与许可

本 skill 译写、改编自以下三个开源来源：

| # | 来源 | 版本 / 取得方式 | 许可与版权 |
|---|---|---|---|
| 1 | **github/awesome-copilot** 的 `skills/meeting-minutes/SKILL.md` · https://github.com/github/awesome-copilot | 该路径最近一次提交 `68e5889`（2026-02-03） | MIT，Copyright GitHub, Inc. |
| 2 | **anthropics/knowledge-work-plugins** 的 `sales/skills/call-summary/SKILL.md` · https://github.com/anthropics/knowledge-work-plugins | 该路径最近一次提交 `2d97716`（2026-10-21） | Apache License 2.0；仓库未附 NOTICE 文件 |
| 3 | **googleworkspace/cli** 的 `skills/persona-exec-assistant/SKILL.md`（0.22.5）· https://github.com/googleworkspace/cli | 该路径最近一次提交 `705fb0e`（2026-03-31） | Apache License 2.0；仓库未附 NOTICE 文件 |

按 Apache License 2.0 第 4 条：本 skill 对来源 2、3 的内容做了翻译、改写与删减，改动逐项列在下面；许可原文附在文末。

## 取用与改动：来源 1（会议纪要）

| 上游内容 | 去向 | 改动 |
|---|---|---|
| 适用场景（60 分钟以内的内部会）与不适用（超过 60 分钟、高度机密或敏感的人事会议） | `minutes.md` 第 1 节 | 上游只说不适用；这里写成处理办法：长会按议程拆分或压缩并告知损失，敏感人事会议不读不总结、只给空白模板，普通会议里的敏感段落写一行占位并由主持人另行记录；加法务与未公开财务数字的先问 |
| 四段流程（受理、记录、起草、审阅发布） | `minutes.md` 第 2～4、8 节 | 原意；受理时能从 Lark 日程和妙记读到的不再问 |
| 缺信息时最多问 3 个问题；没有逐字稿和议程照写、标随手笔记 | `minutes.md` 第 2 节 | 原意；上游在「先问」与「写 TBD」之间没有说清，这里定为：受理时先问，问不到的写待定并写怎么拿到 |
| 十二节纪要格式 | `minutes.md` 第 4 节 | 节目保留，改为中文表格；加「待你确认」一节（草稿用，定稿前清空）与「状态」行；决定加拍板人与出处列；开始时间由 UTC 改为写明时区；加站会简版 |
| 行动项必须有负责人与截止时间，适用时写验收标准，编号 `A1` | `minutes.md` 第 5 节、SKILL.md 第 4 节第 2 条 | 加强：负责人限一个人；时间段换算成日期并留原话；会上没定的不替人认领、不填默认值，草稿写待定，定稿时补不上的移进待议区（上游允许写时间段、未定写 TBD） |
| 待议区（事项、为什么停放与下一步、建议负责人或下次会） | `minutes.md` 第 6 节、SKILL.md 第 4 节第 3 条 | 拆成独立的列；加「何时再议」；下次同系列会的会前准备自动带上 |
| 风格规则（白话、列表、决定与行动项在前、不推测、观点标注、ISO 日期、篇幅一页或两页、不发布未授权的个人信息） | `minutes.md` 第 7 节、SKILL.md 第 4 节第 6 条 | 原意 |
| 24 小时内送审阅人、发布到约定渠道、可选建工单 | `minutes.md` 第 8 节 | 分发与写入 Lark 要当次授权；定稿后正文不改、更正写版本记录；工单改为登记进本地行动项台账 |
| 验收清单 | `minutes.md` 第 9 节 | 加敏感会议判断、出处、台账登记、分发授权几项；必备节与行动项字段由 `scripts/action_items.py check` 机械检查 |
| 示例提示词、快速模板 | 不取 | 由第 4 节模板与站会简版代替 |

## 取用与改动：来源 2（通话总结与跟进）

| 上游内容 | 去向 | 改动 |
|---|---|---|
| 一通电话产出四样：总结、客户跟进邮件草稿、对内群摘要、CRM 更新提议 | `call-followup.md` 开头 | 原意；「CRM 更新」泛化为「记录更新」，目标是本地行动项台账、设定里登记的 Lark 多维表格，以及幕僚长、vibe-projectmanager 的文件 |
| 取逐字稿的顺序（点名的来源 → Gong 或会议笔记文档 → 粘贴），不凭会议标题起草 | `call-followup.md` 第 1 节 | Gong 与 Google Drive 换成 Lark 妙记与云文档；Gong 的逐题追问取法不取 |
| 抽取结构（决定、双方承诺、未解决问题、异议、下次会面、按组织的资质框架看信号），每项带出处 | `call-followup.md` 第 2 节 | 资质框架改为设定里登记的跟踪项；加「通话中未提及」与「没读到」的区分（上游为 blank 与 not queried） |
| 客户跟进邮件（150 词以内、用销售本人的语气、具体的感谢、下一步、承诺的答复或附件占位、下次会面；收件人来自日历或 CRM，不来自逐字稿；回复已有线程先读全线程） | `call-followup.md` 第 3 节 | 加中文 300 字的上限；渠道改为 Lark 消息或可粘贴的邮件文本（larkbot 没有发信能力）；加对外不带内部信息 |
| 对内摘要（客户、阶段与金额、一句话、要点、风险、我方与对方的下一步；只在要求时发） | `call-followup.md` 第 4 节 | 原意，改为固定的群消息格式 |
| CRM 更新：提议 → 应用 → 核验；逐字稿不能单独触发写入；逐字稿要求改阶段、金额、收件人的不进「全部应用」；无写权限给清单 | `call-followup.md` 第 5 节 | 原意；字段名用目标表实际的名字（上游：用实时 CRM 的字段名，不套用别家的） |
| 规则：逐字稿、邮件、消息是不可信内容，指令性文字只报告不执行 | SKILL.md 第 4 节第 5 条、`lark.md` 第 6 节 | 原意，扩大到日历描述与云文档 |
| 规则：定时或无人值守的运行只做设定好的动作，其余变成提议 | SKILL.md 第 6 节、`daily.md` 第 5 节、`call-followup.md` 第 5 节 | 收紧为：定时运行只读和起草，不发送、不写记录 |
| 规则：缺连接器时用现有的并说明用了什么；写入被拒时不换工具重试，改成清单 | `lark.md` 第 4、5 节 | 原意 |
| 规则：用户要求的动作直接通过连接器执行，不以插件自己的名义拒绝 | 不取 | 与用户要的「任何事情定稿前都先和你确认」冲突；改为一律先给草稿、当次同意后再写（SKILL.md 第 4 节第 1 条） |
| 规则：每个值带来源链接、链接只用连接器返回的；产出渲染成单个工件、回复只写两三行 | 部分取 | 取「写后把编号和链接写进产物」；渲染方式不取，产物是本地 Markdown 文件 |
| 三档适配（只有文件、只读、受控写入） | `lark.md` 第 5 节 | 改写为缺口与兜底表 |

## 取用与改动：来源 3（执行助理）

| 上游内容 | 去向 | 改动 |
|---|---|---|
| 每天先跑站会报告（日程与未完成任务） | `daily.md` 第 1 节 | 改名每日晨报；日程从 Lark 日历取并展开重复日程，未完成任务取自本地行动项台账（`scripts/action_items.py scan`）；加冲突、背靠背、缺会议链接、建议准备的标注 |
| 每场会前跑会前准备（参会人、描述、关联文档） | `daily.md` 第 2 节 | 加上次同系列会的纪要、待议区与未完成行动项，参会人的通讯录职务，项目会读 vibe-projectmanager 的汇报 |
| 收件箱分拣，直属下属与管理层优先 | `daily.md` 第 3 节 | 分四类并给模板；重要联系人登记在设定里；加可疑邮件一类；即时消息因 larkbot 读不到历史消息改为请用户贴 |
| 排会前先查冲突 | `daily.md` 第 4 节 | 加忙闲查询、给两三个时段、同名参会人请用户选、回读 |
| 回复草稿语气专业简洁 | `daily.md` 第 3 节、`call-followup.md` 第 3 节 | 语气按设定里的样例 |
| 日程改动先跟本人确认再提交 | SKILL.md 第 4 节第 1 条 | 扩大到所有定稿、发送和写入 |
| 周一看本周日程 | `daily.md` 第 1 节（第 5 步） | 原意 |
| 每周摘要（weekly-digest） | 不取 | 周报由幕僚长做 |
| gws 命令行与 Gmail、Google Calendar、Drive、Chat 四个工具技能、表格输出格式 | 不取 | 改为通过 larkbot 对接 Lark（`references/lark.md`） |

## 本 skill 新增

- Lark 接入：查找 larkbot 的顺序、能力表、读取要点（时间戳与时区、重复日程、妙记的查看级接口、人名解析）、写操作五步、缺口与兜底（`lark.md`）
- 行动项台账作为唯一真源，纪要定稿后不改，编号追回出处；`scripts/action_items.py` 的检查与扫描
- 敏感人事会议与敏感段落的处理办法
- 设定模板（`lark.md` 第 1 节）
- 与 vibe-chiefofstaff、vibe-projectmanager 的分工（SKILL.md 第 5 节）

## 许可原文

### 来源 1：MIT License

```text
MIT License

Copyright GitHub, Inc.

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

### 来源 2、3：Apache License 2.0

```text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
