import json, base64, os
S = os.path.dirname(os.path.abspath(__file__))
V = {r['symbol']: r for r in json.load(open(f'{S}/all_verdicts.json'))}
C = {r['symbol']: r for r in json.load(open(f'{S}/all_challenges.json'))}

def img(sym):
    b = base64.b64encode(open(f'{S}/charts/{sym}.png','rb').read()).decode()
    return f'data:image/png;base64,{b}'

CSS = """
:root{
  --ground:#F4F3F7; --surface:#FFFFFF; --surface-2:#FAF9FC;
  --ink:#191722; --ink-2:#5B5670; --ink-3:#8A85A0;
  --line:#E3E0EA; --line-2:#CFCADB;
  --accent:#5B3E8F; --accent-soft:#EEE9F6; --accent-2:#B4650F;
  --up:#0B7A38; --up-soft:#E4F2E9; --down:#BB2C2C; --down-soft:#F8E7E7;
  --warn:#8A6A12; --warn-soft:#F6EFDC;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#131219; --surface:#1C1A24; --surface-2:#232030;
    --ink:#EFEDF4; --ink-2:#A9A3BA; --ink-3:#7A7490;
    --line:#2F2C3C; --line-2:#403C52;
    --accent:#B7A0E4; --accent-soft:#2A2340; --accent-2:#E19A47;
    --up:#4CC47C; --up-soft:#16301F; --down:#F1706C; --down-soft:#331A1A;
    --warn:#D9B25A; --warn-soft:#302713;
  }
}
:root[data-theme="dark"]{
  --ground:#131219; --surface:#1C1A24; --surface-2:#232030;
  --ink:#EFEDF4; --ink-2:#A9A3BA; --ink-3:#7A7490;
  --line:#2F2C3C; --line-2:#403C52;
  --accent:#B7A0E4; --accent-soft:#2A2340; --accent-2:#E19A47;
  --up:#4CC47C; --up-soft:#16301F; --down:#F1706C; --down-soft:#331A1A;
  --warn:#D9B25A; --warn-soft:#302713;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Source Serif 4",Georgia,serif; font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px 96px}
.col{max-width:68ch}
h1,h2,h3,h4{font-family:Archivo,"Helvetica Neue",Arial,sans-serif;text-wrap:balance;margin:0}
.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace}
.eyebrow{
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11px;
  letter-spacing:.16em; text-transform:uppercase; color:var(--ink-3);
}

/* ---------- masthead ---------- */
header.mast{border-bottom:2px solid var(--ink);margin-bottom:40px;padding:44px 0 26px}
.mast h1{font-size:clamp(38px,6vw,66px);font-weight:800;letter-spacing:-.033em;line-height:.98}
.mast .sub{margin-top:14px;color:var(--ink-2);font-size:19px;max-width:62ch}
.mastmeta{display:flex;flex-wrap:wrap;gap:10px 26px;margin-top:24px}
.mastmeta div{display:flex;flex-direction:column;gap:3px}
.mastmeta .v{font-family:"IBM Plex Mono",monospace;font-size:14px;color:var(--ink);font-variant-numeric:tabular-nums}

/* ---------- clause ---------- */
.clause{
  background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--accent);
  padding:20px 22px;margin:0 0 40px;
}
.clause pre{
  margin:10px 0 0;font-family:"IBM Plex Mono",monospace;font-size:13px;line-height:1.85;
  color:var(--ink);white-space:pre-wrap;word-break:break-word;
}
.clause .hl{color:var(--accent-2);font-weight:600}

/* ---------- funnel ---------- */
.funnel{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:0 0 14px}
.stage{background:var(--surface);padding:18px 16px}
.stage .n{font-family:Archivo,sans-serif;font-size:34px;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums;line-height:1}
.stage .lbl{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3);margin-top:7px}
.stage .d{font-size:13.5px;color:var(--ink-2);margin-top:8px;line-height:1.45;font-family:Archivo,sans-serif}
.stage.term .n{color:var(--accent)}

/* ---------- sections ---------- */
section{margin-top:64px}
.shead{display:flex;align-items:baseline;gap:14px;border-bottom:1px solid var(--line-2);padding-bottom:10px;margin-bottom:26px}
.shead h2{font-size:27px;font-weight:800;letter-spacing:-.02em}
.shead .count{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-3);margin-left:auto;white-space:nowrap}
p{margin:0 0 16px}

/* ---------- verdict card ---------- */
.card{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--line-2);margin-bottom:34px}
.card.buy{border-top-color:var(--up)}
.card.cond{border-top-color:var(--accent-2)}
.chead{display:flex;flex-wrap:wrap;align-items:flex-start;gap:14px;padding:20px 22px 16px;border-bottom:1px solid var(--line)}
.chead .tick{font-family:Archivo,sans-serif;font-size:27px;font-weight:800;letter-spacing:-.02em;line-height:1.1}
.chead .co{font-size:14px;color:var(--ink-2);display:block;font-weight:400;letter-spacing:0;margin-top:2px;font-family:"Source Serif 4",serif}
.chead .px{margin-left:auto;text-align:right}
.chead .px .p{font-family:"IBM Plex Mono",monospace;font-size:22px;font-variant-numeric:tabular-nums}
.chead .px .pl{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)}
.chips{display:flex;flex-wrap:wrap;gap:6px;width:100%}
.chip{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;padding:4px 9px;border:1px solid var(--line-2);color:var(--ink-2)}
.chip.k{background:var(--up-soft);border-color:transparent;color:var(--up);font-weight:600}
.chip.c{background:var(--warn-soft);border-color:transparent;color:var(--warn);font-weight:600}
.chip.a{background:var(--accent-soft);border-color:transparent;color:var(--accent)}
.cbody{padding:22px}
.cbody h4{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin:22px 0 8px}
.cbody h4:first-child{margin-top:0}
.cbody p{font-size:16px;margin:0 0 12px}
.chartbox{border:1px solid var(--line);background:var(--surface-2);padding:8px;margin:4px 0 18px;overflow-x:auto}
.chartbox img{display:block;width:100%;min-width:640px;height:auto}
.cap{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-3);margin-top:7px;line-height:1.5}

/* levels */
.levels{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:6px 0 18px}
.lv{background:var(--surface-2);padding:12px 13px}
.lv .k{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)}
.lv .v{font-family:"IBM Plex Mono",monospace;font-size:17px;font-variant-numeric:tabular-nums;margin-top:5px}
.lv.stop .v{color:var(--down)} .lv.tgt .v{color:var(--up)} .lv.rr .v{color:var(--accent);font-weight:600}
.strike{color:var(--ink-3);text-decoration:line-through;font-size:12px;margin-left:5px}

.bear{background:var(--down-soft);border-left:3px solid var(--down);padding:13px 16px;margin:4px 0 6px}
.bear .t{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--down);font-weight:600;margin-bottom:5px}
.bear p{font-size:15px;margin:0;color:var(--ink)}

/* ---------- tables ---------- */
.tw{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}
table{width:100%;border-collapse:collapse;font-size:14.5px;min-width:620px}
th{
  font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink-3);text-align:left;padding:11px 14px;border-bottom:1px solid var(--line-2);white-space:nowrap;font-weight:500;
}
td{padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:none}
td.sym{font-family:Archivo,sans-serif;font-weight:700;white-space:nowrap}
td.num{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;white-space:nowrap}
td.why{color:var(--ink-2);font-size:14px;line-height:1.5;min-width:270px}
tbody tr:hover{background:var(--surface-2)}
.tag{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.09em;text-transform:uppercase;padding:3px 7px;white-space:nowrap;display:inline-block}
.tag.ref{background:var(--down-soft);color:var(--down);font-weight:600}
.tag.wk{background:var(--warn-soft);color:var(--warn);font-weight:600}

/* ---------- notes ---------- */
.notes{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.note{background:var(--surface);padding:19px 20px}
.note h4{font-family:Archivo,sans-serif;font-size:15.5px;font-weight:700;margin-bottom:7px;letter-spacing:-.01em}
.note p{font-size:14.5px;color:var(--ink-2);margin:0;line-height:1.55}
.note .stat{font-family:"IBM Plex Mono",monospace;font-size:25px;font-weight:600;color:var(--accent-2);font-variant-numeric:tabular-nums;display:block;margin-bottom:5px}

ol.method{counter-reset:m;list-style:none;padding:0;margin:0;border:1px solid var(--line);background:var(--surface)}
ol.method li{counter-increment:m;padding:15px 20px 15px 60px;position:relative;border-bottom:1px solid var(--line);font-size:15.5px;color:var(--ink-2)}
ol.method li:last-child{border-bottom:none}
ol.method li::before{
  content:counter(m,decimal-leading-zero);position:absolute;left:20px;top:15px;
  font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--accent);letter-spacing:.06em;
}
ol.method b{color:var(--ink);font-weight:600}

footer{margin-top:70px;padding-top:22px;border-top:2px solid var(--ink);color:var(--ink-3);font-size:13.5px}
footer p{margin:0 0 9px;max-width:78ch}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:no-preference){tbody tr{transition:background .12s ease}}
@media (max-width:640px){
  body{font-size:16px}
  .wrap{padding:0 16px 64px}
  .chead .px{margin-left:0;text-align:left}
}
"""

