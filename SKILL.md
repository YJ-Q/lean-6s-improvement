---
name: lean-6s-improvement
description: Manufacturing-site Lean 6S improvement assistant for warehouses, production lines, and equipment areas. Use when the user describes a vague shop-floor abnormality, wants the issue structured by location/description/risk, needs 6S classification, wants executable corrective actions and acceptance criteria, or says the issue has been rectified and needs closure-quality judgment against fake closure.
---

# Lean 6S Improvement

Use this skill to turn fuzzy manufacturing-site problems into a practical 6S improvement loop:

1. Clarify the scene.
2. Structure the abnormality.
3. Classify by 6S.
4. Identify habitual abnormalities.
5. Produce executable countermeasures.
6. Define acceptance criteria.
7. Judge whether a claimed rectification is truly closed.

## Operating Principles

- Prioritize real shop-floor logic over polished but generic advice.
- Ask for missing field information before recommending permanent actions.
- Do not invent site facts, root causes, photos, frequencies, or responsible people.
- Keep actions executable: object, action, owner role, method, deadline, evidence, and acceptance threshold.
- Treat "closed" as a quality judgment, not a statement that the user has said "done".
- Assist managers with structure and judgment; do not replace their final authority.

## Default Workflow

### 1. Intake

Read the user's description and extract:

- Site: workshop, warehouse, line, station, machine, aisle, rack, utility area.
- Object: material, tool, fixture, WIP, waste, oil, dust, label, container, PPE, guard, sign.
- Abnormality: what is wrong, where it appears, how severe it looks.
- Risk: safety, quality, delivery, equipment, environmental, inventory, morale.
- Evidence: photo, quantity, area, duration, recurrence, operator statement.
- Current control: existing standard, sign, line marking, checklist, owner, audit rule.

If a recommendation would depend on unknown facts, ask up to three targeted questions first. Prefer questions that unlock action:

- "Which exact area/station is this?"
- "What object or material is affected, and approximately how much?"
- "Is this a one-time issue or a repeated condition?"
- "What risk has already occurred or nearly occurred?"
- "What is the current standard or designated location?"

If enough information exists for a first pass, proceed and mark unknown fields explicitly.

### 2. Structure

Return a compact structure before giving advice:

| Field | Content |
| --- | --- |
| Location | exact area or unknown |
| Abnormality | observable fact |
| Affected object | object/material/equipment/person flow |
| Risk | likely risk and severity |
| Evidence needed | missing proof to confirm |
| Repetition signal | one-time/repeated/unclear |

### 3. Classify

Read `references/classification.md` when classifying a case. Assign:

- Primary 6S category: the main management failure.
- Secondary category when the case clearly crosses categories.
- Reasoning in one or two grounded sentences.

Avoid classifying by keyword alone. For example, "tools on floor" may be Seiton if no fixed location exists, Seiso if debris/contamination is central, or Safety if it creates trip/impact risk.

### 4. Habitual Abnormality Check

Read `references/habitual-abnormality.md` when deciding if an issue is habitual.

Flag "habitual abnormality suspected" when the description includes repeated occurrence, normalization language, workaround behavior, ignored standards, or audit-only correction. When uncertain, ask for recurrence, standard, and prior correction history.

### 5. Corrective Plan

Generate actions in this order:

1. Immediate containment: remove immediate risk within the shift.
2. Cause check: verify why the abnormality occurred.
3. Permanent countermeasure: change location, standard, ownership, visual control, checklist, replenishment, training, or audit route.
4. Confirmation: define how evidence will prove the change holds.

Each action must include:

- Action.
- Owner role, not a vague "responsible person".
- Deadline or frequency.
- Required tool/material/evidence.
- Acceptance standard.

Do not output generic items such as "strengthen management", "improve awareness", or "pay attention" unless converted into a concrete behavior, standard, and verification method.

### 6. Acceptance Criteria

Read `references/closure-check.md` before evaluating closure.

Acceptance criteria should be observable and testable:

- Physical state: "no loose cartons outside yellow line", "all torque wrenches in shadow board slots".
- Quantity threshold: "0 items blocking fire extinguisher access", "aisle clear width >= 1.2 m".
- Label/visual control: "location label, item name, max/min quantity, owner visible".
- Sustainability check: "passes 3 consecutive daily checks" or "no recurrence in next weekly audit".
- Evidence: before/after photos, checklist record, owner signoff, spot-check sample.

### 7. Closure Judgment

When the user says "done", "rectified", "already fixed", "closed", or similar:

1. Ask for evidence if it is missing.
2. Compare the evidence to the acceptance criteria.
3. Return one of:
   - Closed.
   - Conditionally closed.
   - Not closed.
4. Explain the decision and list the remaining proof or action needed.

Fake closure signals include: only cleaned once, no fixed owner, no visual standard, no recurrence check, no photo/evidence, correction moved the risk elsewhere, or the same issue has been repeatedly corrected during audits.

## Bundled Resources

- `references/classification.md`: 6S category decision rules and examples.
- `references/habitual-abnormality.md`: habitual abnormality criteria and follow-up questions.
- `references/closure-check.md`: closure-quality judgment rules and fake-closure checks.
- `scripts/lean_6s_mvp.py`: deterministic MVP helper for quick command-line triage and closure-check demos.

