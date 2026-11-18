[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/zero-two-1836/world-news-18-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/zero-two-1836/world-news-18-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261118)

# World News — 18 November 2026, in One Image

make.fun bounty submission: **"Sum up 18 November's world news in one image"**
($250, no entry fee, deadline Fri 20 Nov 2026 07:00 WIB).

## What it does

`main.py` renders a single 1024×1024 PNG poster — **WORLD NEWS,
Wednesday, 18 November 2026** — built for the judge in RULES.txt:

- **It names the day, huge, in the header** — the judge's first criterion.
- **Six stories, each with a large drawn picture + a short bold label**,
  so a viewer who missed the day can tell what happened from the
  picture alone: a tanker under missile fire (US–Iran), the Kerch
  Bridge, a snowflake over a shelter tent (Gaza winter), a globe
  (COP31), an airliner (Trump in Manila), giant 007 (Pattinson is Bond).
- **Legible at ~300 pixels across** (the judge's craft criterion):
  every glyph is at least 21 output px tall; there is no small body
  text anywhere. Rendered at 2048×2048 and box-averaged down 2× for
  smooth anti-aliased edges.
- **Breadth**: conflict, war, crisis, climate, politics, culture, plus
  an "Also today" panel (N. Korea missile, Romania quake, Waymo, measles,
  Eisenkot).

Stories, as wire-reported on 18 November 2026:

1. **US–Iran war escalates** — US sinks five Iranian tankers; Iran
   strikes ships near Hormuz and fires missiles at a US base in Jordan.
2. **Ukraine hits Kerch Bridge again** — second night of strikes on the
   Crimea link as Russia hits bridges ahead of Thursday's summit.
3. **Gaza faces a freezing winter** — UN warns of more deaths from cold;
   1.7M displaced, 1.4M face acute hunger.
4. **COP31 talks enter final days** — 144 disputed items in Antalya
   before the summit ends Friday.
5. **Trump lands in Manila for Quad** — Quad talks ahead of a China
   visit; a would-be assassin is jailed for 27 years.
6. **Pattinson is the new James Bond** — Robert Pattinson named the
   next 007.

## How to run

```sh
python3 main.py
```

Writes the image to `/output/entry.png` (and to `output/entry.png`
next to the script as a fallback). One run takes ~10 seconds.

## Constraints honoured

- **Python 3.13, standard library only** — imports are `os`, `struct`,
  `zlib`. No third-party packages, no network access.
- **Deterministic** — same run produces byte-identical PNG every time
  (verified: three consecutive runs give the same SHA-256).
- **One image** — a single PNG at `/output/entry.png`, 1024×1024,
  ~24 KB (cap: at most 1024×1024 px and 1 MiB).

## History

- **v1** (round 3 submission `01a1ed5c`): 1024×742 text infographic,
  six story cards + "also today" strip. Live rank #4759 of 5061 —
  its small body text turned to mush at the ~300 px width the judge
  views, and no story had a picture.
- **v2** (this version): full poster redesign for the judge's criteria
  — big pictures, big type, no small text.
