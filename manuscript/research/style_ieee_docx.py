"""Apply IEEE reference run typography without changing reference wording or paragraph layout.

Call style_references(document, refs_json_path) immediately before Document.save().
The document must already contain the complete numbered bibliography under References.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Pt, RGBColor
from docx.text.run import Run


def _visible_text(paragraph):
    return ''.join(node.text or '' for node in paragraph._p.iter(qn('w:t')))


def _normalize(text):
    # Match the builder's existing typographical-hyphen normalization only.
    return text.replace('\u2010', '-').replace('\u2011', '-')


def _tex_literal(text):
    replacements = {
        r'\&': '&', r'\%': '%', r'\_': '_', r'\#': '#',
        r'\$': '$', r'\{': '{', r'\}': '}',
        r'\textendash{}': '–', r'\textemdash{}': '—',
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.replace('---', '—').replace('--', '–')


def _format_run(run, italic):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.italic = bool(italic)
    run.font.bold = False
    run.font.underline = False
    fonts = run._r.get_or_add_rPr().get_or_add_rFonts()
    for name in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + name), 'Times New Roman')


def style_references(document, refs_json_path):
    """Style all numbered IEEE references in place and return a compact audit dict.

    Italic spans come only from the supplied reference's ``\\textit{...}`` spans.
    DOI and URL text becomes a black, non-underlined clickable link. All visible
    text, paragraph numbering, paragraph properties and non-reference content
    are retained. Validation of every expected paragraph occurs before mutation.
    """
    data = json.loads(Path(refs_json_path).read_text(encoding='utf-8'))
    references = data['references']
    expected = {int(ref['number']): ref for ref in references}
    located = {}
    in_references = False
    for paragraph in document.paragraphs:
        value = _visible_text(paragraph)
        if value.strip().lower() == 'references':
            in_references = True
            continue
        if not in_references:
            continue
        match = re.match(r'^\[(\d+)\]\s+', value)
        if match:
            number = int(match.group(1))
            if number not in expected:
                raise ValueError(f'Unknown numbered reference [{number}]')
            if number in located:
                raise ValueError(f'Duplicate numbered reference [{number}]')
            located[number] = paragraph
    if set(located) != set(expected):
        raise ValueError(f'Incomplete bibliography; missing numbers {sorted(set(expected)-set(located))}')

    plans = []
    for number, ref in expected.items():
        paragraph = located[number]
        original = _visible_text(paragraph)
        expected_text = f"[{number}] {ref['plain_text']}"
        if _normalize(original) != _normalize(expected_text):
            raise ValueError(f'Reference [{number}] differs from the verified IEEE wording')
        spans = []
        latex = ref.get('latex_text') or ref['ieee_tex_text']
        for match in re.finditer(r'\\textit\{([^{}]*)\}', latex):
            phrase = _normalize(_tex_literal(match.group(1)))
            start = _normalize(original).find(phrase)
            if start < 0:
                raise ValueError(f'Italic phrase missing in reference [{number}]: {phrase!r}')
            spans.append((start, start + len(phrase)))
        links = []
        if ref.get('doi'):
            display = ref['doi']
            target = 'https://doi.org/' + display
        else:
            display = ref.get('url') or ''
            target = display
        if display:
            start = original.find(display)
            if start < 0:
                raise ValueError(f'Link text missing in reference [{number}]')
            links.append((start, start + len(display), target))
        plans.append((paragraph, original, spans, links))

    styled = italic_count = link_count = 0
    for paragraph, original, spans, links in plans:
        ppr_before = paragraph._p.pPr.xml if paragraph._p.pPr is not None else None
        points = sorted({0, len(original)} | {x for span in spans for x in span} |
                        {x for start, end, _ in links for x in (start, end)})
        paragraph.clear()  # python-docx retains w:pPr and its complete formatting.
        for start, end in zip(points, points[1:]):
            if start == end:
                continue
            italic = any(a <= start and end <= b for a, b in spans)
            link = next((target for a, b, target in links if a <= start and end <= b), None)
            run = paragraph.add_run(original[start:end])
            _format_run(run, italic)
            if link:
                hyperlink = OxmlElement('w:hyperlink')
                hyperlink.set(qn('r:id'), paragraph.part.relate_to(link, RT.HYPERLINK, is_external=True))
                hyperlink.set(qn('w:history'), '1')
                paragraph._p.remove(run._r)
                hyperlink.append(run._r)
                paragraph._p.append(hyperlink)
        assert _visible_text(paragraph) == original, 'Reference text changed unexpectedly'
        ppr_after = paragraph._p.pPr.xml if paragraph._p.pPr is not None else None
        assert ppr_after == ppr_before, 'Reference paragraph properties changed unexpectedly'
        styled += 1
        italic_count += len(spans)
        link_count += len(links)
    return {'styled_references': styled, 'italic_spans': italic_count,
            'clickable_links': link_count, 'reference_font_pt': 9,
            'visible_text_preserved': True, 'paragraph_properties_preserved': True}
