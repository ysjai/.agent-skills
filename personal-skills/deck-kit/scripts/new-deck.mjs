#!/usr/bin/env node
/* new-deck.mjs — 生成一份新片子的外壳（单文件 HTML，内联 CSS/JS/logo）
   用法：
     node scripts/new-deck.mjs --out outputs/deck.html --title "标题" [--brand brand.json] [--accent "#8E3B45"]
*/
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const argv = process.argv.slice(2);
const opt = {};
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
}

if (!opt.out) {
  console.error('缺少 --out。用法：node ' + path.join(ROOT, 'scripts/new-deck.mjs') + ' --out outputs/deck.html --title "标题"');
  process.exit(1);
}

const DEFAULTS = {
  name: '',
  tagline: '',
  accent: '#8E3B45',
  logos: []
};

let cfg = { ...DEFAULTS };
if (opt.brand) {
  const bp = path.resolve(opt.brand);
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(bp, 'utf8'));
  } catch (e) {
    console.error('读不了 brand.json：' + bp);
    console.error('  ' + (e instanceof SyntaxError ? 'JSON 格式有误：' + e.message : e.message));
    process.exit(1);
  }
  const dir = path.dirname(bp);
  cfg = {
    name: raw.name || DEFAULTS.name,
    tagline: raw.tagline || raw.footer || DEFAULTS.tagline,
    accent: raw.accent || DEFAULTS.accent,
    logos: (raw.logos && raw.logos.length ? raw.logos : DEFAULTS.logos).map(l => ({
      src: path.isAbsolute(l.src || l) ? (l.src || l) : path.resolve(dir, l.src || l),
      alt: l.alt || ''
    }))
  };
}
if (opt.accent) cfg.accent = opt.accent;
if (!/^#[0-9A-Fa-f]{6}$/.test(cfg.accent)) {
  console.error('accent 必须是 6 位十六进制色值，例如 "#8E3B45"，当前：' + cfg.accent);
  process.exit(1);
}

const dataUri = p => {
  if (!fs.existsSync(p)) { console.error('找不到 logo：' + p); process.exit(1); }
  const ext = path.extname(p).toLowerCase();
  const mime = ext === '.svg' ? 'image/svg+xml' : ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : 'image/png';
  return `data:${mime};base64,` + fs.readFileSync(p).toString('base64');
};

const brandJson = JSON.stringify({
  brand: cfg.logos.map(l => ({ src: dataUri(l.src), alt: l.alt }))
});

let css = fs.readFileSync(path.join(ROOT, 'assets/deck.css'), 'utf8');
css = css.replace(/--accent:#[0-9A-Fa-f]{6};/, `--accent:${cfg.accent};`);

const js = fs.readFileSync(path.join(ROOT, 'assets/deck.js'), 'utf8');
const tpl = fs.readFileSync(path.join(ROOT, 'assets/template.html'), 'utf8');

const title = typeof opt.title === 'string' ? opt.title : '未命名演示文稿';
const brandline = [cfg.name, cfg.tagline].filter(Boolean).join(' · ');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const html = tpl
  .replace('{{TITLE}}', () => esc(title))
  .replace('{{BRANDLINE}}', () => esc(brandline))
  .replace('{{BRAND}}', () => brandJson)
  .replace('{{CSS}}', () => css)
  .replace('{{JS}}', () => js);

const out = path.resolve(opt.out);
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, html);

const pages = (html.match(/<section class="slide/g) || []).length;
console.log(`✔ 已生成 ${path.relative(process.cwd(), out)}`);
console.log(`  标题：${title}`);
console.log(`  品牌：${cfg.name || '未指定'}${cfg.logos.length ? ' · ' + cfg.logos.length + ' 个 logo' : ' · 无 logo'}`);
console.log(`  强调色：${cfg.accent}`);
console.log(`  页数：${pages}（含封面与 1 页示例） · 体积 ${(html.length / 1024).toFixed(0)}KB`);
console.log('');
console.log('下一步：');
console.log('  1. 按 ' + path.join(ROOT, 'references/layouts.md') + ' 把页面插到 <!-- SLIDES --> 锚点之前');
console.log('  2. node ' + path.join(ROOT, 'scripts/verify.mjs') + ' ' + path.relative(process.cwd(), out));
