# AI User Research Operating System V4.0

**A portable, executable and traceable research package for AI and Agents**

[中文版](README_zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-7c5cfc.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/diandian1001/user-research-sop?style=social)](https://github.com/diandian1001/user-research-sop)
[![Version](https://img.shields.io/badge/Version-V4.0-10b981.svg)](https://github.com/diandian1001/user-research-sop)

Give this repository to an AI or Agent and it can start from the business decision, select an appropriate research method, generate materials, maintain project state, manage evidence and produce ready-to-use deliverables.

| Entry | File | Best for |
|---|---|---|
| Repository-aware Agent | `AGENTS.md` | Agents that can inspect a repository |
| Skill / System Instructions | `SKILL.md` | Platforms supporting Projects, Skills or system instructions |
| Any AI Chat | `PORTABLE.md` | Models that cannot reliably read a full GitHub repository |

Clear tasks default to Quick Execution Mode. The AI asks a question only when the missing answer would materially change the method, scope or conclusion.

---

## Start in One Prompt

### Repository Mode

```text
Read AGENTS.md and use this repository to complete the following user-research task:
[paste task]
```

### Skill Mode

```text
Use SKILL.md in Quick Execution Mode to complete:
[paste task]
```

### Any AI Mode

Copy the full contents of `PORTABLE.md`, then append the task.

The first response should state the task understanding, business decision, execution mode, recommended method, confirmed information, assumptions, critical gaps and next action.

---

## 30-Second Example

**Input** — Tell the AI:
> *"Help me understand why our new users are not coming back after the first week."*

**Process** — The AI will:
1. Ask clarifying questions (define "not coming back", timeline, audience)
2. Recommend the right method (likely funnel analysis + interviews)
3. Generate a data request template and interview guide
4. Guide you through analysis step by step
5. Help you write the report

**Output** — You get:
- A structured research plan
- Ready-to-use data request and interview materials
- An analysis framework with step-by-step guidance
- A completed report with prioritized action recommendations

→ [Full walkthrough example](examples/完整案例-Walkthrough.md) | [Real case study](examples/case-telecom-conversion-diagnosis.md)

---

## What It Supports

### Currently Supported

| Research Task | Method | Best For |
|--------------|--------|----------|
| Understanding user motivations | In-depth interview guide | Exploratory research — *why* questions |
| Validating hypotheses at scale | Survey/questionnaire design | Quantitative validation — *what* and *how much* |
| Competitive landscape analysis | Desktop research | Understanding what others are doing |
| Conversion & retention analysis | Funnel analysis | Finding where users drop off |

### Not Currently Supported

- Usability testing (requires task-based observation protocols)
- Eye-tracking / biometric studies
- A/B testing design and statistical power analysis
- Longitudinal / diary studies
- Field ethnography
- Accessibility audits

This list will grow as the project evolves. If your research need falls outside the current scope, the AI will tell you honestly rather than pretending to cover it.

### Who This Is For

- Product managers who need to run user research but lack formal training
- Designers who want to validate their work with user evidence
- Junior researchers looking for a structured workflow
- Teams that want to standardize their research process

### Who This Is NOT For

- Academic researchers requiring rigorous methodological justification
- Regulated clinical/medical research
- Situations where research output will be used as legal evidence
- Complete beginners who have never heard of "user research" — you'll need basic familiarity with research concepts

---

## How to Use

### ChatGPT

1. Open a new chat
2. Paste: `https://github.com/diandian1001/user-research-sop` and say *"Use SKILL.md from this repo"*
3. If ChatGPT cannot read the URL directly, copy the content of `SKILL.md` and paste it as your first message
4. Then describe your research need

### Claude

1. Create a new Project in Claude
2. Add `SKILL.md` as Project Knowledge
3. Start a conversation and describe your research need
4. Claude will follow the guidance script automatically

### Hermes

1. Add the repo URL or `SKILL.md` to your Hermes session
2. Say: *"帮我做用户研究"* or *"Guide me through a user research project"*
3. Hermes will use its tools (search, file analysis, code execution) where available

---

## What the AI Will Guide You Through

| Step | What Happens |
|------|-------------|
| Step 1: Understand Needs | 4 questions (multiple choice + fill-in) to clarify your research objective |
| Step 2: Recommend Method | Decision tree picks the right method for your problem and timeline |
| Step 3: Generate Materials | AI creates interview outlines or survey drafts based on rules, not fixed templates |
| Step 4: Analysis Guidance | Step-by-step framework for quantitative (5 steps) or qualitative (4 steps) analysis |
| Step 5: Report Generation | Fill-in-the-blank template generates a complete Markdown report |

---

## File Structure

```
user-research-sop/
├── AGENTS.md                ← Repository loading and execution protocol
├── PORTABLE.md              ← Single-file package for any AI
├── SKILL.md                 ← Core operating instructions (V4.0)
├── README.md                ← This file (English)
├── README_zh.md             ← Chinese documentation
├── LICENSE                  ← MIT License
├── evaluation/
│   └── benchmark.md         ← Cross-platform repeated-run benchmark design
├── templates/               ← Blank templates (copy & use)
│   ├── project-state.md
│   ├── evidence-ledger.md
│   ├── 需求确认表.md
│   ├── 访谈记录表.md
│   ├── 数据提需模板.md
│   └── Agent-Loop-审查清单.md
├── examples/                ← Filled examples & case studies
│   ├── 完整案例-Walkthrough.md
│   ├── case-telecom-conversion-diagnosis.md  ← Real case study
│   ├── 需求确认表-示例.md
│   ├── 访谈记录表-示例.md
│   └── 数据提需模板-示例.md
└── prompt-templates/        ← Copy-paste prompts for each phase
    ├── 01-需求承接.md
    ├── 02-研究设计.md
    ├── 03-数据采集.md
    ├── 04-数据分析.md
    ├── 05-报告交付.md
    └── 06-Agent-Loop.md
```

---

## Important Limitations

Please read these before using the project:

1. **AI cannot replace research ethics judgment.** You are responsible for informed consent, privacy protection, and ethical data handling.
2. **AI cannot guarantee sample quality.** It can recommend sample sizes, but cannot verify that your respondents are representative.
3. **AI output requires human verification.** Facts, numbers, and inferences must be checked before use. The AI may misclassify, misinterpret, or miss nuance.
4. **Sensitive data requires local processing or anonymization.** Do not paste raw user data containing PII (personally identifiable information) into public AI services.
5. **This project does not cover all research methods.** See "What It Supports" above for current scope.
6. **Do not use this project to fabricate research findings or user evidence.** It is a guidance tool, not a substitute for actual research.

---

## V4.0 Core Upgrades

- **Three execution modes**: Quick Execution, Standard Collaboration and Guided Learning
- **Agent loading protocol**: `AGENTS.md` defines the repository reading and execution order
- **Portable single-file package**: `PORTABLE.md` can be copied directly into any AI chat
- **Decision first**: the business decision is defined before choosing a method
- **Project state management**: scope, definitions, assumptions and progress persist across stages
- **Claim-level evidence ledger**: important findings trace back to data, verbatim statements and sources
- **Automatic delivery**: the AI generates deliverables from evidence instead of asking the user to refill templates
- **Corrected method rules**: no universal 500-response target, fixed 5% threshold or default NPS
- **Cross-workflow routing**: complex competitive analysis routes to the dedicated workflow
- **Benchmark design**: repeated cross-platform evaluation with explicit source verification

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| V1.0 | 2026-06 | Six-phase linear workflow + 4 templates |
| V2.0 | 2026-06 | Added Agent Loop, pitfall warnings, sub-processes |
| V2.1 | 2026-06 | Rewritten README, 6 prompt templates, 3 examples, FAQ |
| V3.0 | 2026-07 | AI-first rewrite: guidance script, rules over templates, decision tree |
| V4.0 | 2026-07 | Execution packaging: AGENTS, PORTABLE, project state, evidence ledger, automatic delivery and Benchmark |

---

## Author

**Diandian** — User Researcher, 2+ years UX Research experience, Psychology background. Focused on bridging user research methodology with AI workflows.

---

## License

MIT — Use it however you want, including commercially. Just give credit.
