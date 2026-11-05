#!/usr/bin/env python3
"""Builds the /solutions/legal page: contract data extraction for legal teams.

All product facts come from Sensible's live contracts doc-type page and docs
(fields, supported contract types, clause identification, amendment linking, FAQs,
security, pricing, SDK usage). The sample contracts shown in the workbench are
illustrative, except the MSA, which mirrors Sensible's public contracts demo.

Run from anywhere:  python3 build/lg_build.py
Reads:   build/template/index.html (site nav, footer, base CSS), build/css/*.css, build/js/lg.js
Writes:  site/legal.html (deployable page), build/out/fragment.html (Webflow-ready body fragment)
"""
import html as H
import json
import os
import re
from lg_art import hero_rects, mini, icon, hybrid_art, schem

os.chdir(os.path.dirname(os.path.abspath(__file__)))

src = open('template/index.html').read().split('\n')
L = lambda a, b: '\n'.join(src[a - 1:b])
full = '\n'.join(src)
ap_css = open('css/ap.css').read()
bs_css = open('css/bs.css').read()
lg_css = open('css/lg.css').read()
lg_js = open('js/lg.js').read()


def esc(s):
    return H.escape(str(s), quote=False)


def attr(obj):
    return H.escape(json.dumps(obj, ensure_ascii=False), quote=True)


def pj(v, ind=0):
    """Dark-panel highlighter (k / s / n), mirrors pretty() in lg.js."""
    pad, end = ' ' * (ind + 2), ' ' * ind
    if v is None:
        return '<span class="n">null</span>'
    if isinstance(v, bool):
        return f'<span class="n">{str(v).lower()}</span>'
    if isinstance(v, (int, float)):
        return f'<span class="n">{v}</span>'
    if isinstance(v, str):
        return f'<span class="s">"{esc(v)}"</span>'
    if isinstance(v, list):
        if not v:
            return '[]'
        return '[\n' + ',\n'.join(pad + pj(x, ind + 2) for x in v) + '\n' + end + ']'
    return '{\n' + ',\n'.join(f'{pad}<span class="k">"{esc(k)}"</span>: {pj(x, ind + 2)}' for k, x in v.items()) + '\n' + end + '}'


def dt(source, iso):
    return {'source': source, 'value': iso, 'type': 'date'}


