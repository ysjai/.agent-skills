/* ============================================================
   deck.js — 运行时外壳
   负责：品牌注入 / 缩放自适应 / 翻页 / 点位 / 目录缩略图 / 全屏放映
   页面本身只写 section.slide，不再关心导航。
   ============================================================ */
(function () {
  const CFG = window.DECK || {};
  const stage = document.getElementById('stage');
  if (!stage) return;

  const slides = Array.from(stage.querySelectorAll(':scope > .slide'));
  const total = slides.length;
  if (!total) return;

  const clean = t => (t || '').replace(/\s+/g, ' ').trim();
  const titles = slides.map((s, i) => {
    if (s.classList.contains('cover')) return '封面';
    const t = s.querySelector('.title');
    return clean(t && t.textContent) || ('第 ' + (i + 1) + ' 页');
  });

  let cur = 0;
  let presenting = false, idleTimer = null, lastMove = 0;

  /* ---------- 品牌 ---------- */
  const brandList = (Array.isArray(CFG.brand) ? CFG.brand : []).filter(b => b && b.src);
  function makeBrand(cls) {
    const el = document.createElement('div');
    el.className = 'brand ' + cls;
    brandList.forEach((b, i) => {
      if (i > 0) { const s = document.createElement('span'); s.className = 'sep'; el.appendChild(s); }
      const img = document.createElement('img');
      img.src = b.src;
      img.alt = b.alt || '';
      el.appendChild(img);
    });
    return el;
  }
  const cover = slides.find(s => s.classList.contains('cover'));
  const brandline = cover && cover.querySelector('.brandline');
  if (brandList.length) {
    slides.forEach(s => { if (!s.classList.contains('cover')) s.appendChild(makeBrand('head')); });
    if (brandline) brandline.insertBefore(makeBrand('cover'), brandline.firstChild);
    measureBrand();
    window.addEventListener('load', measureBrand);
  } else {
    document.documentElement.style.setProperty('--brand-w', '0px');
  }
  /* 没有 logo 也没有品牌行文案时，整行不占位 */
  if (brandline && !brandline.querySelector('img') && !clean(brandline.textContent)) {
    brandline.style.display = 'none';
  }

  /* 页脚来源行没写文案时，连圆点一起去掉，只留页码 */
  document.querySelectorAll('.foot .fl').forEach(el => {
    if (!clean(el.textContent)) el.remove();
  });

  /* 按 logo 实际宽高比算出占位宽度，供标题区留白，避免长 kicker 压到 logo */
  function measureBrand() {
    const host = document.querySelector('.slide:not(.cover) .brand.head');
    if (!host) return;
    const h = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--brand-h')) || 28;
    const gap = parseFloat(getComputedStyle(host).columnGap) || 13;
    const step = gap * 2 + 3; /* 两个 logo 之间：gap + 分隔线(1px) + 两侧各 1px */
    let total = 0;
    host.querySelectorAll('img').forEach((img, i) => {
      const ratio = img.naturalWidth && img.naturalHeight ? img.naturalWidth / img.naturalHeight : 2.4;
      total += ratio * h + (i ? step : 0);
    });
    if (total) document.documentElement.style.setProperty('--brand-w', Math.ceil(total) + 'px');
  }

  /* ---------- 外壳 DOM ---------- */
  const prog = document.createElement('div');
  prog.className = 'progress';
  prog.id = 'progress';
  document.body.insertBefore(prog, document.body.firstChild);

  const nav = document.createElement('div');
  nav.className = 'nav';
  nav.id = 'nav';
  nav.innerHTML =
    '<button class="arrow" id="prev" type="button" title="上一页 ←" aria-label="上一页">‹</button>' +
    '<div class="dots" id="dots"></div>' +
    '<button class="arrow" id="next" type="button" title="下一页 →" aria-label="下一页">›</button>' +
    '<span class="cnt" id="cnt" aria-live="polite"><b>01</b><i>/</i><em>01</em></span>' +
    '<span class="sep"></span>' +
    '<button class="fs" id="fs" type="button" title="全屏播放 (F)" aria-label="全屏播放">' +
    '<svg class="ico-expand" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3.4H3.4V9"/><path d="M15 3.4h5.6V9"/><path d="M20.6 15v5.6H15"/><path d="M3.4 15v5.6H9"/></svg>' +
    '<svg class="ico-compress" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3.4 9H9V3.4"/><path d="M20.6 9H15V3.4"/><path d="M15 20.6V15h5.6"/><path d="M9 20.6V15H3.4"/></svg>' +
    '</button>';
  document.body.appendChild(nav);

  const tipEl = document.createElement('div');
  tipEl.className = 'tip';
  document.body.appendChild(tipEl);

  const tocTab = document.createElement('button');
  tocTab.className = 'toc-tab';
  tocTab.id = 'tocTab';
  tocTab.type = 'button';
  tocTab.title = '目录 (T)';
  tocTab.setAttribute('aria-label', '展开或收起目录');
  tocTab.innerHTML =
    '<svg class="ico-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">' +
    '<path d="M8.5 6h12.5M8.5 12h12.5M8.5 18h12.5"/>' +
    '<circle cx="3.8" cy="6" r="1.15" fill="currentColor" stroke="none"/>' +
    '<circle cx="3.8" cy="12" r="1.15" fill="currentColor" stroke="none"/>' +
    '<circle cx="3.8" cy="18" r="1.15" fill="currentColor" stroke="none"/></svg>' +
    '<svg class="ico-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M15 4.5 7.5 12l7.5 7.5"/></svg>';
  document.body.appendChild(tocTab);

  const tocEl = document.createElement('aside');
  tocEl.className = 'toc';
  tocEl.id = 'toc';
  tocEl.setAttribute('aria-label', '页面目录');
  tocEl.innerHTML = '<div class="toc-list" id="tocList"></div>';
  document.body.appendChild(tocEl);

  const dotsEl = document.getElementById('dots');
  const tocList = document.getElementById('tocList');
  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');
  const fsBtn = document.getElementById('fs');
  const cntEl = document.getElementById('cnt');
  const cntCur = cntEl.querySelector('b');
  const cntAll = cntEl.querySelector('em');
  const PAD = Math.max(2, String(total).length);
  cntAll.textContent = String(total).padStart(PAD, '0');

  /* ---------- 点位：首页 + 4 个等分 + 末页 ---------- */
  const ANCHORS = 5;
  const anchorPages = [];
  for (let k = 0; k <= ANCHORS; k++) {
    const p = 1 + Math.round((total - 1) * k / ANCHORS);
    if (anchorPages[anchorPages.length - 1] !== p) anchorPages.push(p);
  }
  anchorPages.forEach(p => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'ndot';
    b.setAttribute('aria-label', '跳转到第 ' + p + ' 页：' + titles[p - 1]);
    b.addEventListener('click', () => { go(p - 1); hideTip(); });
    b.addEventListener('mouseenter', () => showTip(p - 1, b));
    b.addEventListener('mouseleave', hideTip);
    dotsEl.appendChild(b);
  });
  const dotEls = Array.from(dotsEl.children);

  /* ---------- 缩略图目录 ---------- */
  const tocItems = slides.map((s, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'toc-item';
    b.setAttribute('aria-label', '第 ' + (i + 1) + ' 页：' + titles[i]);
    b.title = '第 ' + (i + 1) + ' 页 · ' + titles[i];
    const num = document.createElement('span');
    num.className = 'toc-num';
    num.textContent = String(i + 1).padStart(PAD, '0');
    const th = document.createElement('span');
    th.className = 'toc-thumb';
    const clone = s.cloneNode(true);
    clone.classList.add('active');
    clone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
    th.appendChild(clone);
    b.appendChild(num);
    b.appendChild(th);
    b.addEventListener('click', () => go(i));
    tocList.appendChild(b);
    return b;
  });

  tocList.addEventListener('scroll', () => {
    tocEl.classList.toggle('at-end', tocList.scrollTop + tocList.clientHeight >= tocList.scrollHeight - 3);
  });

  function setToc(open) {
    tocEl.classList.toggle('open', open);
    tocTab.classList.toggle('on', open);
    document.body.classList.toggle('toc-open', open);
    fit();
    if (!open) return;
    const it = tocItems[cur];
    if (it) {
      const lr = tocList.getBoundingClientRect(), ir = it.getBoundingClientRect();
      if (ir.bottom > lr.bottom - 26) tocList.scrollTop += ir.bottom - lr.bottom + 26;
      else if (ir.top < lr.top + 10) tocList.scrollTop -= (lr.top + 10 - ir.top);
    }
    requestAnimationFrame(() => {
      tocEl.classList.toggle('at-end', tocList.scrollTop + tocList.clientHeight >= tocList.scrollHeight - 3);
    });
  }
  tocTab.addEventListener('click', () => setToc(!tocEl.classList.contains('open')));

  /* ---------- 提示气泡 ---------- */
  function showTip(i, el) {
    tipEl.textContent = (i + 1) + ' / ' + total + '　' + titles[i];
    tipEl.classList.add('show');
    const r = el.getBoundingClientRect();
    const w = tipEl.offsetWidth;
    let x = r.left + r.width / 2;
    x = Math.min(Math.max(x, w / 2 + 12), window.innerWidth - w / 2 - 12);
    tipEl.style.left = x + 'px';
  }
  function hideTip() { tipEl.classList.remove('show'); }

  /* ---------- 渲染与翻页 ---------- */
  function render() {
    slides.forEach((s, i) => s.classList.toggle('active', i === cur));
    let bi = 0, bd = Infinity;
    anchorPages.forEach((p, i) => { const d = Math.abs(p - (cur + 1)); if (d < bd) { bd = d; bi = i; } });
    dotEls.forEach((d, i) => d.classList.toggle('on', i === bi));
    tocItems.forEach((b, i) => b.classList.toggle('on', i === cur));
    prevBtn.disabled = cur === 0;
    nextBtn.disabled = cur === total - 1;
    cntCur.textContent = String(cur + 1).padStart(PAD, '0');
    prog.style.width = ((cur + 1) / total * 100) + '%';
  }
  function go(n) {
    n = Math.max(0, Math.min(total - 1, n));
    if (n === cur) return;
    cur = n;
    render();
  }
  prevBtn.onclick = () => go(cur - 1);
  nextBtn.onclick = () => go(cur + 1);

  /* ---------- 全屏放映 ---------- */
  function toggleFs() {
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {});
  }
  fsBtn.addEventListener('click', toggleFs);

  function clearIdle() { clearTimeout(idleTimer); idleTimer = null; }
  function wakeChrome(force) {
    if (!presenting) return;
    const now = Date.now();
    if (!force && now - lastMove < 180) return;
    lastMove = now;
    document.body.classList.remove('ui-idle');
    clearIdle();
    idleTimer = setTimeout(() => document.body.classList.add('ui-idle'), 2200);
  }
  function syncPresenting() {
    presenting = !!document.fullscreenElement;
    document.body.classList.toggle('presenting', presenting);
    fsBtn.classList.toggle('on', presenting);
    if (presenting) { setToc(false); wakeChrome(true); }
    else { clearIdle(); document.body.classList.remove('ui-idle'); }
    fit();
  }
  document.addEventListener('fullscreenchange', syncPresenting);
  document.addEventListener('mousemove', () => wakeChrome(false), { passive: true });
  document.addEventListener('click', () => wakeChrome(true), { passive: true });

  /* ---------- 键盘与手势 ---------- */
  document.addEventListener('keydown', e => {
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); go(cur + 1); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); go(cur - 1); }
    else if (e.key === 'Home') { e.preventDefault(); go(0); }
    else if (e.key === 'End') { e.preventDefault(); go(total - 1); }
    else if (e.key === 't' || e.key === 'T') { e.preventDefault(); if (!presenting) setToc(!tocEl.classList.contains('open')); }
    else if (e.key === 'f' || e.key === 'F') { e.preventDefault(); toggleFs(); }
    else if (e.key === 'Escape') { setToc(false); if (document.fullscreenElement) document.exitFullscreen(); }
  });

  let sx = null;
  document.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, { passive: true });
  document.addEventListener('touchend', e => {
    if (sx === null) return;
    const dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 50) { dx < 0 ? go(cur + 1) : go(cur - 1); }
    sx = null;
  }, { passive: true });

  /* ---------- 自适应 ---------- */
  function fit() {
    const reserve = presenting ? 24 : 104;
    const leftPad = document.body.classList.contains('toc-open') ? 170 : 0;
    const s = Math.min((window.innerWidth - leftPad - 36) / 1280, (window.innerHeight - reserve) / 720);
    stage.style.transform = 'translateX(' + (leftPad / 2) + 'px) scale(' + s + ')';
  }
  window.addEventListener('resize', fit);
  fit();
  render();
})();