def levels(orig, corr, rr_o, rr_c):
    def cell(k, v, extra='', strike=None):
        s = f'<span class="strike">{strike}</span>' if strike else ''
        return f'<div class="lv {extra}"><div class="k">{k}</div><div class="v">{v}{s}</div></div>'
    return ('<div class="levels">'
        + cell('Entry', corr['e'], '', orig['e'] if orig['e'] != corr['e'] else None)
        + cell('Stop', corr['s'], 'stop', orig['s'] if orig['s'] != corr['s'] else None)
        + cell('Target 1', corr['t'], 'tgt', orig['t'] if orig['t'] != corr['t'] else None)
        + cell('R:R (T1)', rr_c, 'rr', rr_o if rr_o != rr_c else None)
        + '</div>')

# ---------------- BUY cards ----------------
BUY = [
 dict(sym='AUBANK', cls='buy', chips=[('k','Buy'),('a','Breakout + retest'),('',u'₹21.8 cr/hr')],
   orig=dict(e='1098–1118', s='1088', t='1150'), corr=dict(e='1108.5', s='1082', t='1149'),
   rr_o='2.1', rr_c='2.07',
   read="An uninterrupted hourly staircase off the 24-Jul low at 963 — higher lows at 1027, 1040, 1049, 1063.7 and 1084. Between 12-Aug and 20-Aug the highs compressed into a shallow descending-highs pause (1099, 1098, 1092.5, 1078.6, 1092.5); on Friday price broke straight through it and closed at 1108.2, the high of the day and of the 52-week range.",
   saw="Every pullback in the 180-bar window is a two-to-four bar shallow dip that stops at or just under the rising EMA20, and the EMA20/50/200 fan out in order without crossing once since 27-Jul. The final candle is full-bodied green with no upper wick at all — unlike the rejection wicks that spoil ENDURANCE and SONACOMS.",
   vol="Up-volume to down-volume runs 2.46 over 40 bars. Friday's two heaviest bars were both up-closes; down bars during the 18-Aug dip ran 0.15–0.33x — textbook dry-up on the pullback.",
   bear="The skeptic's core objection was that Friday's closing bar was missing from the file, making the “closed at the high” claim unverifiable. That objection does not survive: Chartink's official Friday close for AUBANK is 1108.20, matching our last bar to the paisa. What does stand is the stop — 1088 sits above Friday's 1084 low and would fire before the thesis's own invalidation level. Use 1082.",
   inval="An hourly close below 1084 puts price back inside the 1063–1099 range. Loss of 1063.7 ends the higher-low sequence outright."),
 dict(sym='HEG', cls='buy', chips=[('k','Buy'),('a','Tight flag'),('',u'₹15.1 cr/hr')],
   orig=dict(e='703–714', s='694', t='749'), corr=dict(e='710', s='692', t='742'),
   rr_o='2.44', rr_c='1.78',
   read="From 582.7 on 17-Jul the pivot lows march up 671.1 → 684.1 → 688.45 → 700.8 → 705.0. The 18-Aug impulse reached 749.0, then price corrected to 696.10 and has spent three sessions coiling in a 696–722 band, closing Friday at 710.75 sitting on the EMA20 with the EMA50 two rupees beneath.",
   saw="The 18-Aug spike to 749 left a long upper wick, yet the three sessions since gave back almost none of the move — price is consolidating at 710 rather than retracing to 690. The last twelve hourly candles are tiny and overlapping, resting directly on a still-rising EMA20. The daily panel shows a clean breakout above the 615 April high.",
   vol="Volume is drying into the coil exactly as a flag should: the 20-bar average is 0.67 of the 100-bar. Friday's bars ran 0.4–1.1x against 1.7–2.2x on the 19-Aug advance. Up/down volume 1.46.",
   bear="The “unbroken higher-low staircase” is not unbroken — 696.10 undercut 700.80, and that pullback closed below the hourly EMA50. More importantly the original 749 target sits on the heaviest distribution bar of the year (5.4M shares), so it is supply, not a destination. Pulling target 1 back to 742 and the stop to 692 gives an honest 1.78:1, not 2.44.",
   inval="An hourly close below 696.10 breaks the chain and takes out the EMA50. Below 690 the whole August structure is compromised."),
]