# ============================================================ HERO STAGE DATA (live extraction)
# row: (key, display value, kind s|n, confidence, "page · bbox", source text, check note, needs_review)
CONTRACTS = [
    dict(
        k='msa', tab='MSA', file='MSA-2024-0418-NB.pdf', ref='MSA-2024-0418-NB', pages=12, title='Master Services Agreement',
        blocks=[
            ('p', 'This Master Services Agreement is entered into as of [[effective_date|April 18, 2024]], by and between Client [[client_party|Stillwater Robotics, Inc.]], a Delaware corporation, and Provider [[provider_party|Northbridge Studio LLC]], a Massachusetts limited liability company.'),
            ('h', '2. Compensation &amp; Payment'),
            ('p', 'Client shall pay Provider the fees set forth in each SOW. Invoices are due [[payment_terms_days|Net 30]] from the date of issuance. Undisputed amounts not paid when due accrue interest at [[late_interest_pct_per_month|1.5% per month]] or the maximum rate permitted by law.'),
            ('h', '3. Term &amp; Termination'),
            ('p', 'The initial term shall continue for twenty-four (24) months and shall [[auto_renewal|renew for successive one-year periods]] unless terminated by either Party upon [[termination_notice_days|sixty (60) days’ written notice]].'),
            ('h', '4. Governing Law'),
            ('p', 'This Agreement is governed by the laws of the Commonwealth of [[governing_law|Massachusetts]].'),
            ('sig', 'signatories', ('E. Whitmore', 'Elena Whitmore', 'VP, Operations'), ('J. Northbridge', 'Julian Northbridge', 'Managing Partner')),
        ],
        rows=[
            ('effective_date', '2024-04-18', 's', 0.99, 'p.1 · [64, 148, 118, 14]', 'as of April 18, 2024', 'ISO 8601, printed text kept as source', False),
            ('client_party', 'Stillwater Robotics, Inc.', 's', 0.99, 'p.1 · [64, 176, 190, 14]', 'Client Stillwater Robotics, Inc., a Delaware corporation', 'Role resolved: client', False),
            ('provider_party', 'Northbridge Studio LLC', 's', 0.99, 'p.1 · [64, 204, 180, 14]', 'Provider Northbridge Studio LLC, a Massachusetts LLC', 'Role resolved: provider', False),
            ('payment_terms_days', '30', 'n', 0.98, 'p.2 · [64, 120, 52, 14]', 'Invoices are due Net 30', 'Typed as a number, not prose', False),
            ('late_interest_pct_per_month', '1.5', 'n', 0.97, 'p.2 · [64, 158, 96, 14]', 'accrue interest at 1.5% per month', 'Percentage normalized', False),
            ('auto_renewal', 'true', 'n', 0.96, 'p.3 · [64, 110, 240, 14]', 'renew for successive one-year periods', 'Found by meaning, not position', False),
            ('termination_notice_days', '60', 'n', 0.97, 'p.3 · [64, 138, 210, 14]', 'sixty (60) days’ written notice', 'Spelled-out number returned as 60', False),
            ('governing_law', 'Massachusetts', 's', 0.98, 'p.9 · [64, 232, 120, 14]', 'laws of the Commonwealth of Massachusetts', 'Captured once, no conflicts found', False),
            ('signatories', '[ 2 signatories ]', 'n', 0.99, 'p.12 · [64, 520, 482, 74]', 'Elena Whitmore, VP Operations · Julian Northbridge, Managing Partner', 'Match the preamble parties', False),
        ]),
    dict(
        k='nda', tab='NDA', file='Halcyon-Meridian-NDA.pdf', ref='NDA-2025-0109', pages=6, title='Mutual Non-Disclosure Agreement',
        blocks=[
            ('p', 'This Mutual Non-Disclosure Agreement is effective [[effective_date|January 9, 2025]] between [[disclosing_party|Halcyon Biologics, Inc.]] (“Discloser”) and [[receiving_party|Meridian Capital Partners LP]] (“Recipient”). [[mutual|Each party may disclose and receive Confidential Information]].'),
            ('h', '2. Term'),
            ('p', 'This Agreement continues for [[term_months|thirty-six (36) months]] unless earlier terminated by either party.'),
            ('h', '4. Confidentiality'),
            ('p', 'Obligations of confidentiality survive for [[confidentiality_survival_years|five (5) years]] following expiration or termination. Neither party shall solicit the other’s employees for [[non_solicit_months|twelve (12) months]].'),
            ('h', '9. Governing Law'),
            ('p', 'This Agreement is governed by the laws of the State of [[governing_law|New York]].'),
            ('sig', 'signatories', ('P. Raman', 'Dr. Priya Raman', 'Chief Executive Officer'), ('M. Hale', 'Marcus Hale', 'General Partner')),
        ],
        rows=[
            ('effective_date', '2025-01-09', 's', 0.99, 'p.1 · [60, 150, 120, 14]', 'effective January 9, 2025', 'ISO 8601, printed text kept as source', False),
            ('disclosing_party', 'Halcyon Biologics, Inc.', 's', 0.99, 'p.1 · [60, 176, 170, 14]', 'Halcyon Biologics, Inc. (“Discloser”)', 'Role resolved: discloser', False),
            ('receiving_party', 'Meridian Capital Partners LP', 's', 0.99, 'p.1 · [60, 202, 210, 14]', 'Meridian Capital Partners LP (“Recipient”)', 'Role resolved: recipient', False),
            ('mutual', 'true', 'n', 0.97, 'p.1 · [60, 230, 380, 14]', 'Each party may disclose and receive Confidential Information', 'Mutual vs. one-way detected', False),
            ('term_months', '36', 'n', 0.98, 'p.2 · [60, 118, 160, 14]', 'thirty-six (36) months', 'Spelled-out number returned as 36', False),
            ('confidentiality_survival_years', '5', 'n', 0.96, 'p.3 · [60, 140, 150, 14]', 'survive for five (5) years', 'Found by meaning, not position', False),
            ('non_solicit_months', '12', 'n', 0.95, 'p.3 · [60, 168, 140, 14]', 'solicit the other’s employees for twelve (12) months', 'Found by meaning, not position', False),
            ('governing_law', 'New York', 's', 0.97, 'p.5 · [60, 300, 90, 14]', 'laws of the State of New York', 'Law and venue captured separately', False),
            ('signatories', '[ 2 signatories ]', 'n', 0.99, 'p.6 · [60, 480, 486, 72]', 'Dr. Priya Raman, CEO · Marcus Hale, General Partner', 'Signed on different dates, both kept', False),
        ]),
    dict(
        k='saas', tab='SaaS agreement', file='Cobalt-Redwood-SaaS.pdf', ref='SUB-2025-0301', pages=18, title='Subscription Agreement',
        blocks=[
            ('p', 'This Subscription Agreement is effective [[effective_date|March 1, 2025]]. [[vendor_party|Cobalt Analytics, Inc.]] (“Vendor”) grants [[customer_party|Redwood Health Systems]] (“Customer”) a subscription to the Services.'),
            ('h', '3. Fees'),
            ('p', 'Customer shall pay an Annual Subscription Fee of [[annual_fee|$184,000]], invoiced annually and payable [[payment_terms_days|Net 45]].'),
            ('h', '12. Renewal'),
            ('p', 'The Subscription Term renews for successive 12-month periods unless either party gives notice at least [[renewal_notice_days|ninety (90) days]] before the renewal date.'),
            ('h', '14. Liability &amp; Service Levels'),
            ('p', 'Each party’s aggregate liability is limited to [[liability_cap_months_of_fees|the fees paid in the twelve (12) months]] preceding the claim. Vendor commits to [[sla_uptime_pct|99.9% uptime]].'),
            ('h', '20. Governing Law'),
            ('p', 'This Agreement is governed by the laws of the State of [[governing_law|Delaware]].'),
        ],
        rows=[
            ('effective_date', '2025-03-01', 's', 0.99, 'p.1 · [58, 140, 110, 14]', 'effective March 1, 2025', 'ISO 8601, printed text kept as source', False),
            ('vendor_party', 'Cobalt Analytics, Inc.', 's', 0.99, 'p.1 · [58, 160, 160, 14]', 'Cobalt Analytics, Inc. (“Vendor”)', 'Role resolved: vendor', False),
            ('customer_party', 'Redwood Health Systems', 's', 0.99, 'p.1 · [58, 180, 170, 14]', 'Redwood Health Systems (“Customer”)', 'Role resolved: customer', False),
            ('annual_fee', '184000', 'n', 0.98, 'p.2 · [58, 118, 70, 14]', 'Annual Subscription Fee of $184,000', 'Currency typed with unit', False),
            ('payment_terms_days', '45', 'n', 0.98, 'p.2 · [58, 140, 60, 14]', 'payable Net 45', 'Typed as a number, not prose', False),
            ('renewal_notice_days', '90', 'n', 0.96, 'p.9 · [58, 262, 130, 14]', 'notice at least ninety (90) days before the renewal date', 'Found by meaning, not position', False),
            ('liability_cap_months_of_fees', '12', 'n', 0.95, 'p.11 · [58, 180, 230, 14]', 'limited to the fees paid in the twelve (12) months', 'Cap normalized to months of fees', False),
            ('sla_uptime_pct', '99.9', 'n', 0.97, 'p.11 · [58, 212, 100, 14]', 'Vendor commits to 99.9% uptime', 'Percentage normalized', False),
            ('governing_law', 'Delaware', 's', 0.97, 'p.16 · [58, 330, 90, 14]', 'laws of the State of Delaware', 'Captured once, no conflicts found', False),
        ]),
    dict(
        k='lease', tab='Commercial lease', file='Pinecrest-Aldous-Lease.pdf', ref='LSE-2024-0901', pages=34, title='Commercial Lease Agreement',
        blocks=[
            ('p', 'This Commercial Lease is made between [[landlord|Pinecrest Properties LLC]] (“Landlord”) and [[tenant|Aldous &amp; Wren Studio LLC]] (“Tenant”) for [[premises|Suite 300, 88 Harbor Street, Boston, MA 02110]].'),
            ('h', '2. Term'),
            ('p', 'The Commencement Date is [[commencement_date|September 1, 2024]] and the term is [[term_months|sixty (60) months]].'),
            ('h', '4. Rent'),
            ('p', 'Base Rent is [[base_rent_monthly|$14,500.00 per month]], increasing [[rent_escalation_pct_annual|3% annually]] on each anniversary. Tenant shall deposit [[security_deposit|$29,000.00]] as security.'),
            ('h', '26. Renewal Option'),
            ('p', 'Tenant may extend for one five-year term by written notice given not less than [[renewal_option_notice_days|six (6) months]] before expiration.'),
        ],
        rows=[
            ('landlord', 'Pinecrest Properties LLC', 's', 0.99, 'p.1 · [60, 152, 170, 14]', 'Pinecrest Properties LLC (“Landlord”)', 'Role resolved: landlord', False),
            ('tenant', 'Aldous & Wren Studio LLC', 's', 0.99, 'p.1 · [60, 172, 170, 14]', 'Aldous & Wren Studio LLC (“Tenant”)', 'Role resolved: tenant', False),
            ('premises', 'Suite 300, 88 Harbor Street, Boston, MA', 's', 0.98, 'p.1 · [60, 192, 300, 14]', 'Suite 300, 88 Harbor Street, Boston, MA 02110', 'Address captured as one field', False),
            ('commencement_date', '2024-09-01', 's', 0.98, 'p.2 · [60, 118, 130, 14]', 'Commencement Date is September 1, 2024', 'ISO 8601, printed text kept as source', False),
            ('term_months', '60', 'n', 0.98, 'p.2 · [60, 136, 130, 14]', 'the term is sixty (60) months', 'Spelled-out number returned as 60', False),
            ('base_rent_monthly', '14500', 'n', 0.98, 'p.6 · [60, 204, 130, 14]', 'Base Rent is $14,500.00 per month', 'Currency typed with unit', False),
            ('rent_escalation_pct_annual', '3.0', 'n', 0.97, 'p.6 · [60, 222, 100, 14]', 'increasing 3% annually', 'Percentage normalized', False),
            ('security_deposit', '29000', 'n', 0.98, 'p.6 · [60, 244, 90, 14]', 'deposit $29,000.00 as security', 'Currency typed with unit', False),
            ('renewal_option_notice_days', '180', 'n', 0.62, 'p.21 · [60, 350, 120, 14]', 'not less than six (6) months before expiration', 'Converted from months, low confidence: sent to human review', True),
        ]),
]


