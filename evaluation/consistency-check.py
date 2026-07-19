#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user-research-sop consistency check
Python stdlib only, cross-platform.

Usage:
    python evaluation/consistency-check.py              # normal check
    python evaluation/consistency-check.py --regression  # regression tests
"""
import re, sys, tempfile, shutil
from pathlib import Path

# ── Safe output ───────────────────────────────────────────────────────
_U = True
try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8","utf8"):
        import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except: _U = False

def _s(n):
    d = {"pass":"[PASS]","fail":"[FAIL]"} if not _U else {"pass":"\u2705","fail":"\u274c"}
    return d.get(n, n)

# ── Shared ────────────────────────────────────────────────────────────
EXEMPT = ["不得使用","不要使用","不使用","禁止","取消","不支持","Not Currently","不得","不应","不使用固定"]

# Evidence tags that can label numbers (table-level or section-level)
EVID_TAGS = {"[规划假设]","[虚构","[案例中的","规划假设","虚构示意","虚构流程",
             "未独立核验","占位","待验证","来源陈述","案例中的脱敏","案例中的虚构"}
# Whitelist for 【...】 brackets — only these pass
BRACKET_TAGS = {"虚构示意","虚构流程","规划假设","来源陈述","案例中的脱敏","案例中的虚构",
                "待验证","脱敏记录","未独立核验","占位"}

# Number patterns to detect
_NUM_RE = re.compile(
    r'(?:'
    r'\d[\d,]*\.?\d*[%％]'
    r'|\d+(?:\s*[-—]\s*\d+)?\s*(?:分钟|min|天|场|份|家|人|条|步|轮|个)'
    r'|\d+(?:\s*[-—]\s*\d+)?\s*(?:minutes?|days?|weeks?)'
    r'|SLA[（(]\s*≤?\s*\d+'
    r'|\d{4}[-/]\d{2}[-/]\d{2}'         # 2026-07-05
    r'|\d{4}年\d{1,2}月\d{1,2}日'       # 2026年7月5日
    r'|\d{1,2}月\d{1,2}日'              # 7月15日
    r'|\d{1,2}月\d{1,2}日[-—]\d{1,2}月?\d{1,2}日'  # 7月2日-7月10日
    r'|\d[\d,]*\.?\d*'                   # bare numbers
    r')'
)

# Structural tokens to mask (not data)
_STRUCT_TOKENS = [
    # Markdown heading prefix
    re.compile(r'^#+\s*'),
    # Section numbers at heading start: "2.1 ", "4.3.2 "
    re.compile(r'^\d+(?:\.\d+)+\s'),
    # Ordered list number: "1. ", "2. "
    re.compile(r'^\s*\d+\.\s'),
    # Table separator: |---|---|
    re.compile(r'^\|[\s]*[-:]+'),
    # Table ordinal column: | # |
    re.compile(r'^\|[\s]*#\s*\|'),
    # Claim ID
    re.compile(r'Claim\s*ID', re.I),
    # Version numbers
    re.compile(r'V\d+\.\d+'),
    # Stage/Task refs
    re.compile(r'Stage\s+\d+'), re.compile(r'Task\s+\d+'),
    # Score ranges
    re.compile(r'0—2\s*分'), re.compile(r'每项\s*0—2'),
    # Benchmark structure
    re.compile(r'\d+\s*个平台'), re.compile(r'\d+\s*次运行'), re.compile(r'\d+\s*份结果'),
    # Semantic structural counts (not data)
    re.compile(r'\d+条(?:核心发现|要求|建议|原则|规则|维度|检查项|结论|标准|步骤|记录)'),
    re.compile(r'(?:核心发现|结论|建议|要求|规则)[（(]\d+条[)）]'),  # 核心发现（3条）
    re.compile(r'\d+个(?:步骤|维度|阶段|平台|模块|问题|条件)'),
    re.compile(r'第\d+步'),
    re.compile(r'步骤\d+'),
    # File names in backticks
    re.compile(r'`\d+[-—]'), re.compile(r'`\S*\.md`'),
    # Participant IDs
    re.compile(r'P\d+'),
]

def _mask_structural(line):
    """Return line with structural tokens replaced by spaces."""
    masked = line
    for pat in _STRUCT_TOKENS:
        masked = pat.sub(' ', masked)
    return masked

# ── Heading stack for section scope ───────────────────────────────────
class HeadingStack:
    """Track Markdown headings and their evidence labels."""
    def __init__(self):
        self.stack = []  # [(level, label, line_num)]

    def update(self, line, line_num):
        """Process a heading line. Returns the current effective label."""
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if not m:
            return self.current_label()
        level = len(m.group(1))
        heading_text = m.group(2)
        # Find label in heading
        label = None
        for tag in BRACKET_TAGS:
            if tag in heading_text:
                label = tag
                break
        # Also check for定向 declarations in the heading
        if not label:
            bm = re.search(r'【([^】]+)】', heading_text)
            if bm and bm.group(1) in BRACKET_TAGS:
                label = bm.group(1)
        # Pop stack to parent level
        while self.stack and self.stack[-1][0] >= level:
            self.stack.pop()
        # Push new heading
        self.stack.append((level, label, line_num))
        return self.current_label()

    def current_label(self):
        """Get the current effective label (nearest ancestor with a label)."""
        for level, label, _ in reversed(self.stack):
            if label:
                return label
        return None

    def scope_label(self, line_num):
        """Check if line_num is within a labeled section scope."""
        label = self.current_label()
        if label:
            return label
        return None

# ──定向 declarations (file-level) ────────────────────────────────────
定向_RE = re.compile(r'【([^】]+)】')
定向_TARGET_RE = re.compile(r'(?:以下|本[案例节文件]|所有)(?:.*?)(?:【([^】]+)】)')

def _find定向_label(lines, row_idx):
    """Check if there's a定向 declaration that covers this row.
    
    A定向 declaration must:
    1. Be in a blockquote or heading
    2. Explicitly state what it covers (e.g., "以下所有数字", "本节所有比例")
    3. The target must include the current row's context
    """
    line = lines[row_idx]
    
    # Check the line itself for定向
    for tag in BRACKET_TAGS:
        if tag in line:
            return tag
    
    # Check blockquote lines above (within 5 lines)
    for j in range(row_idx - 1, max(row_idx - 5, -1), -1):
        ln = lines[j].strip()
        if not ln.startswith('>') and not ln.startswith('#'):
            # Allow blank lines
            if ln == '' or ln == '>':
                continue
            break  # Non-blockquote, non-heading content found
        for tag in BRACKET_TAGS:
            if tag in ln:
                # Check if the declaration explicitly covers this context
                # Look for "以下", "本节", "本案例", "所有" keywords
                if re.search(r'以下|本[案例节文件]|所有', ln):
                    return tag
                # Or if it's a定向 target like "里程碑日期为【虚构流程示意】"
                tm = re.search(r'为【([^】]+)】', ln)
                if tm and tm.group(1) in BRACKET_TAGS:
                    return tm.group(1)
    
    return None

# ── Table label check ─────────────────────────────────────────────────
def _find_table_label(lines, row_idx):
    """Check if there's a valid EVID_TAGS label on the table header or pre-table line.
    
    Allowed: only EVID_TAGS whitelist.
    Search backward from the table row for a label, allowing one blank line gap.
    """
    # Find the table: look backward for the nearest non-table line
    table_start = row_idx
    for j in range(row_idx - 1, max(row_idx - 5, -1), -1):
        ln = lines[j].strip()
        if ln.startswith('|') and not re.match(r'^\|[\s]*[-:]+', ln):
            table_start = j  # Still in table
        elif ln == '' or ln == '>':
            continue  # Blank line, keep looking
        else:
            break  # Found non-table content
    # Check lines above the table for a label
    for j in range(table_start - 1, max(table_start - 3, -1), -1):
        if j < 0: break
        ln = lines[j].strip()
        if ln == '' or ln == '>':
            continue
        for tag in EVID_TAGS:
            if tag in lines[j]:
                return tag
        bm = re.search(r'【([^】]+)】', lines[j])
        if bm and bm.group(1) in BRACKET_TAGS:
            return bm.group(1)
        break  # Found non-empty, non-label line
    return None

# ── Number has label check ────────────────────────────────────────────
def _number_has_label(lines, row_idx, heading_stack):
    """Check if a number at row_idx has proper evidence labeling.
    
    Scope hierarchy:
    1. Line-level: tag on the same line
    2. Table-level: valid EVID_TAGS on table header or pre-table line
    3. Section-level: heading with scope label (from heading stack)
    4.定向-level:定向 declaration above
    """
    line = lines[row_idx]
    
    # 1. Line-level
    for tag in BRACKET_TAGS:
        if tag in line:
            return tag
    
    # 2. Table-level (only if line is a table row)
    if '|' in line and not re.match(r'^\|[\s]*[-:]+', line.strip()):
        tag = _find_table_label(lines, row_idx)
        if tag:
            return tag
    
    # 3. Section-level (heading stack)
    label = heading_stack.scope_label(row_idx)
    if label:
        return label
    
    # 4.定向-level
    tag = _find定向_label(lines, row_idx)
    if tag:
        return tag
    
    return None

# ── I/O helpers ───────────────────────────────────────────────────────
def read_md(p):
    if not p.exists(): return None, "not found"
    try:
        with open(p, "r", encoding="utf-8") as f: return f.readlines(), None
    except: return None, "not UTF-8"

def txt(root, rel):
    lines, err = read_md(root / rel)
    return "".join(lines) if not err else ""

# ── Checks ────────────────────────────────────────────────────────────
def run_checks(root):
    issues = []
    def add(f, line, rule, desc, rec):
        r = f if isinstance(f, str) else str(f.relative_to(root))
        issues.append((r, line, rule, desc, rec))

    # 1. Links
    for mf in root.rglob("*.md"):
        if ".git" in mf.parts: continue
        lines, err = read_md(mf)
        if err: continue
        for i, line in enumerate(lines, 1):
            for m in re.finditer(r'\[.*?\]\(([^)]+)\)', line):
                link = m.group(1)
                if link.startswith(("http://","https://","mailto:","#")): continue
                lp = link.split("#")[0]
                if lp and not (mf.parent / lp).exists():
                    add(mf, i, "LINK", "broken: "+link, "fix")

    # 2. Modes
    cn = {"快速执行","标准协作","引导教学"}
    en = {"Quick Execution","Standard Collaboration","Guided Learning"}
    cn_p = re.compile(r'(快速执行|标准协作|引导教学)')
    en_p = re.compile(r'(Quick Execution|Standard Collaboration|Guided Learning)')
    for f in ["SKILL.md","PORTABLE.md","README_zh.md"]:
        t = txt(root, f)
        miss = cn - set(m.group() for m in cn_p.finditer(t))
        if miss: add(f, 0, "MODE", "missing: "+str(miss), "add")
    for f in ["README.md","AGENTS.md"]:
        t = txt(root, f)
        miss = en - set(m.group() for m in en_p.finditer(t))
        if miss: add(f, 0, "MODE", "missing: "+str(miss), "add")

    # 3. Thresholds
    tpats = [
        (re.compile(r'每群[>=]\s*50'), "fixed group >=50"),
        (re.compile(r'每群至少\s*50'), "fixed group >=50"),
        (re.compile(r'行业基准回收率\s*[0-9]+[%]'), "fixed recovery rate"),
        (re.compile(r'答题时长\s*[<]\s*1\s*分钟\s*(剔除|移除|过滤)'), "fixed 1-min exclusion"),
        (re.compile(r'问卷总时长\s*[<=]\s*8\s*分钟'), "fixed 8-min cap"),
        (re.compile(r'通用题占比\s*[<=]\s*30[%]'), "fixed 30% ratio"),
        (re.compile(r'差异超过\s*5[%]\s*作为'), "fixed 5% threshold"),
        (re.compile(r'90[%]\s*的用研项目失败'), "unsourced 90%"),
        (re.compile(r'另一个.*模型.*完成.*事实验证'), "AI=fact verification"),
        (re.compile(r'5[—-]8\s*名.*用户.*发现多数'), "fixed 5-8 user"),
        (re.compile(r'多数可用性问题'), "majority claim"),
        (re.compile(r'固定.*研究周期|固定.*测试时长'), "fixed duration"),
        (re.compile(r'暖场\(2min\)\s*→\s*行为回顾\(8min\)'), "fixed interview segments"),
        (re.compile(r'单格样本\s*[<]\s*30'), "cell-N-30"),
        (re.compile(r'高频\+高影响'), "frequency+impact"),
        (re.compile(r'多名参与者复现.*高证据'), "repro=evidence"),
    ]
    for mf in root.rglob("*.md"):
        if ".git" in mf.parts: continue
        rel = mf.relative_to(root)
        if "benchmark" in str(rel).lower():
            t = txt(root, rel)
            if "虚构测试输入" in t: continue
        lines, err = read_md(mf)
        if err: continue
        for i, line in enumerate(lines, 1):
            for pat, desc in tpats:
                if pat.search(line) and not any(kw in line for kw in EXEMPT):
                    add(str(rel), i, "THRESHOLD", desc, "remove")

    # 4. Evidence labels with heading stack + token masking
    edir = root / "examples"
    if edir.exists():
        for mf in sorted(edir.glob("*.md")):
            rel = str(mf.relative_to(root))
            lines, err = read_md(mf)
            if err: continue
            content = "".join(lines)
            # Check for declaration
            if not any(t in content for t in ["数据与证据声明","数据脱敏与标注声明",
                                                "未独立核验","测试输入声明"]):
                add(rel, 0, "EVIDENCE", "missing declaration", "add at top")
            # Build heading stack and scan
            hs = HeadingStack()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Update heading stack on heading lines
                if stripped.startswith('#'):
                    hs.update(stripped, i)
                    # Mask heading prefix and section number, then scan heading text
                    heading_text = re.sub(r'^#+\s*', '', stripped)  # Remove ## prefix
                    heading_text = re.sub(r'^\d+(?:\.\d+)+\s', ' ', heading_text)  # Remove section number (any depth)
                    masked_heading = _mask_structural(heading_text)
                    for m in _NUM_RE.finditer(masked_heading):
                        num = m.group(0)
                        if len(num) <= 1 and not any(c in num for c in ['%','％']):
                            continue
                        label = _number_has_label(lines, i - 1, hs)
                        if not label:
                            add(rel, i, "EVIDENCE", "unlabeled: "+num, "add label")
                    continue
                # Mask structural tokens from the line
                masked = _mask_structural(line)
                # Also mask inline code (backtick content)
                masked = re.sub(r'`[^`]+`', ' ', masked)
                # Also mask Markdown link targets
                masked = re.sub(r'\[.*?\]\([^)]+\)', ' ', masked)
                # Find all numbers in masked line
                for m in _NUM_RE.finditer(masked):
                    num = m.group(0)
                    # Skip very short numbers (likely ordinals in masked context)
                    if len(num) <= 1 and not any(c in num for c in ['%','％']):
                        continue
                    # Check if this position has a label
                    label = _number_has_label(lines, i - 1, hs)
                    if not label:
                        add(rel, i, "EVIDENCE", "unlabeled: "+num, "add label")

    # 5. Benchmark
    blines, err = read_md(root / "evaluation" / "benchmark.md")
    if not err:
        bc = "".join(blines)
        if "待实际运行" not in bc and "未验证" not in bc:
            add("evaluation/benchmark.md", 0, "BENCHMARK", "not marked not-yet-run", "add")
        scoring = re.search(r'## 三.*?## 四', bc, re.DOTALL)
        if scoring:
            dc = len(re.findall(r'^\|\s*\d+\s*\|', scoring.group(0), re.MULTILINE))
        else:
            dc = len(re.findall(r'^\|\s*\d+\s*\|', bc, re.MULTILINE))
        tm = re.search(r'总分\s*(\d+)\s*分', bc)
        if tm and dc:
            st = int(tm.group(1))
            if st != dc * 2:
                add("evaluation/benchmark.md", 0, "BENCHMARK",
                    "dims(%d)*2=%d != %d"%(dc,dc*2,st), "fix")

    # 6. Fences
    for mf in root.rglob("*.md"):
        if ".git" in mf.parts: continue
        lines, err = read_md(mf)
        if err: continue
        op = False; last = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"): op = not op; last = i
        if op: add(mf.relative_to(root), last, "FENCE", "unclosed", "close")

    # 7. Encoding
    for mf in root.rglob("*.md"):
        if ".git" in mf.parts: continue
        try:
            with open(mf, "r", encoding="utf-8") as f: f.read()
        except: add(mf.relative_to(root), 0, "ENCODING", "not UTF-8", "convert")

    # 8. Capability — bidirectional exclusion
    A_METHODS_CN = ["可用性测试","概念测试","原型测试"]
    B_METHODS_CN = ["日记研究","田野民族志","眼动"]

    for f in ["SKILL.md","PORTABLE.md"]:
        t = txt(root, f)
        if not t: continue
        a_match = re.search(r'A\.\s*支持直接执行\s*\|\s*(.+?)(?:\s*\||\n)', t)
        a_methods = set()
        if a_match:
            for m in re.findall(r'(可用性测试|概念测试|原型测试)', a_match.group(1)):
                a_methods.add(m)
        b_match = re.search(r'B\.\s*只能协助.*?\|\s*(.+?)(?:\s*\||\n)', t)
        b_methods = set()
        if b_match:
            for m in re.findall(r'(日记研究|田野民族志|眼动|可用性测试|概念测试|原型测试)', b_match.group(1)):
                b_methods.add(m)
        for m in A_METHODS_CN:
            if m not in a_methods: add(f, 0, "CAPABILITY", "'%s' not in A" % m, "add to A")
            if m in b_methods: add(f, 0, "CAPABILITY", "'%s' in both A and B" % m, "remove from B")
        for m in B_METHODS_CN:
            if m not in b_methods: add(f, 0, "CAPABILITY", "'%s' not in B" % m, "add to B")
            if m in a_methods: add(f, 0, "CAPABILITY", "'%s' in both A and B" % m, "remove from A")

    for f in ["README.md","README_zh.md"]:
        t = txt(root, f)
        if not t: continue
        is_en = "README.md" == f
        sup = re.search(r'(Currently Supported|当前支持).*?(?:Not Currently|当前不支持|$)', t, re.DOTALL)
        nosup = re.search(r'(Not Currently Supported|当前不支持).*?$', t, re.DOTALL)
        if sup:
            st = sup.group(0)
            for cn_m, en_m in [("可用性测试","Usability testing"),
                                ("概念测试","Concept"),("原型测试","Prototype")]:
                variant = en_m if is_en else cn_m
                cn_short = cn_m.replace("测试","")
                if not (en_m.lower() in st.lower() or cn_m in st or cn_short in st):
                    add(f, 0, "CAPABILITY", "'%s' not in supported" % variant, "add")
        if nosup:
            ns = nosup.group(0)
            ns_sec = re.split(r'\n##|\n---|\n### ', ns)[0]
            for cn_m, en_m in [("可用性测试","Usability testing"),
                                ("概念测试","Concept testing"),("原型测试","Prototype testing")]:
                variant = en_m if is_en else cn_m
                if cn_m in ns_sec or en_m.lower() in ns_sec.lower():
                    add(f, 0, "CAPABILITY", "'%s' in NOT-supported (should be A)" % variant, "move to supported")
            for cn_m, en_m in [("眼动","Eye-tracking"),("日记研究","Diary"),("田野民族志","Field ethnography")]:
                variant = en_m if is_en else cn_m
                if cn_m not in ns_sec and en_m.lower() not in ns_sec.lower():
                    add(f, 0, "CAPABILITY", "'%s' not in not-supported" % variant, "add")
            for cn_m, en_m in [("眼动","Eye-tracking"),("日记研究","Diary"),("田野民族志","Field ethnography")]:
                variant = en_m if is_en else cn_m
                if cn_m in st or en_m.lower() in st.lower():
                    add(f, 0, "CAPABILITY", "'%s' in supported (should be B)" % variant, "move to not-supported")

    # 9. Dup headings
    for mf in root.rglob("*.md"):
        if ".git" in mf.parts: continue
        lines, err = read_md(mf)
        if err: continue
        heads = [(i, l.strip()) for i, l in enumerate(lines, 1) if l.startswith("#")]
        for j in range(1, len(heads)):
            if heads[j][1] == heads[j-1][1]:
                add(mf.relative_to(root), heads[j][0], "DUPHEADING", "dup: "+heads[j][1][:60], "fix")

    # 10. Template thresholds
    for d in ["templates", "prompt-templates"]:
        dp = root / d
        if not dp.exists(): continue
        for mf in dp.rglob("*.md"):
            rel = str(mf.relative_to(root))
            lines, err = read_md(mf)
            if err: continue
            for i, line in enumerate(lines, 1):
                for pat, desc in [(re.compile(r'暖场\(2min\)'),"fixed segments"),
                                   (re.compile(r'每个核心问题配1-2个追问'),"fixed probes"),
                                   (re.compile(r'高频\+高影响'),"frequency+impact"),
                                   (re.compile(r'单格样本\s*[<]\s*30'),"cell-N-30"),
                                   (re.compile(r'多名参与者复现.*高'),"repro=evidence")]:
                    if pat.search(line) and not any(kw in line for kw in EXEMPT):
                        add(rel, i, "THRESHOLD", desc, "remove")

    return issues


# ── Normal mode ───────────────────────────────────────────────────────
def main():
    repo = Path(__file__).resolve().parent.parent
    print("=" * 60)
    print("  user-research-sop consistency check")
    print("=" * 60)
    print("  repo: %s" % repo)
    print()

    issues = run_checks(repo)
    by_rule = {}
    for _, _, rule, _, _ in issues:
        by_rule[rule] = by_rule.get(rule, 0) + 1

    check_names = [
        ("LINK","1. Internal links"), ("MODE","2. Execution modes"),
        ("THRESHOLD","3. Thresholds + template thresholds"),
        ("EVIDENCE","4. Evidence labels"), ("BENCHMARK","5. Benchmark structure"),
        ("FENCE","6. Code fence"), ("ENCODING","7. UTF-8 encoding"),
        ("CAPABILITY","8. Capability consistency"), ("DUPHEADING","9. Duplicate headings"),
    ]
    for rp, name in check_names:
        n = sum(v for k, v in by_rule.items() if k.startswith(rp))
        print("  %s %s%s" % (_s("pass" if n==0 else "fail"), name, " (%d)" % n if n else ""))

    print("\n" + "-" * 60)
    print("  Total: %d issues" % len(issues))
    print("-" * 60)

    if not issues:
        print("\n  All checks passed.")
        sys.exit(0)

    by_file = {}
    for fp, ln, rule, desc, rec in issues:
        by_file.setdefault(fp, []).append((ln, rule, desc, rec))
    print()
    for fp in sorted(by_file):
        print("  [FILE] %s" % fp)
        for ln, rule, desc, rec in by_file[fp]:
            print("    [%s] %s: %s" % (rule, "L%d"%ln if ln else "file", desc))
            print("      -> %s" % rec)
        print()
    sys.exit(1)


# ── Regression mode ───────────────────────────────────────────────────
_DECL = "数据与证据声明\n\n"
_FICTION = "虚构流程示意\n\n"
_DEF_SKILL = ("快速执行\n标准协作\n引导教学\n"
              "A. 支持直接执行 | 可用性测试、概念测试、原型测试\n"
              "B. 只能协助 | 日记研究、田野民族志、眼动\n")
_DEF_PORT = _DEF_SKILL
_DEF_README = ("Quick Execution\nStandard Collaboration\nGuided Learning\n"
               "Currently Supported\n| Usability testing | test |\n| Concept/prototype testing | test |\n"
               "Not Currently Supported\n- Eye-tracking\n- Diary studies\n- Field ethnography\n")
_DEF_README_ZH = ("快速执行\n标准协作\n引导教学\n"
                  "当前支持\n| 可用性测试 | test |\n| 概念或原型测试 | test |\n"
                  "当前不支持\n- 眼动\n- 日记研究\n- 田野民族志\n")
_DEF_AGENTS = "Quick Execution\nStandard Collaboration\nGuided Learning\n"
_DEF_BM = "# Benchmark\n> 状态：待实际运行\n\n## 三\n每项 0-2 分，总分 2 分。\n| 1 | test | 0 | 1 | 2 |\n"

def _mk_repo(extra_files, overrides=None):
    tmp = Path(tempfile.mkdtemp())
    for sub in ["examples","templates","prompt-templates","evaluation"]:
        (tmp / sub).mkdir()
    defs = {"SKILL.md":_DEF_SKILL, "PORTABLE.md":_DEF_PORT,
            "README.md":_DEF_README, "README_zh.md":_DEF_README_ZH,
            "AGENTS.md":_DEF_AGENTS}
    if overrides: defs.update(overrides)
    for f, c in defs.items():
        (tmp / f).write_text(c, encoding="utf-8")
    (tmp / "evaluation" / "benchmark.md").write_text(_DEF_BM, encoding="utf-8")
    for p, c in extra_files.items():
        fp = tmp / p; fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(c, encoding="utf-8")
    return tmp

def _find_issue(issues, rule, file_pat=None, desc_pat=None):
    for i in issues:
        if not i[2].startswith(rule): continue
        if file_pat and file_pat.replace("/", "\\") not in i[0].replace("/", "\\"): continue
        if desc_pat and desc_pat not in i[3]: continue
        return True, i
    return False, None

def regression():
    print("=" * 60)
    print("  REGRESSION TESTS")
    print("=" * 60)
    print()
    passed = 0; failed = 0
    E = "examples/test.md"

    def check(desc, files, overrides, rule, should_find,
              expect_file=None, expect_desc=None, expect_line=None):
        nonlocal passed, failed
        tmp = _mk_repo(files, overrides)
        try:
            issues = run_checks(tmp)
            found, issue = _find_issue(issues, rule, expect_file, expect_desc)
            ok = found == should_find
            if ok and should_find and expect_line is not None and issue:
                ok = issue[1] == expect_line
            sym = "pass" if ok else "fail"
            extra = ""
            if not ok and issue:
                extra = " (got L%d: %s)" % (issue[1], issue[3][:40])
            elif not ok and should_find:
                extra = " (no matching issue)"
            print("  %s %s [%s]%s" % (_s(sym), desc, "PASS" if ok else "FAIL", extra))
            if ok: passed += 1
            else: failed += 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # ── Evidence scope (9 original) ──
    check("Declaration but unlabeled 5min -> FAIL",
          {E: _DECL + "| v | 5min | v |\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="5min")
    check("Declaration but unlabeled 5分钟 -> FAIL",
          {E: _DECL + "测试时长5分钟\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="5分钟")
    check("Declaration but unlabeled 20场 -> FAIL",
          {E: _DECL + "| v | 20场 | v |\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="20场")
    check("Declaration but unlabeled body duration -> FAIL",
          {E: _DECL + "执行周期：7-10天\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="7-10天")
    check("Distant declaration (8 lines) -> FAIL",
          {E: _DECL + "\n\n\n\n\n\n\n\n\n| v | 8.8% | v |\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="8.8%")
    check("Table-level label -> PASS",
          {E: _DECL + "虚构示意\n\n| v | 8.8% | v |\n"}, None,
          "EVIDENCE", False)
    check("Section heading with scope -> PASS",
          {E: _DECL + "## 分析结果【虚构流程示意】\n\n| v | 8.8% | v |\n"}, None,
          "EVIDENCE", False)
    check("After scope ends -> FAIL",
          {E: _DECL + "## 分析结果【虚构示意】\n\n| v | 8.8% | v |\n\n## 另一节\n\n| v | 999 | v |\n"},
          None, "EVIDENCE", True, expect_file=E, expect_desc="999")
    check("Regression file has declaration -> tests are valid",
          {E: _DECL + "虚构示意\n\n| v | 100 | v |\n"}, None,
          "EVIDENCE", False)

    # ── Capability (5 original) ──
    check("Usability in A+B -> FAIL",
          {}, {"SKILL.md": "快速执行\n标准协作\n引导教学\n"
               "A. 支持直接执行 | 可用性测试、概念测试\nB. 只能协助 | 可用性测试、日记研究\n"},
          "CAPABILITY", True, expect_desc="both A and B")
    check("Concept in supported+not-supported -> FAIL",
          {}, {"README.md": "Quick Execution\nStandard Collaboration\nGuided Learning\n"
               "Currently Supported\n| Concept testing | test |\n"
               "Not Currently Supported\n- Concept testing\n"},
          "CAPABILITY", True, expect_desc="in supported")
    check("Eye-tracking in supported -> FAIL",
          {}, {"README_zh.md": "快速执行\n标准协作\n引导教学\n"
               "当前支持\n| 可用性测试 | test |\n| 眼动 | test |\n"
               "当前不支持\n- 田野民族志\n"},
          "CAPABILITY", True, expect_desc="in supported")
    check("Diary missing from not-supported -> FAIL",
          {}, {"README_zh.md": "快速执行\n标准协作\n引导教学\n"
               "当前支持\n| 可用性测试 | test |\n"
               "当前不支持\n- 眼动\n"},
          "CAPABILITY", True, expect_desc="not in not-supported")
    check("Correct mutual exclusion -> PASS",
          {}, None, "CAPABILITY", False)

    # ── Thresholds (3 original) ──
    check("cell-N-30 -> FAIL",
          {"prompt-templates/test.md": "单格样本<30的标注\n"}, None,
          "THRESHOLD", True, expect_desc="cell-N-30")
    check("Fixed segments -> FAIL",
          {"prompt-templates/test.md": "暖场(2min) → 行为回顾(8min)\n"}, None,
          "THRESHOLD", True, expect_desc="fixed segments")
    check("Exempted text -> PASS",
          {"prompt-templates/test.md": "不使用固定样本量\n"}, None,
          "THRESHOLD", False)

    # ── NEW: Structural exclusion (10) ──
    check("Heading 2.1 number -> PASS",
          {E: _DECL + "### 2.1 方法选择\n\n内容\n"}, None,
          "EVIDENCE", False)
    check("Inline code path -> PASS",
          {E: _DECL + "用 `prompt-templates/04-数据分析.md`\n"}, None,
          "EVIDENCE", False)
    check("Parent fiction scope covers child -> PASS",
          {E: _DECL + "## 六、分析过程示意【虚构示意】\n\n### 6.1 用户分群\n\n| 定义 | 数字 |\n| 每周使用 | 3次 |\n"},
          None, "EVIDENCE", False)
    check("Unlabeled 5分钟 in list -> FAIL",
          {E: _DECL + "- 测试时长5分钟\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="5分钟")
    check("Unlabeled 20场 in blockquote list -> FAIL",
          {E: _DECL + "> - 访谈20场\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="20场")
    check("【注意】 not valid tag -> FAIL",
          {E: _DECL + "【注意】\n\n| v | 8.8% | v |\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="8.8%")
    check("Valid table tag with 1 blank line -> PASS",
          {E: _DECL + "虚构示意\n\n| v | 8.8% | v |\n"}, None,
          "EVIDENCE", False)
    check("Multi-number line: struct OK, data FAIL",
          {E: _DECL + "## 2.1 章节\n\n访谈20场\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="20场")
    check("定向 declaration covers milestone -> PASS",
          {E: _DECL + "里程碑日期为【虚构流程示意】\n\n| 节点 | 日期 |\n| 设计 | 7月1日 |\n"},
          None, "EVIDENCE", False)
    check("Line-level tag -> PASS",
          {E: _DECL + "| v | 8.8%【虚构示意】 | v |\n"}, None,
          "EVIDENCE", False)

    # ── NEW: 8 additional tests (semantic counts, dates, heading scan) ──
    # 1. Heading with unlabeled duration -> FAIL
    check("Heading with unlabeled 5分钟 -> FAIL",
          {E: _DECL + "## 测试时长5分钟\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="5分钟")

    # 2. Heading with label -> PASS
    check("Heading with label 5分钟 -> PASS",
          {E: _DECL + "## 测试时长5分钟【规划假设】\n"}, None,
          "EVIDENCE", False)

    # 3. Semantic count "211000条客服会话" -> FAIL (not exempted)
    check("211000条客服会话 -> FAIL",
          {E: _DECL + "211000条客服会话\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="211000")

    # 4. "3个用户分群" -> FAIL (not exempted)
    check("3个用户分群 -> FAIL",
          {E: _DECL + "3个用户分群\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="3")

    # 5. Unlabeled date "7月15日" -> FAIL
    check("Unlabeled 7月15日 -> FAIL",
          {E: _DECL + "| 节点 | 日期 |\n| 投放 | 7月15日 |\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="7月15日")

    # 6. Date under fiction scope -> PASS
    check("Date under fiction scope -> PASS",
          {E: _DECL + "## 里程碑【虚构流程示意】\n\n| 节点 | 日期 |\n| 投放 | 7月15日 |\n"},
          None, "EVIDENCE", False)

    # 7. "第2步访谈20场": report 20场, NOT 2步
    issues_7 = []
    tmp7 = _mk_repo({E: _DECL + "第2步访谈20场\n"}, None)
    try:
        issues_7 = run_checks(tmp7)
    finally:
        shutil.rmtree(tmp7, ignore_errors=True)
    has_20场 = any("20" in i[3] and "EVIDENCE" in i[2] for i in issues_7)
    has_2步 = any("2步" in i[3] for i in issues_7)
    ok7 = has_20场 and not has_2步
    sym7 = "pass" if ok7 else "fail"
    print("  %s 第2步访谈20场: report 20场 not 2步 [%s]" % (_s(sym7), "PASS" if ok7 else "FAIL"))
    if ok7: passed += 1
    else: failed += 1

    # 8. "3条核心发现" -> PASS (semantic structural count)
    check("3条核心发现 -> PASS",
          {E: _DECL + "3条核心发现\n"}, None,
          "EVIDENCE", False)

    # 9. "共211000条客服记录" -> FAIL (not exempted)
    check("共211000条客服记录 -> FAIL",
          {E: _DECL + "共211000条客服记录\n"}, None,
          "EVIDENCE", True, expect_file=E, expect_desc="211000")

    # 10. "### 4.3.2 分析方法" -> PASS (multi-level section number masked)
    check("Multi-level heading 4.3.2 -> PASS",
          {E: _DECL + "### 4.3.2 分析方法\n"}, None,
          "EVIDENCE", False)

    print("\n  Result: %d/%d passed" % (passed, passed + failed))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    regression() if "--regression" in sys.argv else main()