COND = [
 dict(sym='UNITDSPR', chips=[('c','Conditional'),('a','Flat-base breakout'),('',u'₹9.0 cr/hr')],
   orig=dict(e='1548–1572', s='1536', t='1615'), corr=dict(e='1556', s='1526', t='1610'),
   rr_o='2.3', rr_c='1.80',
   read="A three-week horizontal base between 1503 and 1546–1550 — the tightest in the whole screen at a 3.17% range and 0.67% hourly ATR — resolved upward on Friday's 12:15 bar to 1563.4, closing 1556.",
   saw="For thirteen sessions the hourly candles are small-bodied and hug a nearly flat EMA20/EMA50 pair with the EMA200 sloping up beneath. No wide-range whipsaw bars anywhere in the base. The breakout candle is the first tall green body in three weeks and it clears a line that had capped price four separate times.",
   bear="Two corrections. The quoted base low of 1511.7 does not exist (02-Aug is a Sunday; the real low is 1503 on 10-Aug), and 1563.4 is 0.87% <em>above</em> the 52-week high, not 0.47% below it — which is bullish, but not what was claimed. The stop at 1536 sits inside Friday's own range and must move to 1526. The truncation objection is void: Chartink confirms 1556.00 as the official close."),
 dict(sym='NAM-INDIA', chips=[('c','Conditional'),('a','Retest holding'),('',u'₹15.8 cr/hr')],
   orig=dict(e='1240–1258', s='1223', t='1300'), corr=dict(e='1245', s='1222', t='1290'),
   rr_o='2.6', rr_c='1.96',
   read="Three weeks of range between 1155.2 and 1217 on a flat floor, then a decisive 20-Aug break to 1266. The retest has been shallow and orderly — 1231.2, then 1226.9 — from which Friday recovered to 1262.3 and closed 1251.",
   saw="The breakout leaves behind a perfectly horizontal three-week shelf at 1155–1218, the ideal structure to retest against, and the two-day pullback never came close to filling the 20-Aug gap. The daily panel confirms new all-time-high territory with no left-hand supply overhead.",
   bear="The best-evidenced call of the twenty — the flat base, the 3.05x daily breakout volume and the clean air above all verified. But the arithmetic was 33% flattering: honest R:R to 1300 is 1.96, not 2.6, and the stop at 1223 sits <em>above</em> the 1217–1218 shelf its own rationale claims to protect."),
 dict(sym='MOTILALOFS', chips=[('c','Conditional'),('a','Coil under 1004'),('',u'₹14.5 cr/hr')],
   orig=dict(e='975–1006', s='967', t='1060'), corr=dict(e='985', s='965', t='1033'),
   rr_o='2.3', rr_c='2.40',
   read="After the 24-Jul results gap-down from 975 to 845, the stock rebuilt in textbook steps: higher lows 835.1 → 875 → 890 → 930.15 → 968.55. It is now coiling in the top 1.4% of that structure, having tagged 1004.00 twice on Friday and closed 990.",
   saw="The EMA20 has acted as a rising floor on every pullback since 03-Aug, and the entire July gap-down is now filled and reclaimed with no lower high anywhere. The 20-Aug 09:15 bar is a 692k-share thrust straight through 946–980, and Friday held the whole gain in a 990–1004 band rather than giving any back.",
   bear="At the stated 1004.5 trigger the real reward-to-risk is 1.48, not 2.3. Target 1060 is not clear air — it is the top of the Oct–Nov 2025 shelf the stock distributed from before halving. Entering lower at 985 against a 965 stop with a 1033 target is the version that actually pays."),
 dict(sym='COFORGE', chips=[('c','Conditional'),('a','Two-gap breakout'),('',u'₹52.6 cr/hr')],
   orig=dict(e='1892–1905', s='1849', t='1985'), corr=dict(e='1892', s='1849', t='1935'),
   rr_o='2.0', rr_c='2.16',
   read="A genuinely orderly two-week base between 1762.6 and 1836.1 with higher lows throughout, broken by two consecutive gap-and-hold sessions on 19 and 20 Aug. Friday held a tight inside range and closed 1891.7 — the exact high of the day, the week and the six-month window.",
   saw="The consolidation reads as a flat, tight rectangle riding the EMA20 with small alternating bodies — no wide-range bars, no lower highs, no distribution shape. The breakout is not one spike but two gap-and-hold sessions, and the last candle closes at the very top of the chart with no upper wick.",
   bear="The sentence the whole R:R rested on — “no resistance between 1892 and 1990, clean air” — is contradicted by the stock's own daily history: 1892–1990 is a Nov/Dec-2025 distribution top where ~28M shares traded before an 18% collapse. First real supply is 1910–1936. The daily is also stretched (RSI 72.6, +27.4% in 20 sessions), so this is momentum continuation, not low-risk entry."),
]

