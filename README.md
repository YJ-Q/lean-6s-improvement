# lean-6s-improvement

制造业现场 Lean 6S 整改闭环 AI skill。

本项目用于把模糊的制造现场异常转化为可派工、可验收、可防复发的整改闭环任务，而不是生成泛化分析报告。重点覆盖：

- 现场问题结构化：位置、异常、对象、风险、证据、重复信号。
- 6S 分类：整理、整顿、清扫、清洁、素养、安全。
- 习惯性异常识别：判断一次性异常、疑似习惯性异常、很可能习惯性异常。
- 整改方案生成：即时控制、原因检查、永久性对策、验收标准。
- 闭环质量判断：已闭环、有条件闭环、未闭环，防止假闭环。

默认输出采用快速模式，优先给出当班动作、防复发措施、验收标准和闭环证据。用户明确要求时，可切换为整改单模式或闭环审核模式。

## 文件结构

```text
.
├── SKILL.md
├── README.md
├── docs/
│   ├── implementation-plan.md
│   ├── case-validation.md
│   └── case-writing-guide.md
├── examples/
│   ├── cases.md
│   └── cases2.md
├── references/
│   ├── classification.md
│   ├── closure-check.md
│   └── habitual-abnormality.md
└── scripts/
    └── lean_6s_mvp.py
```

核心文件说明：

- `SKILL.md`：skill 的主流程和使用原则。
- `references/classification.md`：6S 分类边界规则。
- `references/closure-check.md`：闭环和假闭环判断规则。
- `references/habitual-abnormality.md`：习惯性异常判断规则。
- `examples/cases.md`：虚拟制造现场案例库。
- `examples/cases2.md`：基于真实项目记录整理的案例库。
- `scripts/lean_6s_mvp.py`：规则型 MVP 脚本，可做单条诊断和案例库回归测试。
- `docs/case-validation.md`：案例库和脚本测试记录。
- `docs/case-writing-guide.md`：新增案例的编写规范。

## 运行环境

脚本仅使用 Python 标准库，不需要安装第三方依赖。

如果本机 `python` 因中文路径等原因无法启动，可使用 Codex runtime 中的 Python：

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --help
```

## 单条问题诊断

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --problem "消防通道又被托盘堵住了，上周刚清理过，这周又堆起来" --pretty
```

输出包括：

- 先确认：追问决策关卡，提示是否必须先补关键信息。
- 初判：已知事实、主要风险、风险等级、主/副分类、不确定事项。
- 后续可补充：不阻断当前初判、但能提升整改质量的问题。
- 当班动作：2-4 条可立即执行的控制措施。
- 防复发措施：2-4 条现场控制优先的永久对策。
- 验收标准：可观察、可测量、可拍照或可记录。
- 闭环证据：照片、点检记录、责任确认和连续检查周期。

## 闭环判断

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --problem "灭火器前堆了纸箱" --rectified-text "已清理纸箱，消防器材前黄色禁停线已恢复，巡查表已加入每日检查项，闭环证据包括整改前后照片和巡查表记录" --pretty
```

闭环判断会返回以下之一：

- 已闭环。
- 有条件闭环。
- 未闭环。

## 案例库测试

测试虚拟案例库：

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --case-file examples\cases.md --test-cases --pretty
```

测试真实案例库：

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --case-file examples\cases2.md --test-cases --pretty
```

当前测试结果：

| 案例库 | 案例数 | 主分类 | 副分类 | 习惯性异常 | 闭环判定 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `examples/cases.md` | 14 | 14/14 | 14/14 | 14/14 | 14/14 |
| `examples/cases2.md` | 17 | 17/17 | 17/17 | 17/17 | 17/17 |

说明：

- 当前准确率统计主分类、副分类、习惯性异常和闭环判定。
- 副分类使用完全一致校验，并在每个案例的 `secondary.ok` 中展示。
- 闭环测试会去掉案例中的显式 `判定：...` 行，只使用理由和证据文本判断，避免直接读取答案。

## 追问决策关卡

脚本输出中的 `question_gate` 会把追问从普通报告字段前置为判断门槛：

- `status`：是否必须先回答关键问题。
- `confidence`：当前判断置信状态。
- `reason`：为什么这些信息会影响判断。
- `must_ask`：最多 3 个必须先确认的问题。
- `nice_to_have`：可后续补充的问题。

当 `status` 为 `must_answer_before_final_judgment` 时，当前结论只能作为初判；用户应先补充 `must_ask` 后再做最终分类、闭环或归档判断。

## 新增案例

新增案例前请先阅读：

```text
docs/case-writing-guide.md
```

建议新增案例放在 `examples/` 下，并保持字段结构一致。

每个案例至少包含：

- 用户输入。
- 现场背景。
- 应追问。
- 结构化结果。
- 6S 分类。
- 是否习惯性异常。
- 整改方案。
- 验收标准。
- 已整改后的闭环判断。
- 待讨论。

## 当前开发状态

已完成：

- 基础 skill 流程。
- 三份规则文档的边界补全。
- 虚拟案例库和真实案例库验证。
- MVP 脚本案例测试模式。
- 副分类纳入自动测试统计。
- 未闭环案例初步覆盖。
- 默认输出从分析报告型调整为整改闭环助手型。

仍待推进：

- 继续扩充清洁、素养、未闭环和假闭环案例。
- 将脚本输出中的措施、验收标准进一步调整为任务单字段。
- 根据更多真实案例减少硬编码规则，提高泛化能力。

## 协作建议

- 修改规则文档后，运行两个案例库测试，确认没有回归。
- 新增案例时，先按 `docs/case-writing-guide.md` 写完整字段，再运行脚本测试。
- 如果案例与规则冲突，优先判断是案例标注问题，还是规则边界需要补充。
- 不要把"已整改"直接等同于"已闭环"。闭环必须有证据、标准、责任和复查。
