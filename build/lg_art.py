"""Inline SVG art for the Legal / Contracts solutions page. Same line-art-with-offset-shadow
language as bs_art.py (ink strokes, hard #E6E6E9 shadow, magenta accent)."""
from bs_art import (_open, _doc, _tag, _t, INK, SH, MAG, AMB, OK, MONO, SANS, SERIF, MUTE,
                    hero_rects, icon as _base_icon)

EXTRA_ICONS = {
    'clm': '<rect x="6" y="8" width="22" height="28" rx="2"/><rect x="18" y="14" width="22" height="28" rx="2" fill="#fff"/><path d="M23 24h12M23 30h12M23 36h7"/>',
    'obligation': '<rect x="8" y="6" width="32" height="36" rx="2"/><path d="M14 16l3 3 5-6M26 17h8M14 27l3 3 5-6M26 28h8M14 37h8"/>',
    'renewal': '<path d="M38 24a14 14 0 1 1-4.5-10.3"/><path d="M38 8v8h-8"/><path d="M24 17v8l5 3"/>',
    'compliance': '<path d="M24 8v32M13 40h22M9 14h30"/><path d="M9 14l-5 12a6 6 0 0 0 10 0zM39 14l-5 12a6 6 0 0 0 10 0z"/>',
    'lock': '<rect x="10" y="22" width="28" height="20" rx="3"/><path d="M16 22v-6a8 8 0 0 1 16 0v6M24 30v5"/>',
    'clock': '<circle cx="24" cy="24" r="17"/><path d="M24 14v10l7 4"/>',
    'contract': '<path d="M12 5h17l9 9v29H12z"/><path d="M29 5v9h9M18 22h14M18 28h14"/><path d="M18 38c3-5 5-5 6-1s3 2 6-2"/>',
}


