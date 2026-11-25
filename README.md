# News Image 20261125 — Wednesday 25 November 2026

Front page, 1024x1024 PNG, 48 stories from 7 regions. Every story
happened, or was first reported, on Wednesday 25 November 2026.

## How it was built
- `draw.py` (Pillow, no network, no clock, no randomness) paints the
  page and writes `entry.png`. Two runs write byte-identical PNGs.
- `main.py` copies the finished `entry.png` to `$MAKEFUN_OUTPUT_DIR`.
- Real news photos in `photos/` (downloaded from web search, per the
  brief "ambil gambar berita di google aja tempel"):
  - `nvidia.jpg` — Jensen Huang on stage (Getty via coaihk.com)
  - `hormuz.jpg` — oil tanker in the Strait of Hormuz (tbsnews.net)
  - `cop31.jpg` — #COP31 sign, Antalya (qna.org.qa)
  - `astronaut.jpg` — rocket launch (wenewsenglish.com; the Pakistan
    astronaut story's article image)
  - `senegal.jpg` — Senegal lift the Africa Cup trophy (espncdn.com)
- The other small panels use the flat Pillow drawings carried over
  from the 23 November entry's `draw.py` (same layout template that
  the Nov 18 round's rank 1-3 entries used: masthead, UTC timeline,
  numbers strip, 3 heroes, 10 small panels, pinned map, also-on list,
  date-check box, confidence tag + source on every story).

## Story sources (25 Nov 2026 digests)
OneTurn (oneturn.news), The Daily Edition No. 280
(thedailyedition.news), Horizon (horizonapp.link/en/2026/11/25),
Axios (Anthropic/OpenAI staff fears), SRI (sri.org.pk), Vodomeri
(m.vodomeri.eu), WE News English, RansomLook. Each story carries its
source beside it on the page; confidence tags are CONFIRMED (named
outlet reporting) or REPORTED (single digest / court decision
reported today).

## Leads
1. Nvidia sinks 7% as AI doubt spreads (Nikkei -2.76%, S&P -0.50%)
2. Two tankers hit mines in the Strait of Hormuz
3. After COP31's collapse, oil states push carbon capture; Nepal
   leaves Antalya with no flood aid

## Date check (left out as older news)
COP31 collapse itself (Sun 22 Nov) · Kyiv region strikes (Mon 23
Nov) · Anthropic IPO $83 (Wed 18 Nov) · Shenzhen summit (Thu 19 Nov)

## Verify
- `python3 draw.py` → `entry.png` (1024x1024, < 1 MiB)
- `mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py`
