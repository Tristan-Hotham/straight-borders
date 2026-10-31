// QA: serve the folder, open index.html at 1280 px and 390 px, collect console errors, take screenshots, exercise the map.
// Run: node code/11_qa.js (needs playwright; Leaflet from a local npm folder, QA_NODE). Tiles and web fonts are blocked offline.
const { chromium } = require('playwright');
const path = require('path'), http = require('http'), fs = require('fs');
const NM = process.env.QA_NODE || '/tmp/claude-0/qa/node_modules';
const ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.csv': 'text/csv', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0].split('#')[0])); fs.readFile(f.endsWith('/') ? f + 'index.html' : f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const b = await chromium.launch();
  for (const [w, h, tag, dark] of [[1280, 900, 'desktop', false], [390, 844, 'phone', false], [1280, 900, 'dark', true]]) {
    const p = await b.newPage({ viewport: { width: w, height: h }, colorScheme: dark ? 'dark' : 'light' });
    const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    await p.route(/leaflet.min.js/, r => r.fulfill({ path: NM + '/leaflet/dist/leaflet.js' }));
    await p.route(/leaflet.min.css/, r => r.fulfill({ path: NM + '/leaflet/dist/leaflet.css' }));
    await p.goto(`http://localhost:${srv.address().port}/index.html`, { waitUntil: 'load' });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_top.png` });
    await p.evaluate(() => document.getElementById('atlas').scrollIntoView());
    await p.waitForTimeout(600);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_world.png` });
    if (tag === 'dark') { console.log(tag, 'errors', errs.filter(e => !/ERR_|net::|Failed to load resource/.test(e))); await p.close(); continue; }
    await p.evaluate(() => { map.fitBounds([[12, -18], [33, 36]]); }); await p.waitForTimeout(900);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_sahara.png` });
    await p.evaluate(() => { selSeg(1); }); await p.waitForTimeout(900);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_seg1.png` });
    await p.evaluate(() => { map.closePopup(); selCountry('NAM', true); }); await p.waitForTimeout(900);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_namibia.png` });
    await p.evaluate(() => document.getElementById('side').scrollIntoView({ block: 'center' })); await p.waitForTimeout(300);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_side.png` });
    // click a line on the canvas: Egypt and Sudan, 22nd parallel
    await p.evaluate(() => { document.getElementById('atlas').scrollIntoView(); map.setView([22, 30], 5); }); await p.waitForTimeout(900);
    const pt = await p.evaluate(() => { const c = map.latLngToContainerPoint([21.995, 29]); const r = map.getContainer().getBoundingClientRect(); return [r.left + c.x, r.top + c.y]; });
    await p.mouse.click(pt[0], pt[1]); await p.waitForTimeout(600);
    const pop = await p.evaluate(() => { const e = document.querySelector('.leaflet-popup-content'); return e ? e.textContent.slice(0, 160) : 'NO POPUP'; });
    await p.screenshot({ path: `${ROOT}/qa/${tag}_click.png` });
    await p.evaluate(() => searchFor('Chad')); await p.waitForTimeout(200);
    const sug = await p.$eval('#sug', e => e.textContent);
    await p.evaluate(() => { document.getElementById('sug').style.display = 'none'; map.closePopup(); document.getElementById('atlas').scrollIntoView(); document.querySelector('.lyrBtn').click(); }); await p.waitForTimeout(300);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_layers.png` });
    await p.evaluate(() => { document.querySelector('.lyrBtn').click(); });
    for (const id of ['contChart', 'sensChart', 'topChart', 'timeChart', 'rmChart', 'scaleChart', 'cyTable']) {
      await p.evaluate(id => document.getElementById(id).scrollIntoView({ block: 'center' }), id); await p.waitForTimeout(250);
      await p.screenshot({ path: `${ROOT}/qa/${tag}_${id}.png` });
    }
    const fsb = await p.$$eval('.mfs-btn', e => e.length);
    const sw = await p.evaluate(() => document.documentElement.scrollWidth);
    console.log(tag, 'fullscreen buttons', fsb, 'scrollWidth', sw, 'popup:', pop, '| search:', sug.slice(0, 80));
    console.log(tag, 'errors', errs.filter(e => !/ERR_|net::|Failed to load resource/.test(e)), 'network errors', errs.filter(e => /ERR_|net::|Failed to load resource/.test(e)).length);
    await p.close();
  }
  await b.close(); srv.close();
})();
