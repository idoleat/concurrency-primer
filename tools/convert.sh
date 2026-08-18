#!/bin/sh
# Regenerate the mdbook sources under src/ from concurrency-primer.tex.
#
#   tools/convert.sh [book.tex] [src-dir]
#
# The conversion runs in three stages:
#
#   1. tools/preprocess.py rewrites the book's private LaTeX macros into
#      constructs pandoc understands.
#   2. pandoc converts LaTeX to Markdown, with tools/mdbook.lua handling the
#      rendering decisions that only make sense for the web edition.
#   3. tools/split.py cuts the result into one file per chapter and writes
#      SUMMARY.md.
#
# Requires pandoc 3 and Python 3.

set -eu

TEX=${1:-concurrency-primer.tex}
SRC=${2:-src}
TOOLS=$(dirname "$0")
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

python3 "$TOOLS/preprocess.py" "$TEX" "$WORK/book.tex"

# --auto_identifiers keeps pandoc from inventing heading ids, so the only ids
# in the AST are the ones \label put there.
# --wrap=preserve keeps the source's one-sentence-per-line layout, which makes
# the generated Markdown reviewable in diffs.
# --reference-location=section keeps each footnote in the section that cites
# it, so splitting the stream does not separate a note from its reference.
# +smart on the writer keeps the Markdown in ASCII: ``...'' becomes "..." and
# an em dash becomes ---.  book.toml's smart-punctuation option is what turns
# those back into real quotes and dashes when the book is rendered, so the
# generated sources stay as typeable as hand-written Markdown.
pandoc \
    --from=latex-auto_identifiers \
    --to=markdown+smart-raw_attribute \
    --lua-filter="$TOOLS/mdbook.lua" \
    --markdown-headings=atx \
    --wrap=preserve \
    --reference-location=section \
    --output="$WORK/book.md" \
    "$WORK/book.tex"

python3 "$TOOLS/split.py" "$WORK/book.md" "$SRC"
