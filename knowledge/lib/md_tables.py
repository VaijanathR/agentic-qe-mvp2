"""
Generic, deterministic markdown-table + section extraction.

No LLM involvement. This module only knows how to read the two SRS
markdown files structurally (headings, tables, prose between them) — it
has no opinion about requirements content and fabricates nothing: every
value it produces is copied verbatim from the source file.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

ID_FULL_RE = re.compile(r"^(REQ-[A-Z]+-\d+|NEG-\d+|[A-Z]+-OQ-\d+|J-\d+)$")
ID_INLINE_RE = re.compile(r"\b(REQ-[A-Z]+-\d+|NEG-\d+|[A-Z]+-OQ-\d+|J-\d+)\b")
RANGE_RE = re.compile(r"([A-Z]+(?:-[A-Z]+)*-)(\d+)…(\d+)")

H2_RE = re.compile(r"^##\s+(\d+)\.\s+(.*\S)\s*$")
H3_RE = re.compile(r"^###\s+(\d+\.\d+)\s+(.*\S)\s*$")


def strip_md(text: str) -> str:
    """Strip the lightweight markdown emphasis wrapping a whole cell/line
    (leading/trailing ** or `) without touching mid-text formatting."""
    t = text.strip()
    while len(t) >= 2 and t[:2] == "**" and t[-2:] == "**":
        t = t[2:-2].strip()
    t = t.strip("`").strip()
    return t


def split_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_separator_row(cells: List[str]) -> bool:
    return all(re.fullmatch(r":?-{1,}:?", c) for c in cells if c != "")


def expand_ids(cell_text: str) -> List[str]:
    """Expand ellipsis ranges (e.g. 'REQ-REG-01…05') and pick up any
    standalone IDs in the same cell, preserving order, de-duplicated."""
    ids: List[str] = []
    spans = []
    for m in RANGE_RE.finditer(cell_text):
        prefix, start, end = m.groups()
        width = len(start)
        for n in range(int(start), int(end) + 1):
            ids.append(f"{prefix}{str(n).zfill(width)}")
        spans.append(m.span())
    remaining = cell_text
    for s, e in sorted(spans, reverse=True):
        remaining = remaining[:s] + " " + remaining[e:]
    for m in ID_INLINE_RE.finditer(remaining):
        ids.append(m.group(1))
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


@dataclass
class Section:
    section_id: str
    title: str
    level: int
    start_line: int
    end_line: int = -1


@dataclass
class Table:
    section_id: str
    header: List[str]
    rows: List[List[str]]
    start_line: int
    end_line: int


@dataclass
class Prose:
    section_id: str
    text: str
    start_line: int
    end_line: int


def parse_sections(lines: List[str]) -> List[Section]:
    sections: List[Section] = []
    for i, line in enumerate(lines):
        m2 = H2_RE.match(line)
        m3 = H3_RE.match(line)
        if m2:
            sections.append(Section(section_id=m2.group(1), title=m2.group(2), level=2, start_line=i))
        elif m3:
            sections.append(Section(section_id=m3.group(1), title=m3.group(2), level=3, start_line=i))
    for idx, s in enumerate(sections):
        s.end_line = sections[idx + 1].start_line if idx + 1 < len(sections) else len(lines)
    return sections


def section_for_line(sections: List[Section], line_no: int) -> Optional[Section]:
    best = None
    for s in sections:
        if s.start_line <= line_no < s.end_line:
            if best is None or s.level >= best.level:
                best = s
    return best


def parse_tables(lines: List[str], sections: List[Section]) -> List[Table]:
    tables: List[Table] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < n:
            header = split_row(line)
            sep = split_row(lines[i + 1])
            if lines[i + 1].strip().startswith("|") and is_separator_row(sep):
                rows = []
                j = i + 2
                while j < n and lines[j].strip().startswith("|"):
                    rows.append(split_row(lines[j]))
                    j += 1
                sec = section_for_line(sections, i)
                tables.append(
                    Table(
                        section_id=sec.section_id if sec else "",
                        header=header,
                        rows=rows,
                        start_line=i,
                        end_line=j,
                    )
                )
                i = j
                continue
        i += 1
    return tables


def table_to_items(table: Table) -> List[Dict[str, str]]:
    """Auto-detects orientation (standard row-per-item vs. transposed
    field-per-row) and returns a list of {"_id": ..., field: value, ...}.
    """
    header = table.header
    items: List[Dict[str, str]] = []
    if (
        len(header) > 1
        and strip_md(header[0]) == "Field"
        and all(ID_FULL_RE.match(strip_md(h)) for h in header[1:])
    ):
        ids = [strip_md(h) for h in header[1:]]
        per_id_fields: List[Dict[str, str]] = [dict() for _ in ids]
        for row in table.rows:
            if not row or not row[0].strip():
                continue
            field_name = strip_md(row[0])
            for col_idx in range(len(ids)):
                value = row[col_idx + 1] if col_idx + 1 < len(row) else ""
                per_id_fields[col_idx][field_name] = value
        for _id, fields in zip(ids, per_id_fields):
            fields["_id"] = _id
            items.append(fields)
    else:
        labels = [strip_md(h) for h in header]
        for row in table.rows:
            if not row or not row[0].strip():
                continue
            item = {labels[k]: (row[k] if k < len(row) else "") for k in range(len(labels))}
            item["_id"] = strip_md(row[0])
            items.append(item)
    return items


def extract_prose_blocks(lines: List[str], sections: List[Section], tables: List[Table]) -> List[Prose]:
    """Prose = lines within a section that are not part of any table and
    not blank/heading-only. Grouped into contiguous blocks."""
    occupied = set()
    for t in tables:
        for k in range(t.start_line, t.end_line):
            occupied.add(k)
    heading_lines = {s.start_line for s in sections}

    blocks: List[Prose] = []
    for sec in sections:
        buf: List[str] = []
        buf_start = None
        for ln in range(sec.start_line + 1, sec.end_line):
            if ln in occupied or ln in heading_lines:
                if buf:
                    text = "\n".join(buf).strip()
                    if text:
                        blocks.append(Prose(sec.section_id, text, buf_start, ln))
                    buf = []
                    buf_start = None
                continue
            line = lines[ln]
            if line.strip() == "" and not buf:
                continue
            if line.strip() == "---":
                continue
            if buf_start is None:
                buf_start = ln
            buf.append(line)
        if buf:
            text = "\n".join(buf).strip()
            if text:
                blocks.append(Prose(sec.section_id, text, buf_start, sec.end_line))
    return blocks
