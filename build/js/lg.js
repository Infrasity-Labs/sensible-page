/* Sensible /solutions/legal: interactions + GSAP motion (needs GSAP + ScrollTrigger) */
(function () {
  'use strict';
  var root = document.querySelector('.ap');
  if (!root) return;
  var $ = function (s, c) { return (c || root).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || root).querySelectorAll(s)); };
  var html = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  /* tiny JSON pretty printer with the .k/.s/.n/.c classes used by the dark code panels */
  function pretty(v, ind) {
    ind = ind || 0;
    var pad = new Array(ind + 3).join(' '), end = new Array(ind + 1).join(' ');
    if (v === null) return '<span class="n">null</span>';
    if (typeof v === 'string') return '<span class="s">"' + esc(v) + '"</span>';
    if (typeof v === 'number' || typeof v === 'boolean') return '<span class="n">' + v + '</span>';
    if (Array.isArray(v)) {
      if (!v.length) return '[]';
      return '[\n' + v.map(function (x) { return pad + pretty(x, ind + 2); }).join(',\n') + '\n' + end + ']';
    }
    var keys = Object.keys(v);
    return '{\n' + keys.map(function (k) { return pad + '<span class="k">"' + esc(k) + '"</span>: ' + pretty(v[k], ind + 2); }).join(',\n') + '\n' + end + '}';
  }

  /* ================= Hero stage: live extraction ================= */
  var stage = $('#lg-stage');
  var timers = [], spot = null, sIdx = 0;
  function clearAll() { timers.forEach(clearTimeout); timers = []; clearInterval(spot); spot = null; }
  function later(fn, ms) { timers.push(setTimeout(fn, ms)); }
  function rowsEl() { return $('.lg-rows.active'); }
  function rowList() { return $$('.lg-row', rowsEl()); }
  function markFor(key) { return $('.lg-sheet.active .lg-hl[data-f="' + key + '"]'); }

  function drawConn(row, mark) {
    var svg = $('.lg-conn'); if (!svg) return;
    if (!row || !mark || window.innerWidth < 992) { svg.classList.remove('on'); return; }
    var body = $('.lg-stage-body').getBoundingClientRect();
    var rects = mark.getClientRects(), m = rects[rects.length - 1];
    if (!m) { svg.classList.remove('on'); return; }
    var r = row.getBoundingClientRect();
    var x1 = m.right - body.left, y1 = m.top + m.height / 2 - body.top;
    var x2 = r.left - body.left, y2 = r.top + 14 - body.top;
    var dx = Math.max(36, (x2 - x1) * 0.5);
    $('path', svg).setAttribute('d', 'M' + x1 + ' ' + y1 + ' C' + (x1 + dx) + ' ' + y1 + ' ' + (x2 - dx) + ' ' + y2 + ' ' + x2 + ' ' + y2);
    var c = $$('circle', svg);
    c[0].setAttribute('cx', x1); c[0].setAttribute('cy', y1); c[1].setAttribute('cx', x2); c[1].setAttribute('cy', y2);
    svg.classList.toggle('warn', row.dataset.flag === '1');
    svg.classList.remove('on'); void svg.getBoundingClientRect(); svg.classList.add('on');
  }

  function setActive(i) {
    var rows = rowList(); if (!rows.length) return;
    sIdx = i;
    rows.forEach(function (r, j) {
      r.classList.toggle('active', j === i);
      var m = markFor(r.dataset.f); if (m) m.classList.toggle('active', j === i);
    });
    var row = rows[i];
    var det = $('#lg-detail');
    $('#lg-d-src').textContent = row.dataset.src;
    $('#lg-d-loc').textContent = row.dataset.loc;
    $('#lg-d-chk').textContent = row.dataset.chk;
    det.classList.toggle('flag', row.dataset.flag === '1');
    drawConn(row, markFor(row.dataset.f));
  }

  function progress(n) {
    var rows = rowList(), total = rows.length, sum = 0;
    for (var i = 0; i < n; i++) sum += parseFloat(rows[i].dataset.conf);
    $('#lg-prog-n').textContent = n + ' / ' + total;
    $('#lg-prog-c').textContent = n ? (sum / n).toFixed(2) : '0.00';
    $('#lg-prog-bar').style.width = (total ? n / total * 100 : 0) + '%';
  }

  function finish() {
    stage.classList.add('done');
    $('#lg-pill-t').textContent = 'Complete';
    var rows = rowList();
    rows.forEach(function (r) { r.classList.add('show'); var m = markFor(r.dataset.f); if (m) m.classList.add('seen'); });
    progress(rows.length);
  }

  function startSpot() {
    if (reduce) return;
    clearInterval(spot);
    spot = setInterval(function () { setActive((sIdx + 1) % rowList().length); }, 2600);
  }

  function reset() {
    clearAll();
    stage.classList.remove('done');
    stage.classList.add('lg-anim');
    $('#lg-pill-t').textContent = 'Extracting';
    $$('.lg-row', stage).forEach(function (r) { r.classList.remove('show', 'active'); });
    $$('.lg-hl', stage).forEach(function (h) { h.classList.remove('seen', 'active'); });
    var svg = $('.lg-conn'); if (svg) svg.classList.remove('on');
    progress(0);
  }

  function playStage() {
    reset();
    var rows = rowList();
    rows.forEach(function (r, i) {
      later(function () {
        r.classList.add('show');
        var m = markFor(r.dataset.f); if (m) m.classList.add('seen');
        setActive(i);
        progress(i + 1);
      }, 450 + i * 620);
    });
    later(function () { finish(); startSpot(); }, 450 + rows.length * 620 + 250);
  }

  function userTakesOver(i) {
    if (!stage.classList.contains('done')) { clearAll(); finish(); } else { clearInterval(spot); spot = null; }
    setActive(i);
  }

  var started = false;
  function startAuto() {
    if (started) return;
    started = true;
    if (reduce) { finish(); setActive(0); return; }
    playStage();
  }

  $$('.lg-ctab').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var k = btn.dataset.k;
      $$('.lg-ctab').forEach(function (b) { b.classList.toggle('active', b === btn); });
      $$('.lg-sheet').forEach(function (s) { s.classList.toggle('active', s.dataset.k === k); });
      $$('.lg-rows').forEach(function (s) { s.classList.toggle('active', s.dataset.k === k); });
      var sh = $('.lg-sheet.active'); if (sh) $('#lg-file').textContent = sh.dataset.file;
      started = true;
      if (reduce) { finish(); setActive(0); } else { playStage(); }
    });
  });
  $$('.lg-row').forEach(function (row) {
    row.addEventListener('mouseenter', function () { if (stage.classList.contains('lg-anim') && !row.classList.contains('show')) return; userTakesOver(rowList().indexOf(row)); });
  });
  $$('.lg-hl').forEach(function (h) {
    h.addEventListener('mouseenter', function () {
      var rows = rowList(), i = rows.findIndex(function (r) { return r.dataset.f === h.dataset.f; });
      if (i >= 0) userTakesOver(i);
    });
  });
  if (stage) stage.addEventListener('mouseleave', function () { if (stage.classList.contains('done')) startSpot(); });
  window.addEventListener('resize', function () { if (stage.classList.contains('done')) setActive(sIdx); });
  /* prepare the build-up state before first paint when motion is allowed */
  if (stage && !reduce) { reset(); }

  /* ================= Clause locator ================= */
  var papers = $('.lg-papers');
  var clauseData = {};
  if (papers) { try { clauseData = JSON.parse(papers.getAttribute('data-clauses')); } catch (e) {} }
  var clauseTimer = null, clauseTouched = false;
  function setClause(id, animate) {
    var d = clauseData[id]; if (!d) return;
    $$('.lg-chip').forEach(function (c) { c.classList.toggle('active', c.dataset.c === id); });
    $$('.lg-paper').forEach(function (p, i) {
      var hit = d.hits[i];
      $$('.lg-sec', p).forEach(function (s) { s.classList.toggle('hit', s.dataset.i === String(hit.sec)); });
      var q = $('.lg-sec-quote', p); if (q) q.innerHTML = hit.quote;
      var o = $('.lg-out', p); if (o) o.innerHTML = pretty(hit.out);
      var m = $('.lg-sec.hit .m', p); if (m) m.textContent = 'MATCHED ' + hit.conf;
    });
    var note = $('#lg-clause-note');
    if (note) note.textContent = d.note;
    if (animate && window.gsap && !reduce) {
      gsap.fromTo($$('.lg-sec.hit'), { x: -8 }, { x: 0, duration: .5, ease: 'power3.out', stagger: .08 });
      gsap.fromTo($$('.lg-out'), { opacity: .35 }, { opacity: 1, duration: .5, ease: 'power2.out', stagger: .08 });
    }
  }
  $$('.lg-chip').forEach(function (c) {
    c.addEventListener('click', function () { clauseTouched = true; clearInterval(clauseTimer); setClause(c.dataset.c, true); });
  });
  function startClauseAuto() {
    if (reduce || clauseTimer) return;
    var ids = $$('.lg-chip').map(function (c) { return c.dataset.c; });
    var i = 0;
    clauseTimer = setInterval(function () {
      if (clauseTouched) { clearInterval(clauseTimer); return; }
      i = (i + 1) % ids.length; setClause(ids[i], true);
    }, 3600);
  }

  /* ================= Amendment chain ================= */
  var nodes = $$('.lg-node');
  var recBody = $('.lg-rec-body'), recTitle = $('#lg-rec-title');
  var chainTimer = null, chainTouched = false;
  function setNode(i, animate) {
    nodes.forEach(function (n, j) { n.classList.toggle('active', j === i); n.classList.toggle('seen', j <= i); });
    var n = nodes[i]; if (!n || !recBody) return;
    var rec; try { rec = JSON.parse(n.getAttribute('data-rec')); } catch (e) { return; }
    recBody.innerHTML = pretty(rec);
    if (recTitle) recTitle.textContent = n.getAttribute('data-title');
    var fill = $('.lg-chain-fill');
    if (fill) {
      var chain = $('.lg-chain');
      var target = n.offsetTop + n.offsetHeight / 2 - 26;
      if (window.gsap && !reduce) gsap.to(fill, { height: Math.max(0, target), duration: .6, ease: 'power2.inOut' });
      else fill.style.height = Math.max(0, target) + 'px';
    }
    if (animate && window.gsap && !reduce) gsap.fromTo(recBody, { opacity: .3, y: 8 }, { opacity: 1, y: 0, duration: .5, ease: 'power2.out' });
  }
  nodes.forEach(function (n, i) {
    n.addEventListener('click', function () { chainTouched = true; clearInterval(chainTimer); setNode(i, true); });
  });
  function startChainAuto() {
    if (reduce || chainTimer || !nodes.length) return;
    var i = 0; setNode(0, true);
    chainTimer = setInterval(function () {
      if (chainTouched) { clearInterval(chainTimer); return; }
      i = (i + 1) % nodes.length; setNode(i, true);
    }, 3400);
  }

  /* ================= Field explorer, API tabs, FAQ ================= */
  $$('.ap-ftab').forEach(function (t) {
    t.addEventListener('click', function () {
      $$('.ap-ftab').forEach(function (x) { x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
      $$('.ap-fpane').forEach(function (p) { p.classList.toggle('on', p.id === 'ap-f-' + t.dataset.ft); });
      var sc = $('.lg-schem'); if (sc) sc.dataset.active = t.dataset.ft;
    });
  });
  $$('.ap-q').forEach(function (q) {
    q.addEventListener('toggle', function () {
      if (q.open) $$('.ap-q').forEach(function (o) { if (o !== q && o.open) o.open = false; });
    });
  });

  /* ================= GSAP ================= */
  if (!window.gsap || !window.ScrollTrigger || reduce) {
    html.classList.remove('ap-js');
    startAuto(); startClauseAuto(); startChainAuto();
    return;
  }
  gsap.registerPlugin(ScrollTrigger);

  function splitWords(el) {
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'ap-w';
            var i = document.createElement('span'); i.textContent = part; w.appendChild(i);
            frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1) { walk(n); }
      });
    })(el);
  }

  var h1 = $('.ap-h1');
  if (h1) {
    splitWords(h1);
    gsap.set(h1, { opacity: 1 });
    var hrs = $$('.ap-hr');
    var intro = gsap.timeline({ defaults: { ease: 'power3.out' } });
    intro
      .from($$('.ap-h1 .ap-w > span'), { yPercent: 115, duration: 1, stagger: 0.05 }, 0.05)
      .fromTo($$('[data-hero]'), { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 0.8, stagger: 0.1 }, 0.1)
      .from(hrs, { opacity: 0, scale: 0.88, transformOrigin: '100% 0%', duration: 1.1, stagger: 0.12 }, 0.1)
      .from($('.lg-stage'), { y: 48, opacity: 0, duration: 1.0 }, 0.3)
      .add(function () { startAuto(); }, 1.3);
    gsap.to(hrs, { y: '+=10', duration: 4.2, repeat: -1, yoyo: true, ease: 'sine.inOut', stagger: { each: 0.4, from: 'end' } });
  }

  ScrollTrigger.batch('[data-reveal]', {
    start: 'top 89%', once: true,
    onEnter: function (els) { gsap.to(els, { opacity: 1, y: 0, duration: 0.85, stagger: 0.09, ease: 'power3.out', overwrite: true }); }
  });

  /* clause locator + amendment chain start when they scroll into view */
  if (papers) ScrollTrigger.create({ trigger: papers, start: 'top 75%', once: true, onEnter: function () { setClause($('.lg-chip.active').dataset.c, true); startClauseAuto(); } });
  if (nodes.length) ScrollTrigger.create({ trigger: '.lg-amend', start: 'top 70%', once: true, onEnter: startChainAuto });

  /* validation rows: stagger in, tick pops, numbers count up */
  var rows = $$('.ap-check');
  if (rows.length) {
    gsap.set(rows, { opacity: 0, y: 14 });
    var icons = rows.map(function (r) { return $('.ic', r); });
    gsap.set(icons, { scale: 0 });
    var vt = gsap.timeline({ scrollTrigger: { trigger: '.ap-checks', start: 'top 78%', once: true } });
    rows.forEach(function (r, i) {
      vt.to(r, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, i * 0.38)
        .to(icons[i], { scale: 1, duration: 0.45, ease: 'back.out(2.6)' }, i * 0.38 + 0.15);
      var res = $('.res[data-count]', r);
      if (res) {
        var target = parseFloat(res.dataset.count), suffix = res.dataset.suffix || '', o = { v: 0 };
        vt.to(o, { v: target, duration: 0.9, ease: 'power2.out', onUpdate: function () {
          res.textContent = Math.round(o.v) + suffix;
        } }, i * 0.38 + 0.1);
      }
    });
    vt.fromTo('.ap-check.flag', { backgroundColor: '#FFE3B8' }, { backgroundColor: '#FFF7EA', duration: 1.1, repeat: 1, yoyo: true }, '>-0.3');
  }

  /* contract-type chips pop in */
  $$('.lg-type-list').forEach(function (list) {
    gsap.from($$('span', list), { opacity: 0, y: 12, scale: .94, duration: .45, ease: 'back.out(1.8)', stagger: .06,
      scrollTrigger: { trigger: list, start: 'top 88%', once: true } });
  });

  /* quote: words fade in with scroll */
  var q = $('.ap-qtext');
  if (q) {
    splitWords(q);
    var words = $$('.ap-w', q);
    words.forEach(function (w) { w.style.overflow = 'visible'; });
    gsap.fromTo(words, { opacity: 0.16 }, { opacity: 1, ease: 'none', stagger: 0.12,
      scrollTrigger: { trigger: '.ap-quote', start: 'top 72%', end: 'bottom 62%', scrub: true } });
  }

  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
