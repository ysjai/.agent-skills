#!/usr/bin/env node
/* verify.mjs — 交付前自检：截图 + 溢出 + 页码 + 占位残留 + 控制台报错
   用法：
     node ~/.workbuddy/skills/deck-kit/scripts/verify.mjs <deck.html> [--out /tmp/deck-shot] [--width 1440 --height 900]
   退出码：0 通过 / 1 有问题（不要交付）/ 2 缺少依赖
*/
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(process.cwd() + path.sep);

let chromium;
for (const base of [process.cwd(), ROOT, path.join(ROOT, '..')]) {
  try { ({ chromium } = require(require.resolve('playwright', { paths: [base] }))); break; } catch {}
}
if (!chromium) {
  console.error('未找到 playwright。在项目里装一次即可：npm i -D playwright');
  process.exit(2);
}

const argv = process.argv.slice(2);
const file = argv.find(a => !a.startsWith('--'));
if (!file) { console.error('用法：node verify.mjs <deck.html>'); process.exit(1); }
const opt = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[++i];

const outDir = opt.out || '/tmp/deck-shot';
const W = Number(opt.width || 1440), H = Number(opt.height || 900);
const TMP = [os.tmpdir(), '/tmp', '/private/tmp', '/var/folders'].some(d => outDir.startsWith(d));
if (TMP || /deck-shot/.test(outDir)) fs.rmSync(outDir, { recursive: true, force: true });
else console.warn('提示：输出目录不在临时目录，保留已有文件（只覆盖同名截图）。');
fs.mkdirSync(outDir, { recursive: true });

const abs = path.resolve(file);
const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));

await page.goto('file://' + abs);
await page.waitForTimeout(600);

const count = await page.evaluate(() => document.querySelectorAll('#stage > .slide').length);
if (!count) {
  console.error('没有找到 #stage > .slide，检查文件结构。');
  await browser.close();
  process.exit(1);
}

await page.evaluate(() => {
  const st = document.getElementById('stage');
  if (st) st.style.transform = 'none';
  document.body.style.paddingBottom = '0';
});

/* 结构检查：封面数量、页码、空正文区、占位残留 */
const struct = await page.evaluate(() => {
  const slides = Array.from(document.querySelectorAll('#stage > .slide'));
  const pad = String(slides.length).length < 2 ? 2 : String(slides.length).length;
  const covers = slides.filter(s => s.classList.contains('cover')).length;
  const strays = [...document.querySelectorAll('section.slide')]
    .filter(el => el.parentElement.id !== 'stage' && !el.closest('.toc-thumb')).length;
  const thin = [];
  slides.forEach((s, i) => {
    if (s.classList.contains('cover')) return;
    const body = s.querySelector('.body');
    if (!body) return;
    const text = (body.textContent || '').replace(/\s+/g, '');
    if (text.length < 40) thin.push(`第 ${i + 1} 页正文只有 ${text.length} 字`);
  });
  const badPages = [], emptyBody = [], placeholders = [];
  const PLACEHOLDER = ['在这里写主标题', '第二行用强调色', '要点标题', '段落标题', '…同上…',
    '两行以内的解释', '示例文本', '数据来源或出处', '一句话说明这一段', 'TODO'];
  slides.forEach((s, i) => {
    const pg = s.querySelector('.foot .pg');
    const want = String(i + 1).padStart(pad, '0');
    if (pg) {
      const got = pg.textContent.trim();
      if (got !== want) badPages.push(`第 ${i + 1} 页页脚写 ${got}，应为 ${want}`);
    } else if (!s.classList.contains('cover')) {
      badPages.push(`第 ${i + 1} 页缺页脚 .foot（页码与来源应固定）`);
    }
    const body = s.querySelector('.body');
    if (body && !body.children.length && !s.classList.contains('cover')) emptyBody.push(i + 1);
    const txt = s.textContent || '';
    PLACEHOLDER.forEach(p => { if (txt.includes(p)) placeholders.push(`第 ${i + 1} 页残留占位文案「${p}」`); });
  });
  return { total: slides.length, covers, badPages, emptyBody, placeholders, strays, thin };
});