def buycard(d):
    chips = ''.join(f'<span class="chip {c}">{t}</span>' for c,t in d['chips'])
    v = V[d['sym']]
    return f"""
<article class="card {d['cls']}">
  <div class="chead">
    <div><div class="tick">{d['sym']}<span class="co">{v.get('company','')}</span></div></div>
    <div class="px"><div class="p">{v['last_close']}</div><div class="pl">21 Aug close</div></div>
    <div class="chips">{chips}</div>
  </div>
  <div class="cbody">
    <div class="chartbox"><img src="{img(d['sym'])}" alt="{d['sym']} hourly and daily candlestick chart" loading="lazy">
      <div class="cap">Top: 180 hourly candles with EMA20 (blue) / EMA50 (orange) / EMA200 (purple). Middle: hourly volume vs 20-bar average. Bottom: 140 daily sessions.</div>
    </div>
    <h4>Levels after correction</h4>
    {levels(d['orig'], d['corr'], d['rr_o'], d['rr_c'])}
    <h4>Hourly structure</h4><p>{d['read']}</p>
    <h4>What the chart shows that the numbers don't</h4><p>{d['saw']}</p>
    <h4>Volume</h4><p>{d['vol']}</p>
    <div class="bear"><div class="t">The case against</div><p>{d['bear']}</p></div>
    <h4>Invalidation</h4><p>{d['inval']}</p>
  </div>
</article>"""

