# Copyright © Boost Organization <boost@boost.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from weblate.utils.quickbook import (
    _find_bracket_end,
    _parse_bracket_keyword,
    _parse_qbk,
    po_to_qbk,
    qbk_to_po,
)


def test_find_bracket_end_nested() -> None:
    text = "[outer [inner] tail]"
    end = _find_bracket_end(text, 0)
    assert end == len(text) - 1


def test_find_bracket_end_triple_quote() -> None:
    text = "['''[not closed]''']"
    end = _find_bracket_end(text, 0)
    assert end == len(text) - 1


def test_parse_bracket_keyword_section_with_id() -> None:
    block = "[section:myid Title here]"
    kw, off = _parse_bracket_keyword(block)
    assert kw == "section"
    assert block[off:-1].lstrip() == "Title here"


def test_skip_include_and_parse_heading() -> None:
    qbk = "[include other.qbk]\n\n[h1 Title]\n"
    segs = _parse_qbk(qbk)
    assert len(segs) == 1
    assert segs[0].msgid == "Title"
    assert segs[0].seg_type == "heading"


def test_paragraph_soft_wrap_joined() -> None:
    qbk = "One line\ncontinued here.\n"
    segs = _parse_qbk(qbk)
    assert len(segs) == 1
    assert segs[0].msgid == "One line continued here."


def test_indented_code_block_skipped() -> None:
    qbk = "Prose line.\n    code not extracted\nMore prose.\n"
    segs = _parse_qbk(qbk)
    assert len(segs) == 2
    assert segs[0].msgid == "Prose line."
    assert segs[1].msgid == "More prose."


def test_section_title_and_body() -> None:
    qbk = "[section:anchor Title line\nBody text here.]\n"
    segs = _parse_qbk(qbk)
    titles = [s for s in segs if s.seg_type == "section-title"]
    paras = [s for s in segs if s.seg_type == "paragraph"]
    assert len(titles) == 1
    assert titles[0].msgid == "Title line"
    assert len(paras) == 1
    assert paras[0].msgid == "Body text here."


def test_inline_bracket_on_wrapped_line() -> None:
    qbk = "Start text\n[@https://example.com/ link]\nend text.\n"
    segs = _parse_qbk(qbk)
    assert len(segs) == 1
    assert "Start text" in segs[0].msgid
    assert "[@https://example.com/ link]" in segs[0].msgid


def test_qbk_to_po_locations() -> None:
    qbk = "[h1 Hi]\n\nHello.\n"
    store = qbk_to_po(qbk, "doc.qbk")
    units = [u for u in store.units if not u.isheader()]
    assert len(units) == 2
    assert "doc.qbk:1" in units[0].getlocations()
    assert "doc.qbk:3" in units[1].getlocations()


def test_po_to_qbk_applies_translation() -> None:
    template = "[heading English]\n"
    store = qbk_to_po(template, "t.qbk")
    for u in store.units:
        if not u.isheader() and u.source == "English":
            u.target = "Česky"
    out = po_to_qbk(template, store, "t.qbk")
    assert out == "[heading Česky]\n"


def test_po_to_qbk_fallback_untranslated() -> None:
    template = "[heading Only]\n"
    store = qbk_to_po(template, "t.qbk")
    out = po_to_qbk(template, store, "t.qbk")
    assert out == template
