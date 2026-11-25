# THE WORLD — Wednesday 25 November 2026

One day of world news on a single newspaper front page: 1024 by
1024 pixels, 48 stories from 7 regions. Every story on the page
happened, or was first reported, on Wednesday 25 November 2026.

## Running it

- `python3 draw.py` paints the page and writes `entry.png`
  (1024x1024, under 1 MiB). Run it twice and the two PNGs are
  byte-identical: Pillow only, no network, no clock, no randomness.
- `mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py` copies
  the finished `entry.png` into `out/`, verifying the copy with
  SHA-256 first.

## What is on the page

- A navy masthead with the date, a UTC timeline of the day, and a
  strip of six numbers (-7% Nvidia, 2 tankers, -2.76% Nikkei,
  $87.41 Brent, 48 stories, 7 regions).
- Three lead stories with real news photographs: Nvidia sinks 7%
  as AI doubt spreads; two tankers hit mines in the Strait of
  Hormuz; after COP31's collapse, oil states push their fix.
- Ten shorter briefs, each with a small flat illustration or a
  real photo (astronaut, Senegal), a confidence tag and a source.
- A pinned world map, a 35-item "also on Wednesday" list, and a
  date-check box naming the older news that was left out on
  purpose: the COP31 collapse itself (Sun 22 Nov), Kyiv region
  strikes (Mon 23 Nov), the Anthropic IPO at $83 (Wed 18 Nov),
  and the Shenzhen summit (Thu 19 Nov).

## Photos

Real news photos in `photos/`, found through web search:

- `nvidia.jpg` — Jensen Huang on stage (Getty via coaihk.com)
- `hormuz.jpg` — an oil tanker in the Strait of Hormuz (tbsnews.net)
- `cop31.jpg` — a #COP31 sign in Antalya (qna.org.qa)
- `astronaut.jpg` — a rocket launch (wenewsenglish.com; the
  article image for the Pakistan astronaut story)
- `senegal.jpg` — Senegal lifting the Africa Cup trophy (espncdn.com)

The other small panels use flat Pillow drawings: a night skyline,
a cracked globe over empty chairs, a tanker among mines, and ten
thumbnail scenes (chart, pitch, court, badge, dome, refinery,
fire, UN, castle, ship).

## Where the stories come from

OneTurn (oneturn.news), The Daily Edition No. 280
(thedailyedition.news), Horizon (horizonapp.link/en/2026/11/25),
Axios (Anthropic/OpenAI staff fears), AP, SRI (sri.org.pk),
Vodomeri (m.vodomeri.eu), WE News English, and RansomLook. Each
story carries its source beside it on the page. Confidence tags
read CONFIRMED where a named outlet reported the story, and
REPORTED where it rests on a single digest or a court decision
reported today.
