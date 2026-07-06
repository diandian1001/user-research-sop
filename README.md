# User Research Standard Operating Procedure (SOP) V2.1
[![License: MIT](https://img.shields.io/badge/License-MIT-7c5cfc.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/diandian1001/user-research-sop?style=social)](https://github.com/diandian1001/user-research-sop)
[![Version](https://img.shields.io/badge/Version-V2.1-10b981.svg)](https://github.com/diandian1001/user-research-sop)

[中文版](README_zh.md)

An **out-of-the-box** user research methodology covering survey design, user interviews, behavioral data analysis, and competitive research.

> Whether you're a junior researcher just getting started or a seasoned professional looking to leverage AI, this SOP works right out of the box.

---

## ✨ What Can It Do For You

- 📋 **Requirement Alignment** — Lock down ambiguous requests with a 3-field confirmation checklist before you start
- 📝 **Survey / Interview Guide Design** — Follow structured guidelines to draft questionnaires and discussion guides
- 📊 **Data Analysis** — Quantitative 5-step + Qualitative 4-step frameworks, each with built-in quality checks
- 📄 **Report Delivery** — Conclusion-first structure + pre-delivery checklist so your output is ready to present as-is
- 🤖 **AI Enhancement (Agent Loop)** — Multi-model cross-review that automatically catches blind spots you might miss

---

## 📁 Project Structure

```
user-research-sop/
├── README.md                 ← You are here (English)
├── README_zh.md              ← 中文版说明文档
├── SKILL.md                  ← Full SOP document (core)
├── LICENSE                   ← MIT License
├── prompt-templates/         ← Copy-paste prompts for each phase
│   ├── 01-需求承接.md
│   ├── 02-研究设计.md
│   ├── 03-数据采集.md
│   ├── 04-数据分析.md
│   ├── 05-报告交付.md
│   └── 06-Agent-Loop.md
├── examples/                 ← Filled examples + full walkthrough
│   ├── 完整案例-Walkthrough.md  ← 🔥 End-to-end walkthrough, start here
│   ├── 需求确认表-示例.md
│   ├── 访谈记录表-示例.md
│   └── 数据提需模板-示例.md
└── templates/                ← Blank templates (copy & use)
    ├── 需求确认表.md
    ├── 访谈记录表.md
    ├── 数据提需模板.md
    └── Agent-Loop-审查清单.md
```

> **Note:** Templates and examples are in Chinese. If you're using this for a Chinese-speaking research context, they're ready to use as-is. For non-Chinese contexts, use them as structural references.

---

## 🚀 Fastest Way to Start

**Skip all docs and read this one file:** [`examples/完整案例-Walkthrough.md`](examples/完整案例-Walkthrough.md)

It's a complete story: from "a stakeholder asks for a research project" to "delivering the final report." Every step, every prompt to copy, every template to fill — connected end to end. Read it once and you'll know exactly how to use this SOP.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Clarify What You Need To Do

Open `templates/需求确认表.md` and fill in three fields:

```markdown
## Research Objective
What decision does this support? (e.g., Decide whether to add a new data package for Game X in Q3)

## Deliverable
What to produce and for whom? (e.g., Executive summary PPT for leadership)

## Timeline
When is the deadline? (e.g., Data collection by July 15, report delivered by July 22)
```

> 💡 If the stakeholder can't articulate the objective clearly, **don't start.** Push back and align before proceeding.

### Step 2: Pick Your Method, Follow the Flow

| Your problem | Recommended method | See chapter |
|-------------|-------------------|------------|
| Don't know what users are thinking | In-depth interviews | [SKILL.md Phase 2 — Interview Guide](SKILL.md#24-访谈提纲设计规范) |
| Need to validate a hypothesis | Survey / questionnaire | [SKILL.md Phase 2 — Survey Design](SKILL.md#22-问卷设计规范) |
| What are competitors doing | Desktop research + text clustering | [SKILL.md Sub-process A — Competitive Research](SKILL.md#子流程a竞品研究专项) |
| Where are users dropping off | Funnel analysis | [SKILL.md Sub-process B — Funnel Analysis](SKILL.md#子流程b漏斗转化分析专项) |

### Step 3: Add AI (Optional but Recommended)

If you want AI to review your survey draft or check your report, see `prompt-templates/06-Agent-Loop.md` for multi-model review setup.

> 💡 **Works without AI too.** The entire SOP is a pure methodology — no AI tools required. AI is an accelerator, not a requirement.

---

## 🤖 What Is an Agent Loop?

An Agent Loop = two AI models reviewing each other's work to catch blind spots.

```
Your survey draft
      ↓
Primary model (Claude/GPT) → Reviews wording, logic, coverage
      ↓
Review model (DeepSeek) → Finds factual errors, missing dimensions, counterexamples
      ↓
You confirm edits → Proceed to next phase
```

**Setup guide:** [`prompt-templates/06-Agent-Loop.md`](prompt-templates/06-Agent-Loop.md)

---

## 📌 Prerequisites

### Required (Free)

- Any Markdown editor (VS Code, Typora, even Notepad works)
- An AI chat tool (ChatGPT, Claude, DeepSeek, Kimi — pick any one)

### Recommended

- **Dual AI models**: one for generation, one for review (e.g., Claude + DeepSeek)
- **Tavily API**: for competitive data search (free tier is enough)
- **Hermes Agent**: auto-loads this SOP and runs the Agent Loop (optional)

### Not Required

- ❌ No coding needed
- ❌ No software installation needed
- ❌ No paid APIs (free models work fine)

---

## ❓ FAQ

**Q: What if I only have one AI model (no second model for review)?**
A: You can still use it. Draft in one conversation, then open a new conversation and ask the model to review your draft. The effect is slightly weaker than dual-model review, but much better than nothing.

**Q: I'm doing user research solo — no team. Can I still use this?**
A: Absolutely. This SOP was designed for solo researchers. The Agent Loop's "review model" replaces the role of a colleague doing a peer review.

**Q: I'm not a user researcher — can I use this?**
A: Yes. Product managers doing competitive analysis, operations teams doing user research, entrepreneurs validating markets — the core methodology is universal.

**Q: How do I use this with Hermes Agent?**
A: Place `SKILL.md` in your `~/.hermes/skills/` directory. Hermes will auto-detect and load it. Then just say "help me do user research" and it will follow the SOP workflow.

**Q: How do I modify the SOP content?**
A: Fork this repo, make your changes, and submit a PR. Or edit `SKILL.md` locally to tailor it to your specific business context.

---

## 📝 Changelog

| Version | Date | Changes |
|---------|------|---------|
| V1.0 | 2026-06 | Six-phase linear workflow + 4 templates |
| V2.0 | 2026-06 | Added Agent Loop, pitfall warnings, sub-processes |
| V2.1 | 2026-06 | Rewritten README, 6 prompt templates, 3 examples, FAQ |

---

## 📄 License

MIT — Use it however you want, including commercially. Just give credit.

---

> Author: [diandian1001](https://github.com/diandian1001) · User Researcher · Shenzhen
