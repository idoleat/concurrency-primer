#!/usr/bin/env python3
"""Split the converted Markdown into an mdbook src/ tree.

pandoc emits one Markdown stream; mdbook wants one file per chapter plus a
SUMMARY.md.  This script cuts the stream at its level 1 and 2 headings, which
correspond to the LaTeX \\section and \\subsection commands, and resolves the
cross-reference markers left behind by tools/preprocess.py.

Usage: split.py <book.md> <src-dir>
"""

import os
import re
import shutil
import sys

# --------------------------------------------------------------------------
# Chapter layout.  Keyed by the normalized heading text (see normalize()), so
# that inline code and <small> markup in a heading do not have to be repeated
# here.  The order of this list is the order of SUMMARY.md.
# --------------------------------------------------------------------------
CHAPTERS = [
    ("abstract", "abstract.md"),
    ("background", "background.md"),
    ("enforcing law and order", "enforcing_law_and_order.md"),
    ("atomicity", "atomicity.md"),
    ('arbitrarily-sized "atomic" types', "Arbitrarily-sized_atomic_types.md"),
    ("read-modify-write", "read-modify-write.md"),
    ("exchange", "read-modify-write/exchange.md"),
    ("test and set", "read-modify-write/test_and_set.md"),
    ("fetch and...", "read-modify-write/fetch_and.md"),
    ("compare and swap", "read-modify-write/compare_and_swap.md"),
    ("example", "read-modify-write/example.md"),
    ("further improvements", "read-modify-write/further_improvements.md"),
    ("shared resources", "shared_resources.md"),
    (
        "concurrency tools and synchronization mechanisms",
        "concurrency_tools.md",
    ),
    ("lock-free", "lock-free.md"),
    ("type of progress", "lock-free/type_of_progress.md"),
    ("spmc solution - lock-based", "lock-free/spmc_lock-based.md"),
    (
        "spmc solution - lock-based and lock-free",
        "lock-free/spmc_lock-based_and_lock-free.md",
    ),
    ("spmc solution - fully lock-free", "lock-free/spmc_fully_lock-free.md"),
    (
        "spmc solution - fully lock-free with cas",
        "lock-free/spmc_fully_lock-free_with_cas.md",
    ),
    ("conclusion on lock-free programming", "lock-free/conclusion.md"),
    ("aba problem", "lock-free/aba_problem.md"),
    (
        "sequential consistency on weakly-ordered hardware",
        "seq_cst_on_weakly_ordered_hw.md",
    ),
    (
        "implementing atomic read-modify-write operations with ll/sc instructions",
        "rmw_with_ll-sc.md",
    ),
    ("spurious ll/sc failures", "rmw_with_ll-sc/spurious_ll-sc_failures.md"),
    (
        "do we always need sequentially consistent operations?",
        "do_we_always_need_seq-cst.md",
    ),
    ("memory orderings", "memory_orderings.md"),
    ("memory consistency models", "memory_ordering/memory_consistency_models.md"),
    ("c11/c++11 atomics", "memory_ordering/c11_cpp11_atomics.md"),
    ("hc svnt dracones", "memory_ordering/hc_svnt_dracones.md"),
    ("hardware convergence", "hardware_convergence.md"),
    (
        "if concurrency is the question, volatile is not the answer.",
        "volatile.md",
    ),
    ("atomic fusion", "atomic_fusion.md"),
    ("takeaways", "takeaways.md"),
    ("additional resources", "additional_resources.md"),
    ("contributing", "contributing.md"),
]
CHAPTER_FILES = dict(CHAPTERS)

# The abstract doubles as the book's landing page, so it keeps the title,
# byline and the release-time placeholder filled in by the add_release_time
# preprocessor.
ABSTRACT_HEADER = """{{#title Concurrency Primer}}
# Concurrency Primer <small><small><small>[^title]</small></small></small>
Matt Kline and Ching-Chun (Jim) Huang\x20\x20
<!--AddTimeHere-->

## Abstract
"""
ABSTRACT_FOOTER = """
[^title]: The original title was *"What every systems programmer should know \
about concurrency"*.
"""

# Where the compilable examples live, relative to the book's src directory.
EXAMPLES_DIR = "examples"

HEADING = re.compile(r"^(#{1,6}) (.*)$")
LABEL_MARKER = re.compile("\u00abLABEL:(.*?)\u00bb")
ANCHOR = re.compile(r'<a id="(.*?)"></a>')
SECREF = re.compile("\u00abSECREF:(.*?)\u00bb")
FIGREF = re.compile("\u00ab(FIGREF|FIGREFCAP):(.*?)\u00bb")
FOOTNOTE = re.compile(r"\[\^(\d+)\]")


def normalize(title):
    """Reduce a rendered heading to a stable dictionary key.

    Punctuation is folded back to ASCII so the keys below do not depend on
    whether pandoc spelled out smart punctuation or left it for mdbook.
    """
    title = re.sub(r"<[^>]+>", "", title)
    title = title.replace("`", "")
    for fancy, plain in (("\u201c", '"'), ("\u201d", '"'), ("\u2019", "'"),
                         ("\u2018", "'"), ("\u2026", "..."),
                         ("\u2014", "---"), ("\u2013", "--")):
        title = title.replace(fancy, plain)
    return re.sub(r"\s+", " ", title).strip().lower()