def condcard(d):
    chips = ''.join(f'<span class="chip {c}">{t}</span>' for c,t in d['chips'])
    v = V[d['sym']]
    return f"""
<article class="card cond">
  <div class="chead">
    <div><div class="tick">{d['sym']}<span class="co">{v.get('company','')}</span></div></div>
    <div class="px"><div class="p">{v['last_close']}</div><div class="pl">21 Aug close</div></div>
    <div class="chips">{chips}</div>
  </div>
  <div class="cbody">
    <div class="chartbox"><img src="{img(d['sym'])}" alt="{d['sym']} hourly and daily candlestick chart" loading="lazy"></div>
    {levels(d['orig'], d['corr'], d['rr_o'], d['rr_c'])}
    <h4>Hourly structure</h4><p>{d['read']}</p>
    <h4>What the chart shows</h4><p>{d['saw']}</p>
    <div class="bear"><div class="t">What the challenge corrected</div><p>{d['bear']}</p></div>
  </div>
</article>"""

WATCH = [
 ('TITAN','5086.1','2.75','Tightest base of its batch (4992–5111, nine sessions, volume 0.53x) and Friday defended the 5011 floor. But range highs are stepping down — 5168, 5153, 5125, 5111, 5110, 5090 — and Friday’s whole recovery traded 0.37x the 20-day average, the thinnest session of the month.'),
 ('ETERNAL','328.0','1.46','Real trend, wrong price. A correctly placed 3.4x-ATR stop paired with a 3% target runs straight into 686M shares of 2025 supply between 332 and 342. Friday was a red daily candle that reversed 4.85 points inside the hour that made the high.'),
 ('360ONE','1199.0','2.35','The 7x breakout volume was a measurement artifact — on daily volume 20-Aug was an ordinary 1.82x. Strip it away and what remains is one gap-and-run hour followed by eight consecutive lower highs.'),
 ('HINDCOPPER','581.0','1.16','Headline 2.9 R:R was the target-2 number; true R:R to target 1 is 1.16. The 16-point stop is 0.6x the daily ATR — inside a single day’s noise. The “higher lows” also step down: 553.00 is below 555.55.'),
 ('RRKABEL','2917.4','1.11','The “new all-time high” is a wick — 14:15 printed 2931.40 and closed 2917.40. Prior bars ran below average volume. Up 42% in 60 days and 51.5% above the daily EMA200.'),
 ('RBLBANK','392.5','1.45','R:R was computed off the untriggered close rather than the stated 394 trigger. The 393.90 high came on the fortnight’s biggest bar, which closed 2.35 off its high; Friday never traded up to it on 27% less volume — a second rejection at the same ceiling.'),
 ('WELSPUNLIV','189.9','1.27','The “two unfilled gaps” do not exist — both bars opened flat and traded their whole range within the hour. The 5.08x volume bar is really 2.63x.'),
 ('SHRIPISTON','4600.1','0.76','The “2.7% three-week rectangle” is really 6.6% wide (4302.8–4586). The 4505 stop sits mid-base — 70 of 77 base bars closed below it. Thinnest liquidity of the finalists at ₹3.4 cr/hr.'),
]
REJ = [
 ('PAYTM','1632.0','REFUTED','0.36','Risks 46 points to make 16.5. Target 1 (1656.5) is the exact level that already broke price 6.6%, and the entry zone extends above its own target. The “closed at the day’s high on the day’s largest volume” claim is false — the session closed on a 22,685-share auction print.'),
 ('EPL','263.0','REFUTED','1.00','Target 1 (274.00) <em>is</em> the entry trigger (274.00) — the claimed 2.77 R:R is arithmetically impossible. Friday spiked to a new 52-week high then sold off three straight hours to close four ticks off the low.'),
 ('HFCL','226.6','REFUTED','1.58','The “ascending base” is five consecutive lower highs (230.90 / 230.64 / 230.35 / 229.80 / 228.80) with 20-Aug undercutting 19-Aug’s low — a descending triangle after a 35.7M-share climax and a 15.0M-share reversal day.'),
 ('TI','575.7','REFUTED','1.46','No ascending triangle exists: the last four session highs are lower highs and Friday’s low undercuts Thursday’s. The true 52-week high is 593.00, not the 590 assumed. Daily RSI 81.7, up 33% in 20 days.'),
 ('ASAHIINDIA','965.8','REFUTED','1.55','The higher-low sequence was listed out of chronological order — the real last pivot low is 936.45, <em>below</em> 948.10 and 950.85. The chain broke Friday morning. Median hourly turnover ₹0.65 cr.'),
 ('MARKSANS','321.3','REFUTED','1.67','Six unbroken sessions of lower highs <em>and</em> lower lows relabelled a “flag”. Friday closed +0.14%, not a reversal, and its second-biggest bar was the down bar to the low.'),
]

