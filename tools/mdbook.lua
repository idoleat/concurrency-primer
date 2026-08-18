--- Pandoc filter: LaTeX AST -> the Markdown dialect mdbook expects.
---
--- Everything here is a rendering decision that has no LaTeX equivalent, so it
--- belongs in the AST rather than in tools/preprocess.py:
---
---   * \textsc{}  -> <small>CAPITALS</small> (small caps have no Markdown form)
---   * $x$, \[x\] -> \\(x\\) and \\[x\\], the delimiters mdbook's
---                   mathjax-support option looks for
---   * figures    -> a placeholder comment plus the caption as a blockquote
---   * \label{}   -> an explicit <a id> anchor, or a marker for split.py
---
--- See `man pandoc`, section "Custom writers"/"Lua filters", for the API.

local LABEL_MARKER = "\u{ab}LABEL:%s\u{bb}"

--- Small caps: uppercase the letters and mark them up with <small>, which is
--- as close as HTML gets without a dedicated font.
function SmallCaps(el)
  local text = pandoc.utils.stringify(el.content):upper()
  return pandoc.RawInline("html", "<small>" .. text .. "</small>")
end

--- mdbook only recognizes math between \\( \\) and \\[ \\].
function Math(el)
  local open, close = "\\\\(", "\\\\)"
  if el.mathtype == "DisplayMath" then
    open, close = "\\\\[", "\\\\]"
  end
  return pandoc.RawInline("markdown", open .. el.text .. close)
end

--- LaTeX's ~ is a typesetting hint; a browser wraps well enough without it.
function Str(el)
  local text = el.text:gsub("\u{a0}", " ")
  if text ~= el.text then
    return pandoc.Str(text)
  end
end

--- \label{} in running text arrives as an empty span carrying an identifier.
--- Spans with no identifier (\textup, ...) are just unwrapped.
function Span(el)
  if el.identifier ~= "" and #el.content == 0 then
    return pandoc.RawInline("html", '<a id="' .. el.identifier .. '"></a>')
  end
  if el.identifier == "" then
    return el.content
  end
end

--- Section labels: emit a marker split.py can map to the chapter file, then
--- drop the identifier so no `{#id}` attribute leaks into the Markdown.
function Header(el)
  if el.identifier == "" then
    return nil
  end
  local marker = pandoc.RawBlock("markdown", LABEL_MARKER:format(el.identifier))
  el.identifier = ""
  return { el, marker }
end

--- Figures are left for the reader to redraw, so emit a placeholder naming the
--- source file and keep the caption as an italic blockquote, which is how the
--- existing mdbook edition presents figure captions.
local function figure_blocks(path, identifier, caption)
  local head = ""
  if identifier ~= "" then
    head = '<a id="' .. identifier .. '"></a>\n'
  end
  path = path:gsub("%.pdf$", ""):gsub("%.png$", "")
  local blocks = {
    pandoc.RawBlock("markdown", head .. "<!-- IMAGE PLACEHOLDER: " .. path .. " -->"),
  }
  if caption and #caption > 0 then
    blocks[#blocks + 1] = pandoc.BlockQuote({ pandoc.Para({ pandoc.Emph(caption) }) })
  end
  return blocks
end

function Figure(el)
  local image
  el:walk({ Image = function(img) image = image or img end })
  if not image then
    return nil
  end
  local identifier = el.identifier ~= "" and el.identifier or image.identifier
  return figure_blocks(image.src, identifier, el.caption.long[1] and
    el.caption.long[1].content or {})
end

--- A bare \includegraphics (no figure environment) becomes Para{Image}.
function Para(el)
  if #el.content == 1 and el.content[1].t == "Image" then
    local image = el.content[1]
    return figure_blocks(image.src, image.identifier, image.caption)
  end
end

return {
  { Figure = Figure, Para = Para },
  { SmallCaps = SmallCaps, Math = Math, Str = Str, Span = Span, Header = Header },
}
