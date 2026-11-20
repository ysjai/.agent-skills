#!/usr/bin/env node
/* brand.mjs — 处理 logo：去白底、等比缩放、输出规范 PNG
   用法：
     node scripts/brand.mjs logo1.png [logo2.png ...] --out-dir assets/logos --height 130
   结果：<name>.png，高度统一，背景透明，便于多个 logo 并排锁排。
*/
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const argv = process.argv.slice(2);
const files = [];
const opt = { 'out-dir': 'assets/logos', height: '130' };
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[++i];
  else files.push(argv[i]);
}
if (!files.length) {
  console.error('用法：node scripts/brand.mjs <logo.png> [--out-dir dir] [--height 130]');
  process.exit(1);
}

const PY = `
import sys
from PIL import Image
src, out, h = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert('RGBA')
w, hh = im.size
px = im.load()
def lum(p): return (p[0]*299 + p[1]*587 + p[2]*114) / 1000
corners = [px[x, y] for x, y in ((0, 0), (w-1, 0), (0, hh-1), (w-1, hh-1))]
vis = [lum(c) for c in corners if c[3] > 10]
if vis and sum(vis) / len(vis) < 200:
    print('WARN', end=' ')
for y in range(hh):
    for x in range(w):
        r, g, b, a = px[x, y]
        lum = (r*299 + g*587 + b*114) / 1000
        if lum >= 250: na = 0
        elif lum <= 232: na = 255
        else: na = int(255 * (250 - lum) / 18)
        px[x, y] = (r, g, b, min(a, na))
bbox = im.getbbox()
if bbox: im = im.crop(bbox)
if im.size[1] > 0:
    ratio = h / im.size[1]
    im = im.resize((max(1, int(im.size[0] * ratio)), h), Image.LANCZOS)
im.save(out, 'PNG', optimize=True)
print('%dx%d' % im.size)
`;

fs.mkdirSync(opt['out-dir'], { recursive: true });

for (const f of files) {
  if (!fs.existsSync(f)) { console.error('跳过（不存在）：' + f); continue; }
  const base = path.basename(f, path.extname(f)).toLowerCase().replace(/[^a-z0-9_-]+/g, '-');
  const out = path.join(opt['out-dir'], base + '.png');
  const r = spawnSync('python3', ['-c', PY, f, out, opt.height], { encoding: 'utf8' });
  if (r.status !== 0) {
    console.error('处理失败（需要 python3 + Pillow）：' + f);
    console.error((r.stderr || '').split('\n').slice(-3).join('\n'));
    continue;
  }
  const kb = (fs.statSync(out).size / 1024).toFixed(1);
  const warned = (r.stdout || '').trim().startsWith('WARN');
  const size = (r.stdout || '').replace('WARN', '').trim();
  console.log(`✔ ${out}  (${size}, ${kb}KB)`);
  if (warned) console.log('  ⚠ 四角不是白底：自动去底可能把图形抠坏，请打开图片确认，必要时手工处理。');
}
console.log('\n已写入品牌库。在 brand.json 里按下面的形式引用：');
console.log('  { "logos": [{ "src": "assets/logos/xxx.png", "alt": "公司名" }] }');