def split_chapters(text):
    """Cut the stream at every level 1 or 2 heading."""
    chapters, current = [], None
    for line in text.split("\n"):
        m = HEADING.match(line)
        if m and len(m.group(1)) <= 2:
            current = {
                "level": len(m.group(1)),
                "title": m.group(2).strip(),
                "lines": [],
            }
            chapters.append(current)
        elif current is not None:
            current["lines"].append(line)
        elif line.strip():
            raise SystemExit("content before the first heading: %r" % line)
    for chapter in chapters:
        key = normalize(chapter["title"])
        if key not in CHAPTER_FILES:
            raise SystemExit("no file mapped for heading %r" % chapter["title"])
        chapter["path"] = CHAPTER_FILES[key]
        chapter["body"] = "\n".join(chapter["lines"]).strip("\n")
    return chapters


def collect_labels(chapters):
    """Map every \\label to the chapter holding it.

    A label attached to the chapter's own heading links to the page itself; any
    other label got an <a id> anchor from the Lua filter and links to it.
    """
    labels = {}
    for chapter in chapters:
        head = chapter["body"].lstrip("\n").split("\n\n", 1)[0]
        for label in LABEL_MARKER.findall(chapter["body"]):
            anchor = label not in head
            labels[label] = (chapter, anchor)
        for label in ANCHOR.findall(chapter["body"]):
            labels[label] = (chapter, True)
    return labels


def link(source, target, anchor, label):
    """Build an mdbook-relative link from one chapter to another."""
    fragment = "#" + label if anchor else ""
    if source["path"] == target["path"]:
        return fragment or None
    href = os.path.relpath(target["path"], os.path.dirname(source["path"]))
    if not href.startswith("."):
        href = "./" + href
    return href[: -len(".md")] + ".html" + fragment


def resolve_references(chapter, labels):
    body = chapter["body"]

    def secref(m):
        label = m.group(1)
        target, anchor = labels[label]
        href = link(chapter, target, anchor, label)
        title = re.sub(r"\s*\[\^\d+\]", "", target["title"])
        return "[%s](%s)" % (title, href) if href else "*%s*" % title

    def figref(m):
        kind, label = m.group(1), m.group(2)
        target, anchor = labels[label]
        href = link(chapter, target, anchor, label)
        text = "The figure above" if kind == "FIGREFCAP" else "the figure"
        return "[%s](%s)" % (text, href) if href else text

    body = SECREF.sub(secref, body)
    body = FIGREF.sub(figref, body)
    return body


def renumber_footnotes(body):
    """pandoc numbers footnotes document-wide; restart at 1 in every chapter."""
    order, mapping = [], {}
    for number in FOOTNOTE.findall(body):
        if number not in mapping:
            mapping[number] = str(len(order) + 1)
            order.append(number)
    return FOOTNOTE.sub(lambda m: "[^%s]" % mapping[m.group(1)], body)


def finalize(chapter, labels):
    body = resolve_references(chapter, labels)
    body = LABEL_MARKER.sub("", body)

    depth = chapter["path"].count("/")
    body = body.replace("@EXAMPLES@", "../" * (depth + 1) + EXAMPLES_DIR)
    body = body.replace("\u00abHORI\u00bb", ":::horizontal")
    body = body.replace("\u00ab/HORI\u00bb", ":::")

    if chapter["level"] == 2:
        # A subsection becomes a page of its own, so its headings move up one
        # level and its own heading becomes the page title.
        body = re.sub(r"^(#+) ", lambda m: m.group(1)[1:] + " ", body, flags=re.M)

    body = renumber_footnotes(body)
    # pandoc writes "``` c"; drop the space so the fences match the rest of the
    # book and any Markdown tooling that expects a bare info string.
    body = re.sub(r"^(\s*)``` (\S+)$", r"\1```\2", body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body).strip("\n")

    if chapter["path"] == "abstract.md":
        return ABSTRACT_HEADER + body + "\n" + ABSTRACT_FOOTER
    return "# %s\n\n%s\n" % (chapter["title"], body)


def write_summary(chapters, src):
    lines = ["# Summary", ""]
    for chapter in chapters:
        if chapter["path"] == "abstract.md":
            lines.append("[Abstract](./abstract.md)")
            continue
        indent = "  " * (chapter["level"] - 1)
        lines.append(
            "%s- [%s](./%s)" % (indent, chapter["title"], chapter["path"])
        )
    with open(os.path.join(src, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    book, src = sys.argv[1], sys.argv[2]
    with open(book, encoding="utf-8") as fh:
        chapters = split_chapters(fh.read())

    labels = collect_labels(chapters)

    for stale in ("SUMMARY.md",):
        path = os.path.join(src, stale)
        if os.path.exists(path):
            os.remove(path)
    for directory in {os.path.dirname(c["path"]) for c in chapters if "/" in c["path"]}:
        shutil.rmtree(os.path.join(src, directory), ignore_errors=True)

    for chapter in chapters:
        path = os.path.join(src, chapter["path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(finalize(chapter, labels))

    write_summary(chapters, src)
    print("wrote %d chapters to %s" % (len(chapters), src))


if __name__ == "__main__":
    main()