def marks(text, flagged):
    def sub(m):
        key, label = m.group(1), m.group(2)
        cls = 'lg-hl rev' if key in flagged else 'lg-hl'
        return f'<mark class="{cls}" data-f="{key}">{label}</mark>'
    return re.sub(r'\[\[(\w+)\|(.+?)\]\]', sub, text)


stage_tabs, stage_sheets, stage_rows = [], [], []
for ci, c in enumerate(CONTRACTS):
    on = ' active' if ci == 0 else ''
    stage_tabs.append(f'<button class="bs-wb-bank-btn lg-ctab{on}" data-k="{c["k"]}">{c["tab"]}</button>')
    flagged = {r[0] for r in c['rows'] if r[7]}
    body = []
    for blk in c['blocks']:
        if blk[0] == 'p':
            body.append(f'<p>{marks(blk[1], flagged)}</p>')
        elif blk[0] == 'h':
            body.append(f'<h5>{blk[1]}</h5>')
        else:
            _, key, a, b = blk
            cells = ''.join(f'<div><i>{x[0]}</i>{x[1]}<br>{x[2]}</div>' for x in (a, b))
            body.append(f'<div class="lg-hl blk" data-f="{key}"><div class="lg-sig">{cells}</div></div>')
    stage_sheets.append(
        f'<div class="lg-sheet{on}" data-k="{c["k"]}" data-file="{c["file"]}">'
        f'<div class="lg-sheet-head"><span>{c["ref"]}</span><span>Page 1 of {c["pages"]}</span></div>'
        f'<h4>{c["title"]}</h4>{"".join(body)}</div>')
    rows = []
    for key, disp, kind, conf, loc, srcq, chk, flag in c['rows']:
        shown = f'"{esc(disp)}"' if kind == 's' else esc(disp)
        chip = f'{conf:.2f} · REVIEW' if flag else f'{conf:.2f}'
        rows.append(
            f'<div class="lg-row show{" flag" if flag else ""}" data-f="{key}" data-conf="{conf}" data-flag="{1 if flag else 0}" '
            f'data-src="{H.escape(srcq, quote=True)}" data-loc="{H.escape(loc, quote=True)}" data-chk="{H.escape(chk, quote=True)}">'
            f'<span class="k">"{key}"</span><span class="v {kind}">{shown}</span><span class="c">{chip}</span></div>')
    stage_rows.append(f'<div class="lg-rows{on}" data-k="{c["k"]}">{"".join(rows)}</div>')

first = CONTRACTS[0]
r0 = first['rows'][0]
stage_html = (
    '<div class="lg-stage" id="lg-stage">'
    f'<div class="lg-stage-bar"><div class="lg-stage-tabs">{"".join(stage_tabs)}</div>'
    '<span class="lg-pill"><i></i><span id="lg-pill-t">Extracting</span></span></div>'
    '<div class="lg-stage-body">'
    f'<div class="lg-paper-pane">{"".join(stage_sheets)}</div>'
    '<div class="lg-json-pane"><div class="lg-json-head"><span>Extracted fields</span><b>Schema valid</b></div>'
    f'{"".join(stage_rows)}'
    '<div class="lg-detail" id="lg-detail">'
    f'<div><span class="l">Source</span><b id="lg-d-src">{esc(r0[5])}</b></div>'
    f'<div><span class="l">Page · box</span><b id="lg-d-loc">{esc(r0[4])}</b></div>'
    f'<div class="chk"><span class="l">Check</span><span id="lg-d-chk">{esc(r0[6])}</span></div></div></div>'
    '<svg class="lg-conn" aria-hidden="true"><path pathLength="1" d=""/><circle r="3.5"/><circle r="3.5"/></svg>'
    '</div>'
    f'<div class="lg-stage-foot"><span id="lg-file">{first["file"]}</span><div class="lg-prog"><i id="lg-prog-bar"></i></div>'
    f'<span><b id="lg-prog-n">{len(first["rows"])} / {len(first["rows"])}</b> fields · avg <b id="lg-prog-c"></b> · illustrative sample</span></div>'
    '</div>')

# ============================================================ CLAUSE LOCATOR DATA
PAPERS = [
    ('Firm A', 'Master Services Agreement',
     [('1', 'Scope of Services'), ('2', 'Compensation & Payment'), ('3', 'Term & Termination'), ('4', 'Confidentiality'),
      ('5', 'Indemnification'), ('6', 'Limitation of Liability'), ('7', 'Force Majeure'), ('8', 'General Provisions')]),
    ('Firm B', 'Professional Services Agreement',
     [('Art. I', 'Definitions'), ('Art. II', 'Services & Deliverables'), ('Art. III', 'Fees'), ('Art. IV', 'Confidential Information'),
      ('Art. V', 'Warranties & Indemnity'), ('Art. VI', 'Liability Limits'), ('Art. VII', 'Early Termination'), ('Art. VIII', 'Events Beyond Control')]),
    ('Firm C', 'Vendor Services Agreement',
     [('9.', 'Deliverables'), ('10.', 'Payment'), ('11.', 'Protection of Information'), ('12.', 'Cancellation and Exit'),
      ('13.', 'Third-Party Claims'), ('14.', 'Cap on Liability'), ('15.', 'Unforeseen Events'), ('16.', 'Notices')]),
]


def hit(sec, conf, quote, out):
    return dict(sec=sec, conf=conf, quote=quote, out=out)


