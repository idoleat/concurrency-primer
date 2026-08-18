#!/usr/bin/env python3
"""Normalize concurrency-primer.tex into a LaTeX dialect pandoc can read.

pandoc understands plain LaTeX, but not the private macros and minted
wrappers this book defines in its preamble and in lib/codeblock.tex.  Rather
than teaching pandoc about them one by one on the command line, we rewrite
them here into constructs pandoc already knows (\\verb, \\textit, minted,
figure, ...) and leave everything else to tools/mdbook.lua.

Cross references cannot be resolved before the document is split into
chapters, so \\secref/\\fig/\\ref are turned into <<...>> markers that
tools/split.py rewrites into mdbook links.

Usage: preprocess.py <in.tex> <out.tex>
"""

import re
import sys

# --------------------------------------------------------------------------
# Markers understood by tools/split.py.  Guillemets are used because pandoc
# never escapes or reflows them, and they cannot occur in the source text.
# --------------------------------------------------------------------------
SECREF = "\u00abSECREF:{}\u00bb"
FIGREF = "\u00abFIGREF:{}\u00bb"
FIGREF_CAP = "\u00abFIGREFCAP:{}\u00bb"
HORI_OPEN = "\u00abHORI\u00bb"
HORI_CLOSE = "\u00ab/HORI\u00bb"

# The arrow that sits between a C snippet and the assembly it compiles to.
# mdbook renders it with MathJax; see book.toml.
BECOMES_ARROW = r"\[\text{ } \xrightarrow{\textit{becomes}} \text{ }\]"

# --------------------------------------------------------------------------
# Prose that only makes sense with LaTeX's automatic figure numbering.
# mdbook has no numbered figures, so these few spots are reworded here (rather
# than in the generated Markdown) to keep the conversion reproducible.
# --------------------------------------------------------------------------
MANUAL_FIXUPS = [
    # "Figure \ref{x} sketches ..." starts a sentence, so it needs a
    # capitalized replacement that also says where the figure is.
    (r"Figure \ref{hw-seq-cst} sketches", r"\Fig{hw-seq-cst} sketches"),
    (r"Figure \ref{hw-relaxed} sketches", r"\Fig{hw-relaxed} sketches"),
    # \fig{} expands to "the figure", so drop the article the source supplies.
    (r"in the \fig{", r"in \fig{"),
    # Without figure numbers, naming the two figures reads better than two
    # identical "the figure" links.
    (
        r"Also the source of figures \ref{fig:ideal-machine} and \ref{fig:dunnington}.",
        r"Also the source of the idealized multi-core processor and memory "
        r"hierarchy figures.",
    ),
    # ideal-machine.png lives at the repository root; every other figure is
    # under images/.  Normalize so the placeholders are uniform.
    (r"{ideal-machine}", r"{images/ideal-machine}"),
]

# minted/listings wrappers from lib/codeblock.tex -> highlight.js language.
CODE_ENVIRONMENTS = {"ccode": "c", "cppcode": "cpp"}

# Commands whose single argument is verbatim-ish text.
MONO_COMMANDS = ("monobox", "keyword", "texttt", "cc", "cpp", "sh")

# Commands that are dropped, argument and all: (name, number of arguments).
DROP_WITH_ARG = (("setcounter", 2), ("setfootnoterule", 1), ("vspace", 1))

# Commands that are dropped but whose argument is kept.
UNWRAP = ("textup",)

# Bare commands that are simply deleted.
DROP_BARE = (
    "punckern",
    "quotekern",
    "noindent",
    "bigskip",
    "smallskip",
    "medskip",
    "newpage",
    "newline",
    "hfill",
    "appendix",
    "itshape",
    "upshape",
    "small",
    "normalsize",
    "large",
    "Large",
    "codesize",
    "centering",
)


def brace_arg(text, start):
    """Return (argument, index just past it) for the group starting at `start`.

    `text[start]` must be '{'.  Nested groups are handled.
    """
    assert text[start] == "{"
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        i += 1
    raise ValueError("unbalanced braces at offset %d" % start)


