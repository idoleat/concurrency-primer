# Converting the LaTeX book to mdbook

`concurrency-primer.tex` is the canonical source of the PDF edition.  The web
edition under `src/` is generated from it with pandoc, so it can be
regenerated whenever the paper changes:

```shell
$ tools/convert.sh              # reads concurrency-primer.tex, writes src/
$ mdbook build                  # or: mdbook serve
```

Requirements: pandoc 3 and Python 3 for the conversion, mdbook for the build.
The conversion overwrites every generated chapter under `src/`, so edit
`concurrency-primer.tex` rather than the Markdown.  `src/preprocessors`,
`src/scripts` and `src/styles` are hand-maintained and are left alone.

## Pipeline

| Stage | File | Job |
| --- | --- | --- |
| 1 | `preprocess.py` | Rewrite the book's private LaTeX macros into constructs pandoc already understands. |
| 2 | `mdbook.lua` | A pandoc Lua filter for the rendering choices that only exist in the web edition. |
| 3 | `split.py` | Cut pandoc's single Markdown stream into one file per chapter and write `SUMMARY.md`. |

`convert.sh` runs the three in order and documents the pandoc options it uses.

## Style rules

The PDF leans on typographic distinctions that HTML either lacks or spells
differently.  The conversion resolves them like this:

* `\textit`, `\emph` and `\introduce` all become plain italics.  They render
  identically in the PDF, so there is nothing to preserve.
* ``` ``quoted'' ``` becomes the actual `“quoted”` characters.  `book.toml`
  turns on `smart-punctuation`, and spelling the characters out keeps the
  Markdown and the rendered page in agreement.
* Math is emitted between `\\(`…`\\)` and `\\[`…`\\]`, the delimiters
  `mathjax-support` looks for.
* `\clang{}` and `\cplusplus{}` expand to `C` and `C++`; the version argument
  the LaTeX macros silently discard (`\cplusplus{17}`) is kept, so this reads
  `C++17`.
* `\textsc{}` becomes `<small>` around capital letters, which is as close as
  HTML gets to small caps.
* `\monobox`, `\keyword`, `\texttt`, `\cc` and `\cpp` all become inline code.
* Figures become `<!-- IMAGE PLACEHOLDER: ... -->` comments followed by the
  caption as a blockquote.  The artwork is redrawn by hand for the web
  edition, so the conversion only marks where it goes.
* Side-by-side `minipage` groups become the `:::horizontal` containers that
  `src/preprocessors/div_scope.py` turns into flex containers.
* `\inputminted` becomes an mdbook `{{#include}}`, so the web edition embeds
  the same compilable files under `examples/` that the PDF does.

## Chapter layout

`\section` becomes a top-level chapter and `\subsection` becomes a nested one;
`\subsubsection` stays as a heading inside its chapter.  The mapping from
heading text to file name lives in `CHAPTERS` at the top of `split.py`, which
is also the order of `SUMMARY.md`.  Adding a section to the paper therefore
means adding one line there.

`\label`/`\secref`/`\fig` have no equivalent in a book with no page or figure
numbers.  `preprocess.py` turns them into markers, and `split.py` resolves
them once it knows which chapter each label landed in: a section reference
becomes a link carrying that section's title, and a figure reference becomes a
link to an `<a id>` next to the figure placeholder.

A handful of sentences only make sense alongside LaTeX's figure numbering
("Figure 7 sketches ...").  Those are reworded in `MANUAL_FIXUPS` in
`preprocess.py` rather than in the generated Markdown, so the conversion stays
reproducible.