CLAUSES = {
    'termination': dict(label='Termination', hits=[
        hit(2, '0.98', 'Either Party may terminate upon <b>sixty (60) days’ written notice</b>. For material breach, <b>30 days</b> to cure.',
            {'clause': 'termination', 'section_ref': '3', 'notice_days': 60, 'cure_period_days': 30}),
        hit(6, '0.96', 'Either party may end this Agreement on <b>ninety (90) days’ prior written notice</b>, or immediately for uncured breach.',
            {'clause': 'termination', 'section_ref': 'Art. VII', 'notice_days': 90, 'cure_period_days': None}),
        hit(3, '0.97', 'Customer may cancel on <b>30 days’ notice</b>. Supplier’s cure period for breach is <b>15 days</b>.',
            {'clause': 'termination', 'section_ref': '12.', 'notice_days': 30, 'cure_period_days': 15}),
    ]),
    'confidentiality': dict(label='Confidentiality', hits=[
        hit(3, '0.97', 'Confidentiality obligations survive <b>three (3) years</b> after termination.',
            {'clause': 'confidentiality', 'section_ref': '4', 'survival_years': 3, 'perpetual_trade_secrets': False}),
        hit(3, '0.95', 'The Receiving Party shall protect Confidential Information for <b>five (5) years</b> from disclosure.',
            {'clause': 'confidentiality', 'section_ref': 'Art. IV', 'survival_years': 5, 'perpetual_trade_secrets': False}),
        hit(2, '0.96', 'Trade secrets remain protected <b>indefinitely</b>; other information is protected for two years.',
            {'clause': 'confidentiality', 'section_ref': '11.', 'survival_years': 2, 'perpetual_trade_secrets': True}),
    ]),
    'indemnification': dict(label='Indemnification', hits=[
        hit(4, '0.97', 'Provider shall indemnify Client against <b>third-party IP infringement claims</b>.',
            {'clause': 'indemnification', 'section_ref': '5', 'indemnitor': 'Provider', 'scope': 'third-party IP claims'}),
        hit(4, '0.94', 'Each party shall indemnify the other against <b>third-party claims</b> arising from its breach.',
            {'clause': 'indemnification', 'section_ref': 'Art. V', 'indemnitor': 'both parties', 'scope': 'third-party claims from breach'}),
        hit(4, '0.96', 'Supplier indemnifies Customer against claims of <b>bodily injury and IP infringement</b>.',
            {'clause': 'indemnification', 'section_ref': '13.', 'indemnitor': 'Supplier', 'scope': 'bodily injury; IP infringement'}),
    ]),
    'liability': dict(label='Limitation of liability', hits=[
        hit(5, '0.97', 'Aggregate liability is capped at the <b>fees paid in the prior 12 months</b>.',
            {'clause': 'limitation_of_liability', 'section_ref': '6', 'cap_value': 12, 'cap_unit': 'months of fees'}),
        hit(5, '0.95', 'Liability shall not exceed the <b>fees paid in the 6 months</b> preceding the claim.',
            {'clause': 'limitation_of_liability', 'section_ref': 'Art. VI', 'cap_value': 6, 'cap_unit': 'months of fees'}),
        hit(5, '0.96', 'Total liability is limited to <b>USD 500,000</b>.',
            {'clause': 'limitation_of_liability', 'section_ref': '14.', 'cap_value': 500000, 'cap_unit': 'USD'}),
    ]),
    'force_majeure': dict(label='Force majeure', hits=[
        hit(6, '0.96', 'Performance is suspended during a force majeure event; either party may terminate after <b>30 days</b>.',
            {'clause': 'force_majeure', 'section_ref': '7', 'performance_suspended': True, 'termination_right_after_days': 30}),
        hit(7, '0.94', 'Neither party is liable for delay beyond its reasonable control; termination right after <b>60 days</b>.',
            {'clause': 'force_majeure', 'section_ref': 'Art. VIII', 'performance_suspended': True, 'termination_right_after_days': 60}),
        hit(6, '0.95', 'Unforeseen events excuse performance; either party may terminate after <b>45 days</b>.',
            {'clause': 'force_majeure', 'section_ref': '15.', 'performance_suspended': True, 'termination_right_after_days': 45}),
    ]),
}
for cid, cd in CLAUSES.items():
    for h in cd['hits']:
        h['out']['section_ref'] = h['out']['section_ref'].rstrip('.')
    refs = ' · '.join(h['out']['section_ref'] for h in cd['hits'])
    cd['note'] = f'{cd["label"]} sits at {refs}. Same clause, three numbering schemes, found by meaning rather than position.'

DEFAULT_CLAUSE = 'termination'
clause_chips = ''.join(
    f'<button class="lg-chip{" active" if cid == DEFAULT_CLAUSE else ""}" data-c="{cid}">{cd["label"]}</button>'
    for cid, cd in CLAUSES.items())
dflt = CLAUSES[DEFAULT_CLAUSE]
papers_html = ''
for pi, (firm, ptitle, secs) in enumerate(PAPERS):
    h = dflt['hits'][pi]
    rows = ''.join(
        f'<div class="lg-sec{" hit" if si == h["sec"] else ""}" data-i="{si}"><span class="n">{n}</span><span>{esc(t)}</span>'
        f'<span class="m">{"MATCHED " + h["conf"] if si == h["sec"] else "MATCHED"}</span></div>'
        for si, (n, t) in enumerate(secs))
    papers_html += (f'<div class="lg-paper" data-reveal><div class="lg-paper-firm"><span>{firm}</span><span>{len(secs)} sections</span></div>'
                    f'<h3>{ptitle}</h3><div class="lg-secs">{rows}</div>'
                    f'<div class="lg-sec-quote">{h["quote"]}</div><div class="lg-out">{pj(h["out"])}</div></div>')

# ============================================================ AMENDMENT CHAIN
AMEND = [
    dict(tag='Original', date='Apr 18, 2024', title='Master Services Agreement', sub='MSA-2024-0418-NB · Stillwater Robotics, Inc. and Northbridge Studio LLC',
         rec={'document_role': 'original_agreement', 'agreement_reference': 'MSA-2024-0418-NB',
              'effective_date': dt('04/18/2024', '2024-04-18'),
              'parties': ['Stillwater Robotics, Inc.', 'Northbridge Studio LLC'], 'initial_term_months': 24}),
    dict(tag='Amendment 1', date='Sep 3, 2024', title='Payment terms change', sub='Modifies §2 Compensation & Payment',
         rec={'document_role': 'amendment', 'original_agreement_reference': 'MSA-2024-0418-NB',
              'amendment_date': dt('September 3, 2024', '2024-09-03'),
              'modified_clauses': [{'section': '2', 'title': 'Compensation & Payment', 'from': 'Net 30', 'to': 'Net 45'}],
              'new_terms': []}),
    dict(tag='Amendment 2', date='Jan 15, 2025', title='Term extension and data addendum', sub='Modifies §3 and adds Exhibit C',
         rec={'document_role': 'amendment', 'original_agreement_reference': 'MSA-2024-0418-NB',
              'amendment_date': dt('January 15, 2025', '2025-01-15'),
              'modified_clauses': [{'section': '3', 'title': 'Term & Termination', 'from': '24 months', 'to': '36 months'}],
              'new_terms': [{'title': 'Exhibit C: Data Processing Addendum', 'type': 'exhibit'}]}),
]
chain_html = '<span class="lg-chain-fill"></span>' + ''.join(
    f'<button type="button" class="lg-node{" active seen" if i == 0 else ""}" data-rec="{attr(a["rec"])}" data-title="{esc(a["tag"])} · {esc(a["date"])}" data-reveal>'
    f'<div class="t"><span>{esc(a["tag"])}</span><b>{esc(a["date"])}</b></div><h4>{esc(a["title"])}</h4><p>{esc(a["sub"])}</p></button>'
    for i, a in enumerate(AMEND))