const problems = [];
const sparse = [];
for (let i = 0; i < count; i++) {
  await page.evaluate(n => {
    document.querySelectorAll('#stage > .slide').forEach((s, j) => s.classList.toggle('active', j === n));
  }, i);
  await page.waitForTimeout(120);
  await page.evaluate(n => {
    const el = document.querySelector('#cnt b');
    if (el) el.textContent = String(n + 1).padStart(el.textContent.length, '0');
  }, i);
  await page.screenshot({ path: path.join(outDir, `p${String(i + 1).padStart(2, '0')}.png`) });

  const hits = await page.evaluate(n => {
    const s = document.querySelectorAll('#stage > .slide')[n];
    const sr = s.getBoundingClientRect();
    const out = [];
    s.querySelectorAll('*').forEach(el => {
      if (el.closest('.toc-thumb')) return;
      const r = el.getBoundingClientRect();
      if (r.height <= 0 || r.width <= 0) return;
      const d = [];
      if (r.bottom > sr.bottom + 0.5) d.push('bottom=' + Math.round(r.bottom - sr.top));
      if (r.right > sr.right + 0.5) d.push('right=' + Math.round(r.right - sr.left));
      if (r.top < sr.top - 0.5) d.push('top=' + Math.round(r.top - sr.top));
      if (r.left < sr.left - 0.5) d.push('left=' + Math.round(r.left - sr.left));
      if (d.length) {
        out.push(el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : '') + '  ' + d.join(' '));
      }
    });
    return out.slice(0, 6);
  }, i);

  if (hits.length) problems.push({ page: i + 1, hits });

  const fill = await page.evaluate(n => {
    const s = document.querySelectorAll('#stage > .slide')[n];
    if (s.classList.contains('cover')) return null;
    const body = s.querySelector('.body');
    if (!body || !body.children.length) return null;
    const br = body.getBoundingClientRect();
    if (br.height < 1) return null;
    let bottom = br.top;
    body.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.height > 0 && r.width > 0) bottom = Math.max(bottom, r.bottom);
    });
    return Math.round(((bottom - br.top) / br.height) * 100);
  }, i);
  if (fill !== null && fill < 82) sparse.push({ page: i + 1, fill });
}

await browser.close();

console.log(`文件：${path.basename(abs)}　页数：${struct.total}　视口：${W}×${H}`);
console.log(`截图：${outDir}/p01.png … p${String(struct.total).padStart(2, '0')}.png`);

const groups = [];
if (errors.length) groups.push(['控制台报错', errors.slice(0, 8)]);
if (struct.covers > 1) groups.push(['多个封面', [`共 ${struct.covers} 个 .cover，一页封面即可`]]);
if (struct.strays) groups.push(['页面落在 #stage 之外（不会显示，也不会被导航统计）',
  [`有 ${struct.strays} 个 section.slide 不在 #stage 内，检查是不是插到了锚点后面或 </div> 之外`]]);
if (struct.badPages.length) groups.push(['页脚页码不连续', struct.badPages]);
if (struct.placeholders.length) groups.push(['占位文案未替换', [...new Set(struct.placeholders)]]);
if (struct.emptyBody.length) groups.push(['正文区为空', struct.emptyBody.map(n => `第 ${n} 页 .body 没有内容`)]);
if (struct.thin.length) groups.push(['正文太空', [...struct.thin, '撑满高度但没内容也是空页，补一段解释或换版式']]);

if (problems.length) groups.push(['元素越界（1280×720 之外会被裁掉）', problems.map(p => `第 ${p.page} 页：` + p.hits.join(' / '))]);

if (groups.length) {
  groups.forEach(([title, lines]) => {
    console.log(`\n✖ ${title}：`);
    lines.forEach(l => console.log('  ' + l));
  });
}
if (sparse.length) {
  console.log('\n⚠ 提示：正文填充偏低（不阻塞，但观众可能觉得没讲完）');
  sparse.forEach(p => console.log(`  第 ${p.page} 页只填了 ${p.fill}%，可以补内容、放大字号或换版式`));
}

if (!groups.length) {
  console.log('\n✔ 通过：无越界、无报错、页码连续、无占位残留。仍建议逐页看截图，检查对齐。');
  process.exit(0);
}
process.exit(1);
