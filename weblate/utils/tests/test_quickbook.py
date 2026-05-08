# Copyright © Boost Organization <boost@boost.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest import TestCase

from weblate.utils.quickbook import (
    _find_bracket_end,
    _parse_bracket_keyword,
    _parse_qbk,
    po_to_qbk,
    qbk_to_po,
)


class QuickBookUtilsTest(TestCase):
    def test_find_bracket_end_nested(self) -> None:
        text = "[outer [inner] tail]"
        end = _find_bracket_end(text, 0)
        self.assertEqual(end, len(text) - 1)

    def test_find_bracket_end_triple_quote(self) -> None:
        text = "['''[not closed]''']"
        end = _find_bracket_end(text, 0)
        self.assertEqual(end, len(text) - 1)

    def test_parse_bracket_keyword_section_with_id(self) -> None:
        block = "[section:myid Title here]"
        kw, off = _parse_bracket_keyword(block)
        self.assertEqual(kw, "section")
        self.assertEqual(block[off:-1].lstrip(), "Title here")

    def test_skip_include_and_parse_heading(self) -> None:
        qbk = "[include other.qbk]\n\n[h1 Title]\n"
        segs = _parse_qbk(qbk)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].msgid, "Title")
        self.assertEqual(segs[0].seg_type, "heading")

    def test_paragraph_soft_wrap_joined(self) -> None:
        qbk = "One line\ncontinued here.\n"
        segs = _parse_qbk(qbk)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].msgid, "One line continued here.")

    def test_indented_code_block_skipped(self) -> None:
        qbk = "Prose line.\n    code not extracted\nMore prose.\n"
        segs = _parse_qbk(qbk)
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0].msgid, "Prose line.")
        self.assertEqual(segs[1].msgid, "More prose.")

    def test_section_title_and_body(self) -> None:
        qbk = "[section:anchor Title line\nBody text here.]\n"
        segs = _parse_qbk(qbk)
        titles = [s for s in segs if s.seg_type == "section-title"]
        paras = [s for s in segs if s.seg_type == "paragraph"]
        self.assertEqual(len(titles), 1)
        self.assertEqual(titles[0].msgid, "Title line")
        self.assertEqual(len(paras), 1)
        self.assertEqual(paras[0].msgid, "Body text here.")

    def test_inline_bracket_on_wrapped_line(self) -> None:
        qbk = "Start text\n[@https://example.com/ link]\nend text.\n"
        segs = _parse_qbk(qbk)
        self.assertEqual(len(segs), 1)
        self.assertIn("Start text", segs[0].msgid)
        self.assertIn("[@https://example.com/ link]", segs[0].msgid)

    def test_qbk_to_po_locations(self) -> None:
        qbk = "[h1 Hi]\n\nHello.\n"
        store = qbk_to_po(qbk, "doc.qbk")
        units = [u for u in store.units if not u.isheader()]
        self.assertEqual(len(units), 2)
        self.assertIn("doc.qbk:1", units[0].getlocations())
        self.assertIn("doc.qbk:3", units[1].getlocations())

    def test_po_to_qbk_applies_translation(self) -> None:
        template = "[heading English]\n"
        store = qbk_to_po(template, "t.qbk")
        for u in store.units:
            if not u.isheader() and u.source == "English":
                u.target = "Česky"
        out = po_to_qbk(template, store, "t.qbk")
        self.assertEqual(out, "[heading Česky]\n")

    def test_po_to_qbk_fallback_untranslated(self) -> None:
        template = "[heading Only]\n"
        store = qbk_to_po(template, "t.qbk")
        out = po_to_qbk(template, store, "t.qbk")
        self.assertEqual(out, template)