# ============================================================ FIELD TABS (from Sensible's "Fields we extract" + FAQ)
FIELD_TABS = [
    ('parties', 'Parties & dates', '01', 8, [
        ('Party names', 'party_a / party_b', 'string', 'Both counterparties, aliased to the roles your CLM expects.', ''),
        ('Party roles', 'party_role', 'string', 'Buyer, seller, licensor, licensee, landlord, tenant. Defined in configuration.', 'Mapped'),
        ('Party addresses', 'party_address', 'string', 'Principal offices as written in the preamble.', ''),
        ('Effective date', 'effective_date', 'date', 'Printed text kept as <code>source</code>; normalized value returned alongside.', 'ISO 8601'),
        ('Execution date', 'execution_date', 'date', 'The date the agreement was signed, when it differs from the effective date.', 'ISO 8601'),
        ('Expiration date', 'expiration_date', 'date', 'Stated end date, or the date implied by the initial term.', 'ISO 8601'),
        ('Governing law', 'governing_law', 'string', 'Jurisdiction whose law governs the agreement.', ''),
        ('Jurisdiction / venue', 'jurisdiction', 'string', 'Courts or forum named for disputes.', ''),
    ]),
    ('financial', 'Financial terms', '02', 8, [
        ('Contract value', 'contract_value', 'currency', 'Total consideration or annual fee, with printed text kept as <code>source</code>.', 'Typed'),
        ('Payment schedule', 'payment_schedule', 'string', 'Net days, milestones, installments, and invoicing cadence.', ''),
        ('Rate / pricing', 'pricing', 'currency', 'Hourly rates, unit prices, and rate cards.', 'Typed'),
        ('Penalties', 'penalties', 'string', 'Late fees, liquidated damages, and service credits.', ''),
        ('Caps', 'liability_cap', 'currency', 'Monetary caps or multiples of fees.', 'Typed'),
        ('Escalation clauses', 'escalation', 'string', 'Annual increases and indexation mechanics.', ''),
        ('Currency', 'currency', 'string', 'Currency the contract is denominated in.', ''),
        ('Tax treatment', 'tax_treatment', 'string', 'Tax responsibilities and gross-up provisions.', ''),
    ]),
    ('clauses', 'Key clauses', '03', 8, [
        ('Termination provisions', 'termination', 'clause', 'Notice period, cure period, and termination rights, wherever they appear.', 'By meaning'),
        ('Renewal terms', 'renewal', 'clause', 'Auto-renewal, renewal length, and the notice window to stop it.', 'By meaning'),
        ('Indemnification', 'indemnification', 'clause', 'Who indemnifies whom, and for what.', 'By meaning'),
        ('Limitation of liability', 'limitation_of_liability', 'clause', 'Caps and exclusions on liability.', 'By meaning'),
        ('Confidentiality', 'confidentiality', 'clause', 'Scope and survival of confidentiality obligations.', 'By meaning'),
        ('IP ownership', 'ip_ownership', 'clause', 'Who owns work product and pre-existing IP.', 'By meaning'),
        ('Non-compete', 'non_compete', 'clause', 'Restrictive covenants and their duration.', 'By meaning'),
        ('Force majeure', 'force_majeure', 'clause', 'Excused events and the resulting termination rights.', 'By meaning'),
    ]),
    ('sign', 'Signatories & amendments', '04', 7, [
        ('Signatory name', 'signatories[].name', 'string', 'Each person who signed, in signature-block order.', ''),
        ('Signatory title', 'signatories[].title', 'string', 'Capacity in which they signed.', ''),
        ('Signature date', 'signatories[].signature_date', 'date', 'Per-signatory date, since counterparties often sign on different days.', 'ISO 8601'),
        ('Original agreement reference', 'original_agreement_reference', 'string', 'The parent contract an amendment modifies.', 'Linked'),
        ('Amendment date', 'amendment_date', 'date', 'When the amendment takes effect.', 'ISO 8601'),
        ('Modified clauses', 'modified_clauses', 'array', 'Each changed provision as a structured change record.', 'Linked'),
        ('New terms', 'new_terms', 'array', 'Provisions and exhibits the amendment adds.', 'Linked'),
    ]),
]
ftabs = ''.join(
    f'<button class="ap-ftab" role="tab" aria-selected="{"true" if i == 0 else "false"}" data-ft="{k}">'
    f'<span class="n">{num}</span><span class="t">{name}</span><span class="c">{n}</span></button>'
    for i, (k, name, num, n, _) in enumerate(FIELD_TABS))
fpanes = ''
for i, (k, name, num, n, rows) in enumerate(FIELD_TABS):
    body = ''.join(
        f'<div class="ap-frow"><div class="ap-fname">{f}</div><div class="ap-fkey"><code>{key}</code><span class="ap-type t-{typ}">{typ}</span></div>'
        f'<div class="ap-fnote">{note}</div><div class="ap-fchk">{f"<span class=ap-chk>{chk}</span>" if chk else ""}</div></div>'
        for f, key, typ, note, chk in rows)
    fpanes += (f'<div class="ap-fpane{" on" if i == 0 else ""}" id="ap-f-{k}" role="tabpanel">'
               f'<div class="ap-frow h"><div>Field</div><div>Schema key</div><div>How Sensible handles it</div><div>Returned as</div></div>{body}</div>')

# ============================================================ PROBLEM CELLS
PROBLEMS = [
    ('01', 'Legal language parsing', 'Contracts mix structured data (party names, dates, amounts) with dense legal prose. LLM reasoning interprets the legal language; SenseML rules extract the specific fields and values your contract management system needs.', 'language'),
    ('02', 'Clause identification', 'Termination, indemnification, confidentiality, force majeure: these clauses appear in varying sections with different numbering schemes. Each clause type is located by semantic meaning, not position, because every firm structures contracts differently.', 'clause'),
    ('03', 'Amendment and addendum linking', 'Original agreement numbers, modified clauses, new terms: amendments reference their parent contract and change specific provisions. Each modification is extracted as a structured change record linked to the original.', 'amend'),
]
problem_cells = ''.join(
    f'<div class="ap-cell" data-reveal><div class="ap-num">{n}</div><h3>{t}</h3><p>{d}</p>{mini(m)}</div>' for n, t, d, m in PROBLEMS)

# ============================================================ VALIDATION CHECKS (illustrative, configured per schema)
CHECKS = (
    '<div class="ap-check"><span class="ic">&#10003;</span><div><b>Dates normalized, source text kept</b><span class="d">Printed &ldquo;04/18/2024&rdquo; returns as 2024-04-18 with the original string preserved alongside</span></div><span class="res">2024-04-18</span></div>'
    '<div class="ap-check"><span class="ic">&#10003;</span><div><b>Preamble parties match the signature blocks</b><span class="d">Both counterparties and both signatories resolve to the same two legal entities</span></div><span class="res" data-count="2" data-suffix=" / 2 parties">2 / 2 parties</span></div>'
    '<div class="ap-check"><span class="ic">&#10003;</span><div><b>Every schema field located</b><span class="d">Termination, payment, renewal, and governing law found in whichever section this counterparty put them</span></div><span class="res" data-count="12" data-suffix=" / 12 fields">12 / 12 fields</span></div>'
    '<div class="ap-check"><span class="ic">&#10003;</span><div><b>Types enforced by your schema</b><span class="d">Notice periods and fees return as numbers and dates as ISO 8601, never as prose</span></div><span class="res">schema valid</span></div>'
    '<div class="ap-check flag"><span class="ic">!</span><div><b>A check that flags</b><span class="d">Governing law is missing from Exhibit B, so the field returns with a low confidence score (0.41) and is routed to human review under your threshold</span></div><span class="res">review flagged</span></div>')

# ============================================================ TYPES
COMMERCIAL = ['MSAs', 'SOWs', 'SaaS / license agreements', 'NDAs', 'Supply agreements', 'Distribution agreements', 'Vendor contracts']
SPECIALIZED = ['Real estate leases', 'Employment agreements', 'Franchise agreements', 'Joint venture agreements', 'Government contracts (FAR/DFARS)']
types_html = (
    '<div class="lg-types" data-reveal>'
    '<div class="lg-type-col"><span class="ap-kicker">Commercial</span><h3>Commercial agreements</h3><p>The workhorse paper of procurement, sales, and partnerships.</p>'
    '<div class="lg-type-list">' + ''.join(f'<span>{t}</span>' for t in COMMERCIAL) + '</div></div>'
    '<div class="lg-type-col"><span class="ap-kicker">Specialized</span><h3>Specialized agreements</h3><p>Longer, more regulated, and less standardized.</p>'
    '<div class="lg-type-list">' + ''.join(f'<span>{t}</span>' for t in SPECIALIZED) + '</div></div></div>')