def replace_command(text, name, render, nargs=1):
    """Replace every \\<name>{...} (nargs groups) using `render(*args)`."""
    out = []
    i = 0
    pattern = "\\" + name
    while True:
        j = text.find(pattern, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        after = j + len(pattern)
        # Do not match a longer command name that merely starts with `name`.
        if after < len(text) and (text[after].isalpha() or text[after] == "*"):
            out.append(text[i : after])
            i = after
            continue
        args = []
        k = after
        try:
            for _ in range(nargs):
                while k < len(text) and text[k] in " \n":
                    k += 1
                if k >= len(text) or text[k] != "{":
                    raise ValueError
                arg, k = brace_arg(text, k)
                args.append(arg)
        except ValueError:
            out.append(text[i:after])
            i = after
            continue
        out.append(text[i:j])
        out.append(render(*args))
        i = k


def unescape_verbatim(s):
    """Turn LaTeX-escaped text back into the characters it stands for."""
    s = s.replace("\\textbackslash", "\\")
    for ch in "_&#%$~^{}":
        s = s.replace("\\" + ch, ch)
    return s.replace("\\,", "").replace("\\ ", " ")


def verb(s):
    """Wrap `s` in \\verb using a delimiter that does not occur in it."""
    for delim in "|!+/^\u00a7":
        if delim not in s:
            return "\\verb%s%s%s" % (delim, s, delim)
    raise ValueError("no usable \\verb delimiter for %r" % s)


# --------------------------------------------------------------------------
# Step 1: lift code out of the way so later text rewriting cannot touch it.
# --------------------------------------------------------------------------
def extract_code(body):
    """Replace every code block with an @@CODEn@@ marker.

    Returns (body, blocks) where blocks[n] is (language, source).
    """
    blocks = []

    def stash(lang, source):
        blocks.append((lang, source.strip("\n").rstrip()))
        return "\n\n@@CODE%d@@\n\n" % (len(blocks) - 1)

    def dedent(source):
        lines = [ln for ln in source.split("\n") if ln.strip()]
        if not lines:
            return source
        pad = min(len(ln) - len(ln.lstrip(" ")) for ln in lines)
        return "\n".join(ln[pad:] if ln.strip() else ln for ln in source.split("\n"))

    for env, lang in CODE_ENVIRONMENTS.items():
        body = re.sub(
            r"\\begin\{%s\}\n(.*?)\\end\{%s\}" % (env, env),
            lambda m, lang=lang: stash(lang, m.group(1)),
            body,
            flags=re.S,
        )

    # \begin{minted}[options]{lang}; autogobble means "strip common indent".
    def minted(m):
        opts, lang, source = m.group(1) or "", m.group(2), m.group(3)
        if "autogobble" in opts:
            source = dedent(source)
        return stash(lang, source)

    body = re.sub(
        r"\\begin\{minted\}(?:\[([^\]]*)\])?\{(\w+)\}\n(.*?)\\end\{minted\}",
        minted,
        body,
        flags=re.S,
    )

    # listings is only used for Arm assembly and for the plain interleaving
    # tables of the sequential-consistency section.  Its option list nests
    # brackets (language={[ARM]Assembler}), so match to the end of the line.
    def lstlisting(m):
        opts, source = m.group(1) or "", m.group(2)
        lang = "armasm" if "ARM" in opts else "text"
        return stash(lang, source)

    body = re.sub(
        r"\\begin\{lstlisting\}(?:\[([^\n]*)\])?\n(.*?)\\end\{lstlisting\}",
        lstlisting,
        body,
        flags=re.S,
    )

    # \inputminted pulls in a standalone example; mdbook does the same with
    # {{#include}}, which keeps the example a real, compilable file.
    body = re.sub(
        r"\\inputminted\{(\w+)\}\{\./(.*?)\}",
        lambda m: stash(m.group(1), "{{#include @EXAMPLES@/%s}}"
                        % m.group(2).split("/", 1)[-1]),
        body,
    )
    return body, blocks


def restore_code(body, blocks):
    def put(m):
        lang, source = blocks[int(m.group(1))]
        return "\\begin{minted}{%s}\n%s\n\\end{minted}" % (lang, source)

    return re.sub(r"@@CODE(\d+)@@", put, body)


# --------------------------------------------------------------------------
# Step 2: document skeleton.
# --------------------------------------------------------------------------
def extract_body(tex):
    body = tex.split("\\begin{document}", 1)[1]
    return body.split("\\end{document}", 1)[0]


def strip_comments(body):
    """Drop comments (code has already been lifted out).

    A `%` at the end of a line also swallows the newline and the indentation
    that follows it, which is how the source keeps \\href and \\footnote
    arguments readable.
    """
    body = "\n".join(ln for ln in body.split("\n") if not ln.lstrip().startswith("%"))
    return re.sub(r"(?<!\\)%[ \t]*\n[ \t]*", "", body)


def extract_urls(body):
    """Hide \\href and \\url targets from the text rewriting below.

    URLs contain characters that are meaningful in prose (`~`, `%`, ...) but
    must survive verbatim.
    """
    urls = []

    def stash(m):
        urls.append(m.group(2))
        return "%s{@@URL%d@@}" % (m.group(1), len(urls) - 1)

    body = re.sub(r"(\\(?:href|url))\{([^}]*)\}", stash, body)
    return body, urls


def restore_urls(body, urls):
    return re.sub(r"@@URL(\d+)@@", lambda m: urls[int(m.group(1))], body)


def make_abstract_section(body):
    """The title page is hand-built in LaTeX; turn it into a real section."""
    head, rest = body.split("\\section{Background}", 1)
    abstract = head.rsplit("\\noindent", 1)[1]
    return "\\section{Abstract}\n%s\n\\section{Background}%s" % (
        abstract.strip(),
        rest,
    )


# --------------------------------------------------------------------------
# Step 3: macros.
# --------------------------------------------------------------------------
def rewrite_macros(body):
    for old, new in MANUAL_FIXUPS:
        body = body.replace(old, new)

    # Thin spaces are a typesetting detail with no Markdown equivalent.
    body = body.replace("\\,", "")

    # \cplusplus{17} and \clang{11} are declared as taking (and discarding) an
    # argument, so the version number is lost in the PDF.  Keep it here.
    body = replace_command(body, "cplusplus", lambda a: "C++" + a)
    body = replace_command(body, "clang", lambda a: "C" + a)
    body = body.replace("\\csharp", "C\\#")

    # Every flavour of monospace becomes \verb, which pandoc turns into
    # Markdown inline code.
    for name in MONO_COMMANDS:
        body = replace_command(body, name, lambda a: verb(unescape_verbatim(a)))
    # \cc|foo|, \cpp|foo| and friends: the same commands with \verb delimiters.
    body = re.sub(r"\\(?:cc|cpp|sh)([|!+])(.*?)\1", lambda m: verb(m.group(2)), body)

    # \introduce is only ever an italicized new term, and so are \emph and
    # \textit: the PDF renders all three identically.
    body = replace_command(body, "introduce", lambda a: "\\textit{%s}" % a)

    for name in UNWRAP:
        body = replace_command(body, name, lambda a: a)
    for name, nargs in DROP_WITH_ARG:
        body = replace_command(body, name, lambda *a: "", nargs=nargs)
    body = re.sub(r"\\setlength\s*\\?\w+\s*\{[^}]*\}", "", body)

    body = body.replace("~\\textrightarrow~", " \u2192 ")
    body = re.sub(r"\\(?:%s)(?![a-zA-Z])\{?\}?" % "|".join(DROP_BARE), "", body)
    # Non-breaking spaces are a typesetting detail; plain spaces read the same
    # in a browser.
    body = body.replace("~", " ")

    # Cross references are resolved once the chapter layout is known.
    body = replace_command(body, "secref", lambda a: SECREF.format(a))
    body = replace_command(body, "Fig", lambda a: FIGREF_CAP.format(a))
    body = replace_command(body, "fig", lambda a: FIGREF.format(a))
    body = replace_command(body, "ref", lambda a: FIGREF.format(a))
    return body


# --------------------------------------------------------------------------
# Step 4: environments.
# --------------------------------------------------------------------------
def rewrite_environments(body):
    body = re.sub(r"\\(?:begin|end)\{samepage\}", "", body)
    body = re.sub(r"\\begin\{itemize\}\[[^\]]*\]", "\\\\begin{itemize}", body)

    body = convert_captionof_figures(body)
    body = convert_interleaving_table(body)
    body = convert_side_by_side(body)

    body = re.sub(r"\\(?:begin|end)\{center\}", "", body)
    return body


def convert_captionof_figures(body):
    """center + includegraphics + captionof -> a plain figure environment."""
    return re.sub(
        r"\\begin\{center\}\s*"
        r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}\s*"
        r"\\captionof\{figure\}\{(.*?)\}\s*"
        r"(\\label\{[^}]*\})?\s*"
        r"\\end\{center\}",
        lambda m: "\\begin{figure}\n\\includegraphics{%s}\n\\caption{%s}\n%s\n"
        "\\end{figure}" % (m.group(1), m.group(2), m.group(3) or ""),
        body,
        flags=re.S,
    )