def icon(name):
    if name in EXTRA_ICONS:
        return (f'<svg class="ap-icon" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="{INK}" '
                f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{EXTRA_ICONS[name]}</svg>')
    return _base_icon(name)


# ---------------------------------------------------------------- 3 challenge illustrations (200x120)
def mini(kind):
    s = _open(200, 120, 'ap-mini')
    if kind == 'language':  # dense legal prose -> typed fields
        s += _doc(14, 10, 96, 100, 0)
        s += '<path d="M24 26h74M24 36h66M24 46h74M24 56h58M24 66h74M24 76h50M24 86h70" stroke-width="1.1" opacity=".5"/>'
        s += f'<rect class="m1" x="24" y="42" width="40" height="9" fill="rgba(132,0,85,.15)" stroke="{MAG}"/>'
        s += f'<rect class="m2" x="52" y="62" width="34" height="9" fill="rgba(132,0,85,.15)" stroke="{MAG}"/>'
        s += f'<path d="M64 46C84 46 92 36 124 36M86 66C104 66 112 62 124 62" stroke="{MAG}" stroke-dasharray="2 3"/>'
        s += _tag(124, 28, 'PARTY', True) + _tag(124, 54, 'DATE') + _tag(124, 80, 'AMOUNT')
    elif kind == 'clause':  # clause located wherever it sits
        s += _doc(10, 12, 54, 96, 0) + _doc(73, 12, 54, 96, 0) + _doc(136, 12, 54, 96, 0)
        for x, lab, hy in ((16, '3.', 36), (79, 'IX', 62), (142, '14.2', 84)):
            s += f'<path d="M{x} 26h38M{x} 36h30M{x} 46h38M{x} 56h28M{x} 66h38M{x} 76h30M{x} 86h38" stroke-width="1" opacity=".38"/>'
            s += f'<rect class="m1" x="{x-2}" y="{hy-4}" width="42" height="12" fill="rgba(132,0,85,.15)" stroke="{MAG}"/>'
            s += f'<text x="{x}" y="{hy+5}" font-size="7.5" {MONO} fill="{MAG}" stroke="none" font-weight="600">{lab}</text>'
        s += f'<path d="M30 118V108M100 118V108M163 118V108" stroke="{MAG}" stroke-dasharray="2 2"/>'
    else:  # amendment linked to parent
        s += _doc(14, 8, 74, 54, 2) + _doc(112, 56, 74, 54, 2)
        s += _t(22, 52, 'MSA-2024-0418', 7, MONO, fill=INK)
        s += _t(120, 100, 'AMENDMENT 1', 7, MONO, fill=INK)
        s += f'<path class="m1" d="M88 36C104 36 100 80 112 80" stroke="{MAG}" stroke-width="1.6" stroke-dasharray="3 3"/>'
        s += f'<rect class="m2" x="120" y="64" width="58" height="9" fill="rgba(132,0,85,.15)" stroke="{MAG}"/>'
        s += _tag(128, 14, 'CHG §2', True)
    return s + '</svg>'


# ---------------------------------------------------------------- hybrid (LLM only vs LLM + SenseML)
def hybrid_art():
    s = _open(440, 250, 'bs-cmp-svg')
    s += f'<rect x="10" y="10" width="200" height="230" rx="6" fill="#FBFBF9" stroke="{SH}"/>'
    s += _t(24, 34, 'LLM-only extraction', 11, SERIF, weight=600)
    s += _t(24, 48, 'Free-text answer to a prompt', 8, SANS, fill=MUTE)
    s += f'<rect x="24" y="60" width="172" height="92" rx="3" fill="#fff" stroke="{SH}"/>'
    s += _t(32, 78, 'The agreement appears to start', 8.2, SERIF, fill=INK)
    s += _t(32, 91, 'around April 2024 and seems to', 8.2, SERIF, fill=INK)
    s += _t(32, 104, 'renew yearly. Either side can', 8.2, SERIF, fill=INK)
    s += _t(32, 117, 'probably leave with two months', 8.2, SERIF, fill=INK)
    s += _t(32, 130, 'of notice...', 8.2, SERIF, fill=INK)
    s += f'<rect x="28" y="106" width="164" height="14" fill="rgba(216,139,31,0.13)" stroke="{AMB}" stroke-dasharray="2 2" rx="2"/>'
    s += _t(24, 172, '\u2715 Output shape follows the prompt', 8.5, SANS, fill='#993333')
    s += _t(24, 190, '\u2715 Dates and notice periods left as prose', 8.5, SANS, fill='#993333')
    s += _t(24, 208, '\u2715 No page or bounding box to audit', 8.5, SANS, fill='#993333')

    s += f'<rect x="230" y="10" width="200" height="230" rx="6" fill="#fff" stroke="{MAG}" stroke-width="1.5"/>'
    s += _t(244, 34, 'Sensible (LLM + SenseML)', 11, SERIF, weight=600, fill=MAG)
    s += _t(244, 48, 'Schema-enforced, typed fields', 8, SANS, fill=MUTE)
    s += f'<rect x="244" y="60" width="172" height="92" rx="3" fill="#F7F3F6" stroke="rgba(132,0,85,0.2)"/>'
    rows = [('effective_date', '2024-04-18'), ('initial_term_months', '24'), ('termination_notice_days', '60'),
            ('governing_law', '"Massachusetts"')]
    for i, (k, v) in enumerate(rows):
        y = 78 + i * 16
        s += _t(252, y, k, 7.6, MONO, fill=MAG)
        s += _t(404, y, v, 7.6, MONO, fill=OK, anchor='end')
    s += f'<path d="M252 140h156" stroke="rgba(132,0,85,0.2)"/>'
    s += _t(252, 148, 'page 1 \u00b7 bbox [64, 212, 410, 28]', 6.8, MONO, fill=MUTE)
    s += _t(244, 172, '\u2713 LLM reads the legal language', 8.5, SANS, fill=OK)
    s += _t(244, 190, '\u2713 SenseML enforces your contract schema', 8.5, SANS, fill=OK)
    s += _t(244, 208, '\u2713 Page + bounding box on every value', 8.5, SANS, fill=OK)
    return s + '</svg>'


# ---------------------------------------------------------------- contract schematic that follows the active field tab
def schem():
    s = (f'<svg class="lg-schem" data-active="parties" viewBox="0 0 220 280" xmlns="http://www.w3.org/2000/svg" fill="none" '
         f'stroke="{INK}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">')
    s += f'<rect x="10" y="10" width="200" height="266" rx="3" fill="{SH}" stroke="none"/>'
    s += f'<rect x="4" y="4" width="200" height="266" rx="3" fill="#fff"/>'
    # title rule
    s += f'<path d="M62 20h80" stroke-width="2"/><path d="M82 28h40" opacity=".5"/>'
    # parties/dates region
    s += f'<g class="rg-parties"><rect class="bg" x="12" y="38" width="184" height="52" rx="2"/>'
    s += '<path d="M20 50h92M20 60h70M20 70h82M20 80h60" opacity=".5"/><path d="M130 50h58M130 60h58M130 70h58" opacity=".5"/>'
    s += f'<text class="lb" x="118" y="35" font-size="7" {MONO} fill="{MAG}" stroke="none">PARTIES &amp; DATES</text></g>'
    # financial region
    s += f'<g class="rg-financial"><rect class="bg" x="12" y="98" width="184" height="42" rx="2"/>'
    s += '<path d="M20 110h100M20 120h86M20 130h92" opacity=".5"/><path d="M146 110h42M146 120h42M146 130h42" stroke-width="2"/>'
    s += f'<text class="lb" x="118" y="95" font-size="7" {MONO} fill="{MAG}" stroke="none">FINANCIAL TERMS</text></g>'
    # clauses region
    s += f'<g class="rg-clauses"><rect class="bg" x="12" y="148" width="184" height="72" rx="2"/>'
    s += '<path d="M20 160h160M20 170h140M20 180h156M20 190h120M20 200h150M20 210h96" opacity=".5"/>'
    s += f'<text class="lb" x="118" y="145" font-size="7" {MONO} fill="{MAG}" stroke="none">KEY CLAUSES</text></g>'
    # signatories region
    s += f'<g class="rg-sign"><rect class="bg" x="12" y="228" width="184" height="36" rx="2"/>'
    s += '<path d="M22 250h60M120 250h60" opacity=".7"/><path d="M26 244c6-8 8-6 10 0s6 2 10-4M124 244c6-8 8-6 10 0s6 2 10-4" stroke-width="1.1"/>'
    s += f'<text class="lb" x="118" y="225" font-size="7" {MONO} fill="{MAG}" stroke="none">SIGNATORIES</text></g>'
    return s + '</svg>'
