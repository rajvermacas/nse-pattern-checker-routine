# Sub-7% base pass

Constraint: base depth **< 7%**. Applied to all 107 screener stocks, not just the RSI top 15
(both top-15 candidates fail it outright — APLAPOLLO 24.6%, BLISSGVS 19.1%).

## Funnel

    107 scanned
     -> 75  have a sub-7% base somewhere in the last 150 bars
     -> 22  still live (price within -6%/+8% of the rim, rim <= 50 bars old)
     -> 22  charted and read visually
     ->  6  graded A

The 53 dropped at step 2 are historical bases that already resolved and ran 30-200%
past the rim (HFCL +213%, YASHO +186%, DIACABS +115%). Depth alone does not make a
setup; the base has to still be there.

## The RSI cross-check

**Zero of the 22 live shallow bases were in the RSI top 15.** Their median RSI rank is
76 of 107. This is the same structural fact the RSI-descending run surfaced, seen from
the other side: a stock sitting in a tight base has, by construction, a mid-range RSI.
Ranking by RSI descending and screening for live bases select disjoint sets.

## Detector limitations the visual pass caught

Depth is a scalar and cannot see shape. Six of the 22 were rejected because the
mechanically-measured depth described something that is not a base:

- **V-spike** — one violent bar makes the low and price snaps back. The shallow number
  is an accident of where that single bar's low landed (HCG, PRUDENT, ENDURANCE).
- **Post-spike volatility** — the rim is a single gap bar and the "base" is the
  digestion of it (LUMAXTECH, ALIVUS).
- **Stale span** — the detected base already resolved and then failed, so the rim is no
  longer a live pivot (MOTILALOFS broke out then collapsed on the chart's largest red
  bar; RBLBANK's base low was undercut weeks later; NAM-INDIA's span is 40 bars old).
- **Unfinished decline** — a stair-step lower that has not stabilised, shaded as a base
  (HEROMOTOCO).

A useful inverse signal also appeared: in a real base volume contracts and range
narrows. In PRUDENT the widest-range bar sits in the *middle* of the base on ~10x
average volume — range expanding inside a base is distribution, not accumulation.

## Result

| Grade | n | Symbols |
|---|---|---|
| A | 6 | UJJIVANSFB, BAJAJ-AUTO, AETHER, SHRIRAMFIN, PNBHOUSING, ETERNAL |
| B | 5 | SOLARINDS, UNITDSPR, TMB, 360ONE, AUBANK |
| C | 5 | ASAHIINDIA, HCG, AJANTPHARM, PRUDENT, ENDURANCE |
| D | 6 | RBLBANK, LUMAXTECH, ALIVUS, NAM-INDIA, MOTILALOFS, HEROMOTOCO |

Four of the six A grades are still *inside* the base (entry ahead); two have just
cleared the rim. Every B is a case where the base and its breakout were sound but
already spent — price 4-8% extended with the entry gone.
