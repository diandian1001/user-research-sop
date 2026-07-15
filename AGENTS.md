# AGENTS.md

## Repository Purpose

This repository is an executable AI user-research operating system.

Its purpose is to help an AI or Agent move from a business problem to a professionally structured research plan, research materials, evidence analysis and final deliverables.

This file defines how an Agent must load and execute the repository.

## Required Loading Order

1. Read `SKILL.md`.
2. Identify the user's task and select an execution mode.
3. Check available capabilities:
   - web search;
   - uploaded-file reading;
   - spreadsheet or data analysis;
   - code or Python execution;
   - persistent file editing.
4. Read only the references, templates and examples needed for the current task.
5. Create or update the project state using `templates/project-state.md`.
6. Execute the work.
7. Record evidence using `templates/evidence-ledger.md`.
8. Run the delivery quality gate before declaring completion.

Do not treat the README as the main operating instruction. README files explain the project to humans; `SKILL.md` controls execution.

## Execution Mode Selection

Use one of three modes:

### 1. Quick Execution

Use when the task is clear and the user wants a usable result quickly.

- Infer non-critical missing information.
- Mark assumptions explicitly.
- Ask only when a missing answer would materially change the method or conclusion.
- Produce the requested deliverable directly.

This is the default mode for a clearly stated task.

### 2. Standard Collaboration

Use when the work has meaningful ambiguity, multiple stakeholders or moderate risk.

- Confirm the decision problem and scope.
- Execute independently between key decision gates.
- Ask for confirmation only at major method or scope choices.

### 3. Guided Learning

Use only when the user explicitly wants to learn the research process.

- Ask one question at a time.
- Explain why each step matters.
- Let the user participate in method selection and material creation.

Do not apply Guided Learning behavior to every user by default.

## Startup Protocol

The Agent's first substantive response must contain:

```markdown
## 任务理解
- 当前业务问题：
- 研究需要支持的决策：
- 目标用户：
- 预期交付物：

## 执行方式
- 执行模式：
- 推荐研究方法：
- 当前可用材料或工具：

## 信息状态
- 已确认：
- 默认假设：
- 关键缺口：

## 下一步
- 直接开始执行，或只提出一个会实质改变方案的关键问题。
````

Do not begin with a long explanation of user research.

## Autonomy Rules

1. Information sufficient: execute directly.
2. Non-critical information missing: make a reasonable assumption and label it `【假设】`.
3. Critical information missing: ask the minimum necessary question.
4. Data unavailable: provide a data request, collection plan or downgraded analysis.
5. Evidence insufficient: use `【待验证】`; do not fabricate findings.
6. Tool unavailable: state the limitation and reduce the scope.
7. Never claim that an interview, survey, test, search or analysis was performed when it was not.
8. Never fabricate quotes, respondents, sample sizes, statistics or source URLs.

## Project State

For multi-step tasks, maintain a project state containing:

* current business decision;
* research questions;
* target users;
* available evidence;
* confirmed scope;
* assumptions;
* unresolved questions;
* completed deliverables;
* current stage;
* next action.

When persistent files are available, save it as `project-state.md`.

When persistent files are unavailable, maintain the same structure in the conversation.

## Evidence Rules

Every important finding must be classified as:

* `【事实】`: directly supported by data, a source or a verbatim user statement;
* `【推论】`: interpretation based on one or more facts;
* `【待验证】`: plausible but not yet supported;
* `【建议】`: proposed action based on the current evidence.

Important claims should receive a Claim ID such as `UR-C001`.

Final reports must allow the reader to trace important conclusions back to evidence.

## Cross-Repository Routing

Use `competitive-analysis-workflow` when the task requires:

* systematic competitor selection;
* evidence grading across multiple competitors;
* product, journey, pricing or business-model comparison;
* competitive opportunity prioritisation;
* a complete competitive-analysis report.

Repository:

`https://github.com/diandian1001/competitive-analysis-workflow`

Keep simple desktop research inside this repository.

## Completion Rule

Do not declare the work complete until:

* the decision question is answered;
* assumptions and limitations are visible;
* major findings have evidence;
* recommendations have owners or owner types, first actions and validation indicators;
* unsupported claims are removed or labelled;
* the requested output format is delivered;
* the quality checklist in `SKILL.md` passes.

If any requirement fails, mark the delivery as incomplete and explain the blocker.
