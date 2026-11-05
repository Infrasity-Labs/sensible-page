"""Inline SVG art for the Bank Statements Doc-Type page. Line-art with a hard offset shadow,
in Sensible editorial colors. All SVGs are lightweight and semantic."""

INK = '#1A1520'
SH = '#E6E6E9'
MAG = '#840055'
AMB = '#D88B1F'
OK = '#2E7B40'
MONO = "font-family=\"IBM Plex Mono, monospace\""
SANS = "font-family=\"IBM Plex Sans, sans-serif\""
SERIF = "font-family=\"IBM Plex Serif, serif\""
MUTE = '#8B857B'


def _open(w, h, cls='ap-ill'):
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none" stroke="{INK}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" focusable="false">')


def _doc(x, y, w, h, lines=3, shadow=True, stroke=INK, fill='#fff', cls=''):
    s = f'<rect x="{x+5}" y="{y+5}" width="{w}" height="{h}" rx="3" fill="{SH}" stroke="none"/>' if shadow else ''
    s += f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke}"/>'
    for i in range(lines):
        yy = y + 12 + i * 8
        ww = w - 20 - (i % 2) * 14
        s += f'<path d="M{x+8} {yy}h{ww}" stroke-width="1.2" opacity=".55"/>'
    return s


def _tag(x, y, label, hot=False):
    w = len(label) * 5.6 + 12
    fill = MAG if hot else '#fff'
    col = '#fff' if hot else INK
    return (f'<g><rect x="{x+3}" y="{y+3}" width="{w}" height="15" fill="{SH}" stroke="none"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="15" fill="{fill}"/>'
            f'<text x="{x+6}" y="{y+11}" font-size="8" {MONO} fill="{col}" stroke="none" letter-spacing=".5">{label}</text></g>')


