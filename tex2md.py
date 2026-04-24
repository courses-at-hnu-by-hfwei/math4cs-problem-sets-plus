#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tex2md.py

Convert the main content (title + sections) of `problems.tex` to Markdown
and write the result to `README.md`.

This is a lightweight, dependency-free converter tailored for the simple
structure used in `problems.tex` (sections, itemize/enumerate, href/url,
footnotes, simple inline macros). It does not require pandoc.
"""
from pathlib import Path
import re
import sys


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def extract_title(tex: str) -> str | None:
    m = re.search(r"\\title\{([^}]*)\}", tex)
    return m.group(1).strip() if m else None


def extract_document_body(tex: str) -> str:
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", tex, re.S)
    if m:
        body = m.group(1)
    else:
        body = tex
    # drop \maketitle if present
    body = re.sub(r"\\maketitle", "", body)
    return body.strip()


def remove_comments(s: str) -> str:
    # Remove LaTeX comments (lines starting with %)
    return re.sub(r"(?m)^%.*\n?", "", s)


def convert_inline(s: str) -> str:
    # Convert common LaTeX inline macros used in problems.tex
    s = re.sub(r"\\href\{([^}]*)\}\{([^}]*)\}", r"[\2](\1)", s)
    s = re.sub(r"\\url\{([^}]*)\}", r"<\1>", s)
    s = re.sub(r"\\textcolor\{[^}]*\}\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\footnote\{([^}]*)\}", r" (注: \1)", s)
    s = s.replace("~", " ")
    s = s.replace("\\%", "%")
    # simple commands: \emph, \textbf, \label -> keep inner text
    s = re.sub(r"\\(?:emph|textbf|textit|label)\{([^}]*)\}", r"\1", s)
    # remove leftover braces used for grouping
    s = s.replace("{", "").replace("}", "")
    # collapse multiple spaces
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def convert_item_blocks(s: str) -> str:
    # itemize
    def repl_itemize(m: re.Match) -> str:
        inner = m.group(1)
        parts = re.split(r"\\item", inner)
        items = [p.strip() for p in parts if p.strip()]
        return "\n".join(f"- {convert_inline(it)}" for it in items)

    s = re.sub(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", repl_itemize, s, flags=re.S)

    # enumerate (allow optional argument like [(1)])
    def repl_enumerate(m: re.Match) -> str:
        inner = m.group(1)
        parts = re.split(r"\\item", inner)
        items = [p.strip() for p in parts if p.strip()]
        return "\n".join(f"{i+1}. {convert_inline(it)}" for i, it in enumerate(items))

    s = re.sub(r"\\begin\{enumerate\}(?:\[[^\]]*\])?(.*?)\\end\{enumerate\}", repl_enumerate, s, flags=re.S)
    return s


def convert_sections(s: str) -> str:
    # section and section* -> headers (use level 2; top-level title will be level 1)
    def repl_section(m: re.Match) -> str:
        title = convert_inline(m.group(1))
        return f"\n\n## {title}\n\n"

    s = re.sub(r"\\section\*?\{([^}]*)\}", repl_section, s)
    return s


def cleanup(s: str) -> str:
    # remove leftover simple LaTeX commands
    s = re.sub(r"\\begin\{.*?\}|\\end\{.*?\}", "", s)
    s = re.sub(r"\\[A-Za-z]+", "", s)
    # normalize blank lines
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def tex_to_markdown(tex_path: Path) -> str:
    tex = read_text(tex_path)
    title = extract_title(tex)
    body = extract_document_body(tex)
    body = remove_comments(body)
    body = convert_inline(body)
    body = convert_item_blocks(body)
    body = convert_sections(body)
    body = cleanup(body)

    md_parts = []
    if title:
        md_parts.append(f"# {title}\n")
    md_parts.append(body)
    return "\n".join(p for p in md_parts if p).strip() + "\n"


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    tex_path = repo_root / "problems.tex"
    if not tex_path.exists():
        print(f"Error: {tex_path} not found", file=sys.stderr)
        return 2

    md = tex_to_markdown(tex_path)
    readme_path = repo_root / "README.md"
    write_text(readme_path, md)
    print(f"Wrote {readme_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
