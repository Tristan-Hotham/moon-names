// QA: open index.html at desktop and phone widths, log console errors, exercise both maps, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server 8801; set PORT to change).
// MapLibre comes from a local npm copy (the CDN is not reachable from the build container); OpenFreeMap tiles are reachable,
// planetary imagery and web fonts are not.
const { chromium } = require("playwright");
const ML = process.env.MAPLIBRE_DIST || "/tmp/ml/node_modules/maplibre-gl/dist";
(async () => {
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const errs = [], checks = [];
  const ok = (c, m) => checks.push((c ? "ok   " : "FAIL ") + m);
  for (const [nm, vw, vh] of [["desktop", 1280, 900], ["phone", 390, 844]]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/cartocdn|fastly|googleapis|gstatic|amazonaws|site-nav/, r => r.abort());
    await p.route(/maplibre-gl\.js$/, r => r.fulfill({ path: ML + "/maplibre-gl.js" }));
    await p.route(/maplibre-gl\.css$/, r => r.fulfill({ path: ML + "/maplibre-gl.css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::|Failed to load resource|AJAXError|tiles?|terrarium/i.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + (process.env.PORT || 8801) + "/index.html", { waitUntil: "load" });
    await p.waitForTimeout(9000);
    await p.screenshot({ path: `qa/${nm}_top.png` });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(700); await p.locator(sel).screenshot({ path: `qa/${nm}_${f}.png` }); };
    await shot("#atlas", "maps_moon");
    ok(await p.evaluate(() => bReady && eReady), `${nm}: both maps ready`);
    ok(await p.evaluate(() => bmap.querySourceFeatures("feat").length > 1000), `${nm}: Moon features drawn`);
    // pick a crater: popup on the body map, the Earth map follows
    await p.evaluate(() => { const f = F.find(f => f.name === "Copernicus" && f.b === "moon"); pickFeature(f.i, true, true); });
    await p.waitForTimeout(2500);
    ok(await p.locator("#bmap .maplibregl-popup").count() === 1, `${nm}: crater popup opens`);
    ok(await p.evaluate(() => S.psel && PLACES[S.psel].name === "Toruń"), `${nm}: Earth follows to Toruń`);
    await shot("#atlas", "pick_copernicus");
    // fly link and place popup
    await p.locator("#bmap .flylink").click(); await p.waitForTimeout(2000);
    ok(await p.locator("#emap .maplibregl-popup").count() === 1, `${nm}: birthplace popup opens`);
    // place -> feature on another world
    await p.evaluate(() => { const k = Object.values(PLACES).find(q => q.name === "Paris").key; pickPlace(k, true); });
    await p.waitForTimeout(2200); await shot("#atlas", "pick_paris");
    await p.evaluate(() => { const f = F.find(f => f.name === "Tolstoj" && f.b === "mercury"); pickFeature(f.i, true, true); });
    await p.waitForTimeout(2500);
    ok(await p.evaluate(() => S.body === "mercury"), `${nm}: switching world by picking`);
    await shot("#atlas", "pick_tolstoj");
    // body buttons and colour
    await p.click('#bodyRow [data-b="venus"]'); await p.waitForTimeout(1200);
    await p.click('#colRow [data-c="occ"]'); await p.waitForTimeout(1200);
    await shot("#atlas", "venus_occ");
    await p.click('#bodyRow [data-b="mars"]'); await p.waitForTimeout(1200);
    ok(await p.evaluate(() => emap.getSource("tw")._data.features.length > 200), `${nm}: Mars village layer`);
    await p.evaluate(() => { const f = F.find(f => f.b === "mars" && PLF[f.fid] && PLF[f.fid][0].place === "Crewe"); pickFeature(f.i, true, false); }); await p.waitForTimeout(1500);
    await p.locator("#bmap [data-town]").click(); await p.waitForTimeout(2200);
    ok(await p.locator("#emap .maplibregl-popup").count() === 1, `${nm}: Crewe popup on Earth`);
    await shot("#atlas", "mars_crewe");
    await p.click('#colRow [data-c="cont"]'); await p.waitForTimeout(800);
    await p.click('#bodyRow [data-b="moon"]'); await p.waitForTimeout(800);
    // search
    await p.fill("#q", "gagar"); await p.waitForTimeout(400);
    ok(await p.locator("#sug li").count() > 0, `${nm}: search suggestions`);
    await p.keyboard.press("Enter"); await p.waitForTimeout(2500);
    ok(await p.evaluate(() => S.fsel != null && F[S.fsel].name === "Gagarin"), `${nm}: search picks Gagarin`);
    // layers panels
    await p.locator("#bmap .lyrBtn").click(); await p.waitForTimeout(300);
    await p.locator('#bmap .lyrPanel [data-k="grat"]').uncheck(); await p.waitForTimeout(300);
    ok(await p.evaluate(() => bmap.getLayoutProperty("grat", "visibility") === "none"), `${nm}: graticule toggles`);
    await shot("#bmap", "body_layers");
    await p.locator('#bmap .lyrPanel [data-k="grat"]').check(); await p.locator("#bmap .lyrBtn").click();
    await p.locator("#emap .lyrBtn").click(); await p.waitForTimeout(300);
    await p.locator('#emap .lyrPanel [data-k="allw"]').check(); await p.waitForTimeout(800);
    ok(await p.evaluate(() => S.all === true), `${nm}: all worlds toggle`);
    await shot("#emap", "earth_layers");
    await p.locator('#emap .lyrPanel .reset').click(); await p.locator("#emap .lyrBtn").click();
    for (const c of ["contChart", "ctyChart", "centChart", "occChart", "womenChart", "discChart", "townTable", "marsChart"]) await shot("#" + c, c);
    // full screen on each map
    await p.locator("#atlas").scrollIntoViewIfNeeded();
    ok(await p.locator(".mfs-btn").count() === 2, `${nm}: two full-screen buttons`);
    await p.locator("#bmap .mfs-btn").click(); await p.waitForTimeout(1200);
    ok(await p.evaluate(() => !!document.fullscreenElement || document.getElementById("bmap").classList.contains("mfs-fake")), `${nm}: full screen on`);
    await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
    await p.locator("#bmap .mfs-btn").click(); await p.waitForTimeout(600);
    if (nm === "phone") { await p.click("#theme"); await p.waitForTimeout(800); await shot("#contChart", "dark_cont"); }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    ok(ov <= 0, `${nm}: horizontal overflow ${ov}px`);
    await p.close();
  }
  console.log(checks.join("\n"));
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