def convert_interleaving_table(body):
    """The six-executions table is a 3x2 grid of listings, not real tabular data.

    Markdown tables cannot hold code blocks, so each row becomes one of the
    horizontal containers the book already uses (see src/styles).
    """
    pattern = re.compile(
        r"\\begin\{center\}\s*"
        r"\\begin\{tabular\}\{[^}]*\}\s*\\hline(.*?)\\end\{tabular\}\s*"
        r"\\captionof\{table\}\{(.*?)\}\s*"
        r"\\end\{center\}",
        re.S,
    )

    def convert(m):
        grid, caption = m.group(1), m.group(2)
        out = []
        for row in grid.split("\\\\ \\hline"):
            cells = re.findall(r"@@CODE(\d+)@@", row)
            if not cells:
                continue
            out.append(HORI_OPEN)
            out.extend("@@CODE%s@@" % n for n in cells)
            out.append(HORI_CLOSE)
        out.append("\\begin{quote}\n\\textit{%s}\n\\end{quote}" % caption.strip())
        return "\n\n" + "\n\n".join(out) + "\n\n"

    return pattern.sub(convert, body)


def convert_side_by_side(body):
    """minipage runs (optionally with a tikz arrow) -> horizontal containers."""
    body = re.sub(
        r"\\raisebox\{[^}]*\}\{\s*\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}\s*\}",
        "@@ARROW@@",
        body,
        flags=re.S,
    )

    minipage = r"\\begin\{minipage\}\{[^}]*\}(.*?)\\end\{minipage\}"
    run = re.compile(
        r"(?:%s)(?:\s*(?:@@ARROW@@)?\s*(?:%s))+" % (minipage, minipage), re.S
    )

    def convert(m):
        parts = []
        for chunk in re.split(r"(@@ARROW@@)", m.group(0)):
            if chunk.strip() == "@@ARROW@@":
                parts.append(BECOMES_ARROW)
                continue
            parts.extend(inner.strip() for inner in re.findall(minipage, chunk, re.S))
        # "before -> after" pairs come one after another in the source; each
        # arrow starts a new container so they stack instead of scrolling.
        containers, current = [], []
        for part in parts:
            if part == BECOMES_ARROW and BECOMES_ARROW in current:
                containers.append(current[:-1])
                current = current[-1:]
            current.append(part)
        containers.append(current)
        return "\n\n" + "\n\n".join(
            "\n\n".join([HORI_OPEN] + c + [HORI_CLOSE]) for c in containers
        ) + "\n\n"

    return run.sub(convert, body)


# --------------------------------------------------------------------------
# Step 5: whitespace pandoc cares about.
# --------------------------------------------------------------------------
def tidy(body):
    # pandoc only attaches \label to a heading when the label is followed by a
    # blank line, so make sure it always is.
    body = re.sub(
        r"(\\(?:sub)*section\{.*?\}\n\\label\{[^}]*\})\n(?!\n)", r"\1\n\n", body
    )
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


PREAMBLE = """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage{minted}
\\begin{document}
"""


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as fh:
        tex = fh.read()

    body = extract_body(tex)
    body, blocks = extract_code(body)
    body = strip_comments(body)
    body, urls = extract_urls(body)
    body = make_abstract_section(body)
    body = rewrite_macros(body)
    body = rewrite_environments(body)
    body = restore_urls(body, urls)
    body = restore_code(body, blocks)
    body = tidy(body)

    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(PREAMBLE + body + "\\end{document}\n")


if __name__ == "__main__":
    main()