def rows(data, kind):
    out=[]
    for r in data:
        if kind=='watch':
            s,p,rr,why=r
            out.append(f'<tr><td class="sym">{s}</td><td class="num">{p}</td><td class="num">{rr}</td><td class="why">{why}</td></tr>')
        else:
            s,p,v,rr,why=r
            out.append(f'<tr><td class="sym">{s}</td><td class="num">{p}</td><td><span class="tag ref">{v}</span></td><td class="num">{rr}</td><td class="why">{why}</td></tr>')
    return '\n'.join(out)

HTML = f"""<title>NSE Hourly Verdicts</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>

<div class="wrap">
<header class="mast">
  <div class="eyebrow">Chartink screen &middot; monthly rsi &gt; 60 &middot; 1-hour price action</div>
  <h1>Two buys out of<br>a hundred and seven.</h1>
  <p class="sub">Every stock on the screen was already in an uptrend on three timeframes. That is what made it useless as a filter — and what made the hourly chart the only place left to find an edge.</p>
  <div class="mastmeta">
    <div><span class="eyebrow">Data through</span><span class="v">Fri 21 Aug 2026, 15:15 IST</span></div>
    <div><span class="eyebrow">Universe</span><span class="v">107 stocks</span></div>
    <div><span class="eyebrow">Charts read</span><span class="v">107 hourly + daily</span></div>
    <div><span class="eyebrow">Analysts</span><span class="v">9 + 5 adversarial</span></div>
  </div>
</header>

<div class="clause">
  <div class="eyebrow">What the screener actually asks for</div>
  <pre>daily RSI(14) &gt; 60  <span class="hl">AND</span>  weekly RSI(14) &gt; 60  <span class="hl">AND</span>  monthly RSI(14) &gt; 60
<span class="hl">AND</span>  market cap &gt; ₹5,000 cr
<span class="hl">AND</span>  30-min EMA(20) &gt;= 0.97 × 30-min close
<span class="hl">AND</span>  1-hour  EMA(20) &gt;= 0.97 × 1-hour close</pre>
</div>

<div class="col">
<p>The last two conditions are the interesting ones: price must sit within roughly 3% of its own 20-EMA on both intraday timeframes. The screen is deliberately looking for momentum that has <em>paused</em> rather than momentum that has run away. That framing is sound, but it still passes 107 names, and a shared multi-timeframe uptrend means the trend itself carries no information here — every candidate has one.</p>
<p>So the question became narrower and more useful: on the 1-hour chart, which of these is actually offering a defined entry, a stop that sits under real structure, and a target that isn't buried in old supply?</p>
</div>

<section>
  <div class="shead"><h2>How 107 became 2</h2></div>
  <div class="funnel">
    <div class="stage"><div class="n">107</div><div class="lbl">Screened</div><div class="d">All Chartink hits, hourly and daily bars pulled and charted.</div></div>
    <div class="stage"><div class="n">29</div><div class="lbl">First-pass buys</div><div class="d">Nine analysts read every chart. 42 avoided, 36 watch-listed.</div></div>
    <div class="stage"><div class="n">20</div><div class="lbl">Challenged</div><div class="d">Top candidates handed to skeptics told to refute them.</div></div>
    <div class="stage term"><div class="n">2</div><div class="lbl">Survived</div><div class="d">Thesis intact after every level was recomputed from raw bars.</div></div>
  </div>
  <p class="cap" style="margin-top:12px">Seven of the twenty challenged calls were refuted outright; eleven were weakened on recomputed risk-reward. The most common failure was quoting a target-2 ratio as if it were the target-1 ratio.</p>
</section>

<section>
  <div class="shead"><h2>The two that survived</h2><span class="count">verified against raw bars</span></div>
  {''.join(buycard(d) for d in BUY)}
</section>

<section>
  <div class="shead"><h2>Conditional — real setups, corrected numbers</h2><span class="count">4 names</span></div>
  <div class="col"><p>Each of these has a genuine hourly structure that survived inspection, but was sold on inflated arithmetic. The levels below are the corrected ones. Treat them as trades that need their trigger to actually print before you act, not as entries at Friday's close.</p></div>
  {''.join(condcard(d) for d in COND)}
</section>

<section>
  <div class="shead"><h2>Watch, don't buy</h2><span class="count">8 names</span></div>
  <div class="tw"><table>
    <thead><tr><th>Symbol</th><th>Close</th><th>True R:R</th><th>Why it isn't a buy yet</th></tr></thead>
    <tbody>{rows(WATCH,'watch')}</tbody>
  </table></div>
</section>

<section>
  <div class="shead"><h2>Rejected on inspection</h2><span class="count">6 of the original buy calls</span></div>
  <div class="col"><p>These were graded buys on the first pass and did not survive fact-checking. In each case the failure is specific and checkable — a level that doesn't exist, a target below the entry, or a structure described as the opposite of what the bars show.</p></div>
  <div class="tw"><table>
    <thead><tr><th>Symbol</th><th>Close</th><th>Verdict</th><th>True R:R</th><th>What broke</th></tr></thead>
    <tbody>{rows(REJ,'rej')}</tbody>
  </table></div>
</section>

<section>
  <div class="shead"><h2>Data problems worth knowing about</h2></div>
  <div class="col"><p>Three defects surfaced during verification. All three are checkable against the numbers, and two of them silently distort common technical statistics.</p></div>
  <div class="notes">
    <div class="note"><span class="stat">81.6%</span><h4>The opening hour reports zero volume</h4>
      <p>Across 107 symbols and 200 bars each, 2,512 of 3,078 09:15 bars carry volume 0. Any &ldquo;3x the 20-bar average&rdquo; claim is therefore computed on a depressed base and overstates the multiple. Volume ratios in the first pass were inflated; daily volume is the honest denominator.</p></div>
    <div class="note"><span class="stat">1 of 107</span><h4>One split-corrupted series</h4>
      <p>TDPOWERSYS shows hourly prices at exactly 2.000x its daily prices from 12-Aug — a 1:2 split applied to one series and not the other. Chartink's official close of 1534.80 matches the hourly, so the <em>daily</em> block is the corrupt one. Its daily RSI of 32.4 and &minus;31% 20-day return are artifacts, not signals.</p></div>
    <div class="note"><span class="stat">8 of 107</span><h4>A bar-labelling artifact, not missing data</h4>
      <p>Eight symbols end Friday at a 14:15 bar rather than 15:15, and three separate challenges treated this as a missing closing hour that invalidated their theses. All eight closes match Chartink's official Friday close to the paisa. The data is complete; only the timestamp is odd.</p></div>
  </div>
</section>

<section>
  <div class="shead"><h2>How this was produced</h2></div>
  <ol class="method">
    <li>Pulled the screener's <b>scan clause</b> straight from Chartink's own payload rather than scraping the rendered table, then posted it back to get all 107 rows.</li>
    <li>Fetched <b>6 months of hourly and 1 year of daily bars</b> per symbol from Yahoo with a cookie-and-crumb session. 107 of 107 succeeded with no gaps.</li>
    <li>Computed a metric pack per stock — EMA stack, RSI, ADX/DI, ATR, pivot highs and lows, volume ratios, daily extension — and <b>rendered a candlestick chart for every one of the 107</b>.</li>
    <li>Nine Opus analysts each took twelve stocks and were required to <b>open and look at every chart image</b> before judging, corroborating the picture against the raw bars rather than reasoning from summary statistics.</li>
    <li>The twenty strongest buy calls went to five adversarial reviewers instructed to <b>refute</b> them: recompute every quoted level, re-derive R:R, measure stop distance in ATR, and check overhead supply.</li>
    <li>Cross-checked all 107 closes against Chartink's independent official close, which is what settled the split and truncation questions.</li>
  </ol>
</section>

<footer>
  <p><b>This is technical analysis, not investment advice.</b> Every level here is derived from price and volume alone — no earnings, no news, no valuation. Setups on the hourly timeframe decay quickly; anything based on Friday's close is stale after Monday's first hour, and a gap through a stop makes the stated risk theoretical.</p>
  <p>Prices are the 21 Aug 2026 session close, cross-verified against Chartink. R:R figures are to target 1 at the corrected entry and stop.</p>
</footer>
</div>
"""
open(f'{S}/report.html','w').write(HTML)
print('written', os.path.getsize(f'{S}/report.html')//1024, 'KB')