# ============================================================ USE CASES, SECURITY, MANAGED, RELATED, FAQ
USE_CASES = [
    ('CLM Integration', 'Push schema-validated contract abstracts into your contract lifecycle system instead of re-keying parties, dates, and terms from PDFs.', 'Legal Ops', 'clm'),
    ('Obligation Tracking', 'Turn payment terms, milestones, and notice periods into structured fields an obligation tracker can schedule and alert against.', 'Contract Management', 'obligation'),
    ('Renewal Management', 'Capture auto-renewal terms, notice windows, and expiration dates so renewals surface before the notice deadline passes.', 'Renewals', 'renewal'),
    ('Compliance & Audit', 'Locate required clauses across counterparties, with the page and bounding box behind every value for reviewers and auditors.', 'Risk & Compliance', 'compliance'),
]
usecase_cards = ''.join(
    f'<div class="bs-usecase-card">{icon(ic)}<h3>{t}</h3><p>{d}</p><span class="bs-usecase-tag">{tag}</span></div>' for t, d, tag, ic in USE_CASES)

SECURITY = [
    ('01', 'SOC 2 Type II and HIPAA', 'Sensible is SOC 2 Type II certified and HIPAA compliant, so contracts containing sensitive terms stay inside an audited boundary.', 'shield'),
    ('02', 'Encrypted end to end', 'Data is encrypted in transit and at rest, from the moment a contract hits the API to the moment JSON comes back.', 'lock'),
    ('03', 'Retention you control', 'Document data is stored indefinitely by default. Custom retention policies are available and can be configured for same-day deletion.', 'clock'),
]
security_cells = ''.join(
    f'<div class="ap-cell" data-reveal><div class="ap-num">{n}</div>{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for n, t, d, ic in SECURITY)

MANAGED = [
    ('01', 'Plan', 'Engineers review your samples and pick the right method.', 'plan'),
    ('02', 'Build', 'SenseML configs written from your samples.', 'build'),
    ('03', 'Deploy', 'Same engine as self-serve, ready for production.', 'deploy'),
    ('04', 'Adjust', 'Configs updated when formats shift or new edge cases appear.', 'adjust'),
    ('05', 'Integrate', 'Help with custom integration into your downstream systems.', 'link'),
]
mgd = ''.join(f'<div class="ap-cell" data-reveal><div class="ap-num">{n}</div>{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for n, t, d, ic in MANAGED)

RELATED = [
    ('Corporate Documents (80 pages)', 'See how a compliance startup automated extraction from 80-page corporate documents.', 'contract', 'https://www.sensible.so/blog/how-a-spanish-compliance-startup-automated-extraction-from-80-page-corporate-documents'),
    ('Accounts Payable Invoices', 'Extract vendor headers, multi-line item tables, and tax reconciliations.', 'invoice', 'https://www.sensible.so/solutions'),
    ('Bank Statements', 'Reconciled ledgers and multi-page transaction tables from 150+ institutions.', 'ledger', 'https://www.sensible.so/doc-types/bank-statements'),
    ('ACORD Insurance Certificates', 'Extract policy limits, insured entities, carriers, and expiration dates.', 'acord', 'https://www.sensible.so/solutions'),
    ('All document types', 'Browse the full library of structured and unstructured document types.', 'stack', 'https://www.sensible.so/solutions'),
]
related_cards = ''.join(
    f'<a class="bs-related-card" href="{url}">{icon(ic)}<h4>{t}</h4><p>{d}</p><span class="bs-related-arrow">View &rarr;</span></a>' for t, d, ic, url in RELATED)

FAQ = [
    ('Can Sensible handle contract amendments and addenda?', 'Yes. Sensible processes amendments as standalone documents, extracting the original agreement reference, amendment date, modified clauses, and new terms. Each modification comes back as a structured change record linked to its parent contract.'),
    ('Does Sensible extract key dates and terms from contracts?', 'Effective date, expiration date, renewal terms, notice periods, payment terms, and milestone dates come back by default. Contracts vary widely, so these are examples of what is commonly pulled, not a closed list. The dates and terms you extract are defined in configuration and shaped to your agreement types.'),
    ('What party information does Sensible extract from contracts?', 'Sensible captures party names, roles (buyer, seller, licensor, licensee), addresses, and signatory details including name, title, and signature date. Roles and party fields are defined in configuration, so you extend them for the agreement types you handle rather than mapping to a fixed set.'),
    ('Can Sensible identify specific clauses in contracts?', 'Yes. Sensible locates clause types like indemnification, limitation of liability, termination, confidentiality, non-compete, and force majeure. Those are common examples. The clauses it looks for are defined in configuration, so you add the provisions specific to your contracts when something is not already covered.'),
    ('Does Sensible support human review?', 'Yes. Sensible flags extractions with low confidence for human review. You can configure review thresholds and workflows.'),
    ('How is contract data secured, and how long is it retained?', 'Sensible is SOC 2 Type II certified and HIPAA compliant. Data is encrypted in transit and at rest. Document data is stored indefinitely by default; custom retention policies are available and can be configured for same-day deletion if needed.'),
    ('What file formats does Sensible support?', 'Sensible processes PDFs (native or scanned), Microsoft Word (DOC, DOCX), spreadsheets (XLSX, XLS, CSV), single-page images (JPEG, PNG), multi-page images (TIFF), and email bodies with attachments.'),
    ('How accurate and how fast is contract extraction?', 'Accuracy depends on document quality and configuration. Most production deployments achieve 95%+ accuracy with proper validation rules and confidence signals. Processing speed depends on document size, page count, OCR requirements, and which extraction methods are used. Simple single-page documents process in seconds; larger documents that use LLM-based extraction take longer.'),
    ('How is pricing structured, and is there a free trial?', 'Sensible uses per-document pricing for predictable costs, with no token-based billing or usage surprises. Volume discounts are available for higher throughput. There is a 14-day free trial on the Growth plan, and no credit card is required to start.'),
]
faqs = ''.join(
    f'<details class="ap-q" data-reveal{" open" if i == 0 else ""}><summary>{q}<i>+</i></summary><div class="ap-q-a"><p>{a}</p></div></details>'
    for i, (q, a) in enumerate(FAQ))

LOGOS = ['vouch.svg', 'limit.png', 'ledgebrook.svg', 'obie.svg', 'neptune-flood.svg', 'insurance-quantified.svg',
         'lettuce.svg', 'founder-shield.svg', 'compscience.svg', 'inclined.png', 'sterlingrisk.png']
logo_imgs = ''.join(f'<img src="assets/logos/{f}" alt="">' for f in LOGOS * 2)

# ============================================================ FRAGMENT
fragment = f'''<div class="ap">

  <!-- 1. HERO: SPEC HEADER + INTERACTIVE CONTRACT WORKBENCH -->
  <section class="ap-hero" id="lg-hero">
    <div class="ap-hero-copy">
      <div class="bs-crumbs" data-hero>
        <a href="https://www.sensible.so">Home</a><span class="sep">/</span>
        <a href="https://www.sensible.so/solutions">Solutions</a><span class="sep">/</span>
        <span class="curr">Legal</span>
      </div>
      <span class="ap-tag" data-hero>[ LEGAL · CONTRACT EXTRACTION ]</span>
      <h1 class="ap-h1">Contract data extraction <em>for legal teams</em></h1>
      <p class="ap-lede" data-hero>Turn MSAs, NDAs, leases, and vendor agreements into schema-validated JSON for CLM, obligation tracking, renewals, and compliance.</p>

      <div class="bs-spec-grid" data-hero>
        <div class="bs-spec-card"><div class="bs-spec-label">Doc Type ID</div><div class="bs-spec-val">contract</div></div>
        <div class="bs-spec-card"><div class="bs-spec-label">Contract Types</div><div class="bs-spec-val">MSA, NDA, SaaS, lease</div></div>
        <div class="bs-spec-card"><div class="bs-spec-label">Formats</div><div class="bs-spec-val">PDF, DOCX, TIFF, PNG</div></div>
        <div class="bs-spec-card"><div class="bs-spec-label">Output</div><div class="bs-spec-val">JSON + bounding boxes</div></div>
      </div>

      <div class="ap-btns" data-hero>
        <a class="ap-btn p" href="https://app.sensible.so/register/">Test with your contract</a>
        <a class="ap-btn s" href="#lg-clauses">How clauses are found</a>
      </div>
      <div class="ap-note" data-hero>14-day free trial · No credit card</div>
    </div>

    <div class="ap-hero-panel">
      {hero_rects()}

      {stage_html}
    </div>
  </section>

  <!-- 2. STATS RIBBON + LOGOS -->
  <div class="ap-ribbon"><div class="ap-wrap"><div class="ap-ribbon-grid">
    <div class="ap-ribbon-cell"><p class="ap-ribbon-v">75M+</p><p class="ap-ribbon-l">Documents processed</p></div>
    <div class="ap-ribbon-cell"><p class="ap-ribbon-v">SOC 2 + HIPAA</p><p class="ap-ribbon-l">Certified infrastructure</p></div>
    <div class="ap-ribbon-cell"><p class="ap-ribbon-v">95%+</p><p class="ap-ribbon-l">Typical production accuracy</p></div>
    <div class="ap-ribbon-cell"><p class="ap-ribbon-v">14 days</p><p class="ap-ribbon-l">Free trial · no credit card</p></div>
  </div></div></div>
  <div class="ap-logos"><div class="ap-logos-cap">Trusted by teams turning documents into production data</div><div class="ap-logos-track">{logo_imgs}</div></div>

  <!-- 3. WHY CONTRACTS BREAK STANDARD EXTRACTION -->
  <section class="ap-sec" id="lg-problem">
    <div class="ap-wrap ap-head ap-center" data-reveal>
      <span class="ap-kicker">Why contracts are hard</span>
      <h2 class="ap-h2">Why contracts break standard extraction tools</h2>
      <p class="ap-lede">Long-form legal text, nested clauses, and formatting that changes with every counterparty make contracts a language problem, not a layout one.</p>
    </div>
    <div class="ap-grid ap-g3">{problem_cells}</div>
  </section>

  <!-- 4. HYBRID: LLM READS, SENSEML ENFORCES -->
  <section class="ap-sec ap-band" id="lg-hybrid">
    <div class="ap-wrap">
      <div class="ap-head ap-center" data-reveal>
        <span class="ap-kicker">Under the hood</span>
        <h2 class="ap-h2">The LLM reads the clause. <em>SenseML enforces your schema.</em></h2>
        <p class="ap-lede">Hybrid extraction handles the range of legal writing styles while deterministic rules enforce your contract data schema.</p>
      </div>
      <div class="bs-cmp-wrap" data-reveal>
        <div class="bs-cmp-list">
          <div class="bs-cmp-item"><span class="bullet">1</span><div><b>LLM reasoning for legal language</b><p>Dense prose is interpreted by an LLM, so a clause is understood even when it is phrased in a way no template anticipated.</p></div></div>
          <div class="bs-cmp-item"><span class="bullet">2</span><div><b>Deterministic rules for the schema</b><p>SenseML rules extract the specific fields and values your contract management system needs, and the output is schema-enforced.</p></div></div>
          <div class="bs-cmp-item"><span class="bullet">3</span><div><b>Source coordinates on every value</b><p>Every value links back to its page and bounding box, so legal reviewers can audit it against the original document.</p></div></div>
        </div>
        <div style="text-align:center;">{hybrid_art()}</div>
      </div>
    </div>
  </section>

  <!-- 5. CLAUSE LOCATOR (interactive) -->
  <section class="ap-sec" id="lg-clauses">
    <div class="ap-wrap">
      <div class="ap-head ap-center" data-reveal>
        <span class="ap-kicker">Clause identification</span>
        <h2 class="ap-h2">Same clause, three numbering schemes. <em>One structured record.</em></h2>
        <p class="ap-lede">Pick a clause type and watch it get located in three differently structured agreements. Each match is by meaning, not by section number.</p>
      </div>
      <div class="lg-clause-wrap">
        <div class="lg-chips" data-reveal>{clause_chips}</div>
        <div class="lg-papers" data-clauses="{attr(CLAUSES)}">{papers_html}</div>
        <p class="lg-clause-note" id="lg-clause-note">{esc(dflt['note'])} Illustrative agreements.</p>
      </div>
    </div>
  </section>

  <!-- 6. AMENDMENT LINKING (interactive) -->
  <section class="ap-sec ap-band" id="lg-amend">
    <div class="ap-wrap">
      <div class="lg-amend">
        <div>
          <div data-reveal>
            <span class="ap-kicker">Amendment and addendum linking</span>
            <h2 class="ap-h2">Amendments come back as <em>change records</em></h2>
            <p class="ap-lede" style="margin-top:20px;margin-bottom:34px;">An amendment names its parent and changes specific provisions. Sensible extracts the original agreement reference, the amendment date, the modified clauses, and the new terms, so your system can follow the chain.</p>
          </div>
          <div class="lg-chain">{chain_html}</div>
        </div>
        <div class="lg-rec" data-reveal>
          <div class="lg-rec-bar"><span id="lg-rec-title">{esc(AMEND[0]['tag'])} · {esc(AMEND[0]['date'])}</span><b>extract.json</b></div>
          <div class="lg-rec-body">{pj(AMEND[0]['rec'])}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- 7. FIELDS EXPLORER -->
  <section class="ap-sec" id="lg-fields">
    <div class="ap-wrap"><div class="ap-fields">
      <div class="ap-fields-nav" data-reveal>
        <span class="ap-kicker">Data dictionary</span>
        <h2 class="ap-h2">Fields we extract</h2>
        <p class="ap-lede">Every contract is different, so the config is built around your exact schema rather than a fixed list. These are the fields legal and ops teams request most.</p>
        <div class="ap-ftabs" role="tablist" aria-label="Field groups">{ftabs}</div>
        <div class="lg-schem-wrap">{schem()}</div>
      </div>
      <div data-reveal>
        {fpanes}
        <div class="ap-more"><b>Mapped to your schema.</b><span>Whatever else your contract-management system needs gets added in configuration, not in a fixed template.</span></div>
      </div>
    </div></div>
  </section>

  <!-- 8. VALIDATION + REVIEW -->
  <section class="ap-sec ap-band" id="lg-validation">
    <div class="ap-wrap">
      <div class="ap-val">
        <div data-reveal>
          <span class="ap-kicker">Validation and review</span>
          <h2 class="ap-h2">How every contract is checked before it reaches your CLM</h2>
          <p class="ap-lede">Extractions are returned against your schema, and Sensible flags low-confidence results for human review. You configure the review thresholds and workflows, so a reviewer only opens the contracts that need one.</p>
        </div>
        <div class="ap-checks"><div class="ap-checks-h"><span>Example checks</span><span>MSA-2024-0418-NB</span></div>{CHECKS}</div>
      </div>
      <div class="ap-quote">
        <div><span class="ap-kicker">Our view</span></div>
        <blockquote><p class="ap-qtext">Contracts are a language problem, not a layout one.</p><cite>Sensible</cite></blockquote>
      </div>
    </div>
  </section>

  <!-- 9. CONTRACT TYPES -->
  <section class="ap-sec" id="lg-types">
    <div class="ap-wrap">
      <div class="ap-head ap-center" data-reveal>
        <span class="ap-kicker">Supported contract types</span>
        <h2 class="ap-h2">From SaaS agreements to FAR/DFARS contracts</h2>
        <p class="ap-lede">Sensible processes SaaS, employment, NDA, lease, vendor, and specialty contracts.</p>
      </div>
      {types_html}
      <p class="lg-type-foot" data-reveal>Hybrid extraction handles the range of legal writing styles, while deterministic rules enforce your contract data schema.</p>
    </div>
  </section>

  <!-- 10. USE CASES -->
  <section class="ap-sec ap-band" id="lg-usecases">
    <div class="ap-wrap">
      <div class="ap-head ap-center" data-reveal>
        <span class="ap-kicker">Use cases</span>
        <h2 class="ap-h2">Structured contract data for the work legal teams repeat</h2>
        <p class="ap-lede">CLM integration, obligation tracking, renewal management, and compliance, all from the same validated JSON.</p>
      </div>
      <div class="bs-usecase-grid" data-reveal>{usecase_cards}</div>
    </div>
  </section>

  <!-- 11. SECURITY + PRICING -->
  <section class="ap-sec" id="lg-security">
    <div class="ap-wrap ap-head ap-center" data-reveal>
      <span class="ap-kicker">Built for confidential documents</span>
      <h2 class="ap-h2">Contracts are sensitive. The platform treats them that way.</h2>
      <p class="ap-lede">Certified infrastructure, encryption in transit and at rest, and retention policies you set.</p>
    </div>
    <div class="ap-grid ap-g3 lg-sec3">{security_cells}</div>
    <div class="ap-wrap">
      <div class="lg-trial" data-reveal>
        <div><b>14-day free trial</b><span>On the Growth plan. No credit card required to start.</span></div>
        <div><b>Per-document pricing</b><span>Predictable cost with no token-volatility surprises. Volume discounts for higher throughput.</span></div>
        <div><b>Integrates in hours</b><span>REST APIs and SDKs for Python and Node.js. Webhooks, Zapier, and direct API calls are all supported.</span></div>
      </div>
    </div>
  </section>

  <!-- 12. SELF-SERVE OR MANAGED -->
  <section class="ap-sec ap-mgd ap-band" id="lg-managed">
    <div class="ap-wrap ap-head ap-center" data-reveal>
      <span class="ap-kicker">Managed services</span>
      <h2 class="ap-h2">Don&rsquo;t want to build it? <em>We&rsquo;ll write your configs from your samples.</em></h2>
      <p class="ap-lede">Solutions engineers handle plan, build, deploy, and adjust on your behalf. You see clean JSON in your API response. Same engine as self-serve, just with the configuration work outsourced.</p>
      <div class="ap-btns"><a class="ap-btn p" href="https://www.sensible.so/managed-services">See managed services</a><a class="ap-btn s" href="https://www.sensible.so/meeting">Talk to our team</a></div>
    </div>
    <div class="ap-grid ap-g5">{mgd}</div>
  </section>

  <!-- 14. RELATED -->
  <section class="ap-sec ap-band" id="lg-related">
    <div class="ap-wrap">
      <div class="ap-head ap-center" data-reveal>
        <span class="ap-kicker">Document type library</span>
        <h2 class="ap-h2">Explore related document types</h2>
        <p class="ap-lede">Sensible supports hundreds of structured and unstructured document types across lending, insurance, legal, and accounting.</p>
      </div>
      <div class="bs-related-grid" data-reveal>{related_cards}</div>
    </div>
  </section>

  <!-- 15. FAQ -->
  <section class="ap-sec" id="lg-faq">
    <div class="ap-wrap"><div class="ap-faq">
      <div class="ap-faq-head" data-reveal>
        <span class="ap-kicker">Common questions</span>
        <h2 class="ap-h2">Questions from legal and ops teams</h2>
        <p class="ap-lede">Amendments, clause identification, human review, security, and pricing.</p>
      </div>
      <div class="ap-faq-list">{faqs}</div>
    </div></div>
  </section>

</div>'''

os.makedirs('out', exist_ok=True)
open('out/fragment.html', 'w').write(fragment)

# ============================================================ STANDALONE PAGE
base_css = L(20, 249)
cta_footer_css = L(998, 1160)
nav_html = full[full.index('<!-- Navbar -->'):full.index('<!-- 1. HERO FOLD')]
cta_html = full[full.index('<section class="cta-banner">'):full.index('</footer>') + len('</footer>')]
site_extra = '''
    @media (max-width: 991px) { .footer-grid { grid-template-columns: 1fr 1fr; gap: 32px 24px; } }
    @media (max-width: 860px) { .navbar-inner { height: 60px; } .nav-links { display: none; } .nav-cta-group { display: none !important; } .mobile-toggle { display: block; } }
    @media (max-width: 767px) { .container { padding: 0 20px; } .cta-h2 { font-size: 28px; } .cta-banner { padding: 56px 24px; }
      .footer { padding: 64px 0 40px; } .footer-grid { grid-template-columns: 1fr; gap: 40px; padding-bottom: 40px; } .footer-bottom { flex-direction: column; align-items: flex-start; } }
    @media (max-width: 480px) { .nav-logo img { height: 22px !important; } }
    .sensible-font { font-family: 'Matter SQ', var(--font-sans); font-weight: 500; }
'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Contract Data Extraction for Legal Teams | Sensible</title>
  <meta name="description" content="Extract parties, dates, financial terms, and key clauses from MSAs, NDAs, leases, and vendor agreements into schema-validated JSON with page and bounding-box evidence. Amendment linking, human review, SOC 2 Type II."/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"/>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet"/>
  <script>document.documentElement.classList.add('ap-js')</script>
  <style>
{base_css}
{cta_footer_css}
{site_extra}
{ap_css}
{bs_css}
{lg_css}
  </style>
</head>
<body>
{nav_html}
{fragment}
{cta_html}
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
<script>
{lg_js}
</script>
</body>
</html>
'''
os.makedirs('../site', exist_ok=True)
open('../site/legal.html', 'w').write(page)
print('Generated: build/out/fragment.html, site/legal.html')
