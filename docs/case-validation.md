# 现有案例回归验证记录

验证日期：2026-07-19

## 验证范围

- `examples/cases.md`：14 条虚拟案例。
- `examples/cases2.md`：17 条来自既有记录并已脱敏的案例。
- 验证维度：主分类、副分类、习惯性异常、闭环判定。

## 执行命令

```powershell
python scripts/lean_6s_mvp.py --case-file examples/cases.md --test-cases --pretty
python scripts/lean_6s_mvp.py --case-file examples/cases2.md --test-cases --pretty
```

## 结果

两组共 31 条案例均完成四项回归检查：

| 数据集 | 案例数 | 主分类 | 副分类 | 习惯性异常 | 闭环判定 |
|---|---:|---:|---:|---:|---:|
| `cases.md` | 14 | 14/14 | 14/14 | 14/14 | 14/14 |
| `cases2.md` | 17 | 17/17 | 17/17 | 17/17 | 17/17 |

## 解释边界

该结果只说明当前规则实现与这 31 条案例的既有标注一致，可作为回归稳定性证据；它不代表未知现场问题的准确率为 100%，也不等同于真实用户满意度、整改效率、事故率或投资回报已经得到验证。