def _t(x, y, txt, size, fam=SANS, fill=INK, anchor='start', weight=400, ls=0):
    return (f'<text x="{x}" y="{y}" font-size="{size}" {fam} fill="{fill}" stroke="none" '
            f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{ls}">{txt}</text>')


# ---------------------------------------------------------------- hero backdrop
def hero_rects():
    rects = [(600, -40, 420, 320), (470, 120, 400, 360), (330, 300, 390, 360), (170, 440, 380, 360), (-10, 560, 330, 300)]
    body = ''.join(
        f'<rect class="ap-hr" x="{x}" y="{y}" width="{w}" height="{h}" fill="rgba(255,255,255,.30)" stroke="#fff" stroke-width="2.5"/>'
        for x, y, w, h in rects)
    return (f'<svg class="ap-hero-art" viewBox="0 0 1000 760" preserveAspectRatio="xMaxYMid slice" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">{body}</svg>')


# ---------------------------------------------------------------- 4 challenge mini illustrations (200x120)
def mini(kind):
    s = _open(200, 120, 'ap-mini')
    if kind == 'tables':  # Multi-page table continuity
        s += _doc(14, 10, 78, 94, 0) + _doc(104, 10, 78, 94, 0)
        s += '<path d="M22 24h62M22 36h62M22 48h62M22 60h62M22 72h62M22 24v48M46 24v48M84 24v48" stroke-width="1.1" opacity=".55"/>'
        s += '<path d="M112 24h62M112 36h62M112 48h62M112 60h62M112 24v36M136 24v36M174 24v36" stroke-width="1.1" opacity=".55"/>'
        s += f'<path d="M92 56h12" stroke="{MAG}" stroke-dasharray="2 3"/><rect class="m1" x="22" y="48" width="62" height="12" fill="rgba(132,0,85,.15)" stroke="{MAG}"/>'
        s += f'<rect class="m2" x="112" y="24" width="62" height="12" fill="rgba(132,0,85,.15)" stroke="{MAG}"/>'
    elif kind == 'balance':  # Running balance arithmetic check
        s += _doc(30, 8, 100, 104, 0)
        s += '<path d="M42 24h50M42 38h50M42 52h50" stroke-width="1.2" opacity=".55"/><path d="M100 24h18M100 38h18M100 52h18" stroke-width="1.6"/>'
        s += '<path d="M42 66h76" stroke-width="1.6"/>'
        s += f'<path class="m1" d="M100 82h18" stroke="{MAG}" stroke-width="2"/><path d="M42 82h34" stroke-width="1.2" opacity=".55"/>'
        s += f'<circle class="m2" cx="158" cy="64" r="20" fill="#fff" stroke="{OK}"/><path d="M148 64l7 7 13-14" stroke="{OK}" stroke-width="2"/>'
    elif kind == 'fraud':  # Layout & metadata tampering / anomaly
        s += _doc(20, 14, 110, 92, 0)
        s += '<path d="M30 30h40M30 42h60M30 54h70M30 66h50M30 78h60" stroke-width="1.1" opacity=".45"/>'
        s += f'<rect class="m1" x="72" y="48" width="48" height="18" fill="rgba(216,139,31,.15)" stroke="{AMB}" stroke-dasharray="2 2"/>'
        s += f'<circle class="m2" cx="156" cy="58" r="18" fill="#fff" stroke="{AMB}"/><path d="M156 48v12M156 64v2" stroke="{AMB}" stroke-width="2"/>'
    else:  # multi_account: multi-account package splitting
        s += _doc(10, 12, 50, 64, 2) + _doc(75, 44, 50, 64, 2) + _doc(140, 12, 50, 64, 2)
        s += f'<text x="18" y="66" font-size="8" {MONO} stroke="none" fill="{INK}">CHK</text><text x="83" y="98" font-size="8" {MONO} stroke="none" fill="{INK}">SAV</text><text x="148" y="66" font-size="8" {MONO} stroke="none" fill="{INK}">MMA</text>'
        s += f'<path class="m1" d="M60 56C68 56 68 70 75 70M125 70C132 70 132 56 140 56" stroke="{MAG}" stroke-width="1.6" stroke-dasharray="3 3"/>'
    return s + '</svg>'


# ---------------------------------------------------------------- 48px line icons
def icon(name):
    p = {
        'bank': '<path d="M4 18h40M6 18l18-12 18 12M8 18v18M16 18v18M24 18v18M32 18v18M40 18v18M4 36h40M2 42h44"/>',
        'ledger': '<rect x="8" y="6" width="32" height="36" rx="2"/><path d="M8 16h32M8 26h32M18 6v36"/>',
        'stack': '<rect x="14" y="6" width="26" height="32" rx="2"/><path d="M10 12v30h26M20 16h14M20 24h14M20 32h8"/>',
        'txns': '<path d="M8 12h32M8 20h22M8 28h32M8 36h18M36 20v16M42 26l-6-6-6 6"/>',
        'shield': '<path d="M24 6l16 6v12c0 10-7 18-16 20-9-2-16-10-16-20V12l16-6zM18 24l4 4 8-8"/>',
        'file': '<path d="M12 5h17l9 9v29H12z"/><path d="M29 5v9h9M18 24h14M18 31h14M18 38h8"/>',
        'code': '<path d="M16 16l-8 8 8 8M32 16l8 8-8 8M27 10l-6 28"/>',
        'check': '<circle cx="24" cy="24" r="18"/><path d="M16 24l5 5 11-11"/>',
        'flow': '<rect x="6" y="8" width="14" height="12" rx="2"/><rect x="28" y="8" width="14" height="12" rx="2"/><rect x="17" y="28" width="14" height="12" rx="2"/><path d="M13 20v4h11v4M35 20v4H24"/>',
        'tax': '<rect x="8" y="6" width="32" height="36" rx="2"/><path d="M14 14h20M14 20h20M14 26h12M14 32h8"/>',
        'paystub': '<rect x="8" y="8" width="32" height="32" rx="2"/><circle cx="24" cy="18" r="4"/><path d="M16 30c0-4 4-5 8-5s8 1 8 5"/>',
        'pnl': '<rect x="8" y="6" width="32" height="36" rx="2"/><path d="M14 32l6-8 6 4 8-10"/>',
        'invoice': '<rect x="8" y="6" width="32" height="36" rx="2"/><path d="M14 14h20M14 22h14M14 30h20"/>',
        'acord': '<path d="M24 6l16 6v12c0 10-7 18-16 20-9-2-16-10-16-20V12l16-6z"/><path d="M18 22h12M18 28h8"/>',
        'plan': '<circle cx="21" cy="21" r="11"/><path d="M29 29l12 12M16 21h10M21 16v10"/>',
        'build': '<path d="M18 12L6 24l12 12M30 12l12 12-12 12M27 8l-6 32"/>',
        'deploy': '<path d="M24 6c8 6 11 14 9 24H15c-2-10 1-18 9-24zM15 30l-6 8 9-2M33 30l6 8-9-2"/><circle cx="24" cy="20" r="3"/>',
        'adjust': '<path d="M8 14h32M8 24h32M8 34h32"/><circle cx="16" cy="14" r="4" fill="#fff"/><circle cx="32" cy="24" r="4" fill="#fff"/><circle cx="20" cy="34" r="4" fill="#fff"/>',
        'link': '<circle cx="12" cy="24" r="6"/><circle cx="36" cy="12" r="6"/><circle cx="36" cy="36" r="6"/><path d="M18 22l12-8M18 26l12 8"/>',
    }[name]
    return (f'<svg class="ap-icon" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="{INK}" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{p}</svg>')


# ---------------------------------------------------------------- SenseML vs LLM comparison graphic
def senseml_vs_llm_art():
    s = _open(440, 240, 'bs-cmp-svg')
    # Left: Pure LLM prompt (unstructured tokens, hallucination risk)
    s += f'<rect x="10" y="10" width="200" height="220" rx="6" fill="#FBFBF9" stroke="{SH}"/>'
    s += _t(24, 34, 'Pure LLMs / OCR APIs', 11, SERIF, weight=600, fill=INK)
    s += _t(24, 48, 'Token-by-token text guessing', 8, SANS, fill=MUTE)
    s += f'<rect x="24" y="60" width="172" height="88" rx="3" fill="#fff" stroke="{SH}"/>'
    s += f'<path d="M34 76h152M34 90h110M34 104h130M34 118h90M34 132h140" stroke="{SH}" stroke-width="1.5"/>'
    # Red flagged hallucination line
    s += f'<rect x="30" y="100" width="160" height="20" fill="rgba(216,139,31,0.12)" stroke="{AMB}" stroke-dasharray="2 2" rx="2"/>'
    s += _t(36, 114, 'Row 48 dropped · Math delta -$320.00', 7.5, MONO, fill=AMB, weight=600)
    s += _t(24, 168, '✕ Fails on 30+ page statements', 8.5, SANS, fill='#993333')
    s += _t(24, 186, '✕ Pennies hallucinated in balances', 8.5, SANS, fill='#993333')
    s += _t(24, 204, '✕ No audit trail to source coordinates', 8.5, SANS, fill='#993333')

    # Right: Sensible (SenseML deterministic table anchors + math validation)
    s += f'<rect x="230" y="10" width="200" height="220" rx="6" fill="#fff" stroke="{MAG}" stroke-width="1.5"/>'
    s += _t(244, 34, 'Sensible (SenseML + Math)', 11, SERIF, weight=600, fill=MAG)
    s += _t(244, 48, 'Deterministic anchors & table bounds', 8, SANS, fill=MUTE)
    s += f'<rect x="244" y="60" width="172" height="88" rx="3" fill="#F7F3F6" stroke="rgba(132,0,85,0.2)"/>'
    s += f'<path d="M254 76h152M254 90h152M254 104h152M254 118h152M254 132h152M290 60v88M360 60v88" stroke="rgba(132,0,85,0.2)" stroke-width="1"/>'
    s += f'<circle cx="394" cy="76" r="5" fill="{OK}"/><path d="M392 76l1.5 1.5 3-3" stroke="#fff" stroke-width="1.2"/>'
    s += f'<circle cx="394" cy="104" r="5" fill="{OK}"/><path d="M392 104l1.5 1.5 3-3" stroke="#fff" stroke-width="1.2"/>'
    s += _t(244, 168, '✓ Continuous tables over 100+ pages', 8.5, SANS, fill=OK)
    s += _t(244, 186, '✓ Starting + Credits - Debits = Ending verified', 8.5, SANS, fill=OK)
    s += _t(244, 204, '✓ Exact page + bounding box on every value', 8.5, SANS, fill=OK)
    return s + '</svg>'
