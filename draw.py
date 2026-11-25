#!/usr/bin/env python3
"""Render one day of world news as a newspaper front page.

The sheet is 1024 by 1024 pixels and covers Wednesday 25 November
2026: three lead stories illustrated with real news photographs,
ten shorter briefs, a UTC timeline of the day, a strip of six
numbers, a world map carrying numbered pins, a 35-item list of
further stories, and a box dating the older news that was left
out on purpose.

Everything is drawn locally with Pillow. There is no network, no
clock and no randomness, so two runs write the same PNG byte for
byte. Story sources are named beside each item on the page; see
README.md for the photo credits and the source digests.
"""

import math
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

PAGE_W = 1024
PAGE_H = 1024
FOLDER = Path(__file__).resolve().parent
TARGET = FOLDER / "entry.png"

PAPER = (242, 237, 226)
CARD = (255, 255, 255)
CARD_EDGE = (208, 199, 178)
CARD_SHADE = (214, 206, 188)
GOLD = (216, 178, 92)
NUMBERS_BAND = (234, 229, 214)
BOTTOM_WASH = (233, 237, 235)
BAND_LINE = (198, 190, 168)
COLUMN_LINE = (228, 222, 206)
GRAIN_DOT = (237, 232, 220)
INK = (26, 26, 26)
SIGNAL_RED = (178, 34, 34)
MASTHEAD = (24, 48, 84)
MUTED = (110, 110, 105)
HAIRLINE = (60, 60, 60)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_PLAIN = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_PLAIN = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def face(path, size):
    return ImageFont.truetype(path, size)


def fold(pen, text, fnt, width):
    """Greedy word wrap to a pixel width; returns the lines."""
    words = text.split()
    rows = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if pen.textlength(trial, font=fnt) <= width:
            current = trial
        else:
            if current:
                rows.append(current)
            current = word
    if current:
        rows.append(current)
    return rows


def block(pen, left, top, text, fnt, width, fill=INK, leading=None, limit=None):
    """Set a wrapped paragraph; returns the y just below it."""
    rows = fold(pen, text, fnt, width)
    if limit:
        rows = rows[:limit]
    step = leading or int(fnt.size * 1.18)
    for row in rows:
        pen.text((left, top), row, font=fnt, fill=fill)
        top += step
    return top


RENDERS = FOLDER / "assets3d"
PHOTOS = FOLDER / "photos"
CANVAS = None


def place_cover(pen, folder, key, suffix, left, top, wide, tall):
    """Cover-crop an image file into a panel; False when it is missing."""
    path = folder / f"{key}.{suffix}"
    if CANVAS is None or not path.exists():
        return False
    shot = Image.open(path).convert("RGB")
    sw, sh = shot.size
    scale = max(wide / sw, tall / sh)
    shot = shot.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    ox = (shot.width - wide) // 2
    oy = (shot.height - tall) // 2
    shot = shot.crop((ox, oy, ox + wide, oy + tall))
    CANVAS.paste(shot, (left, top))
    return True


def flat_night_city(pen, left, top, wide, tall):
    pen.rectangle([left, top, left + wide, top + tall], fill=(28, 43, 74))
    pen.ellipse([left + wide - 52, top + 10, left + wide - 22, top + 40],
                fill=(240, 230, 190))
    # skyline with one block knocked down
    for bx0, bw0, bh0 in [(0, 34, 62), (38, 30, 84), (72, 36, 56),
                          (150, 40, 92), (196, 34, 70), (236, 38, 80),
                          (278, 30, 60)]:
        pen.rectangle([left + bx0, top + tall - bh0, left + bx0 + bw0,
                       top + tall], fill=(16, 24, 44))
        for wy0 in range(top + tall - bh0 + 8, top + tall - 6, 12):
            for wx0 in range(left + bx0 + 6, left + bx0 + bw0 - 6, 11):
                pen.rectangle([wx0, wy0, wx0 + 4, wy0 + 5], fill=(255, 205, 90))
    # rubble and a searchlight where the block fell
    pen.polygon([(left + 108, top + tall), (left + 128, top + tall - 46),
                 (left + 150, top + tall)], fill=(70, 70, 78))
    pen.polygon([(left + 118, top + tall - 46), (left + 150, top + 22),
                 (left + 186, top + 22), (left + 158, top + tall - 40)],
                fill=(255, 220, 130))
    pen.ellipse([left + 96, top + tall - 18, left + wide - 8, top + tall - 4],
                fill=(120, 90, 60))
    pen.ellipse([left + 120, top + tall - 12, left + 150, top + tall - 2],
                fill=(200, 120, 40))


def flat_empty_summit(pen, left, top, wide, tall):
    pen.rectangle([left, top, left + wide, top + tall], fill=(16, 92, 92))
    # globe, cracked down the middle
    cx0, cy0, r0 = left + wide // 2, top + 52, 34
    pen.ellipse([cx0 - r0, cy0 - r0, cx0 + r0, cy0 + r0], fill=(120, 200, 190))
    pen.ellipse([cx0 - r0, cy0 - r0, cx0 + r0, cy0 + r0],
                outline=(10, 60, 60), width=2)
    pen.arc([cx0 - 20, cy0 - 26, cx0 + 20, cy0 + 26], 300, 60,
            fill=(10, 60, 60), width=2)
    pen.line([cx0 - 8, cy0 - 30, cx0 + 4, cy0 - 8, cx0 - 6, cy0 + 12,
              cx0 + 10, cy0 + 30], fill=(10, 60, 60), width=3)
    # chairs nobody sat in, around the table
    pen.rectangle([left + 30, top + tall - 34, left + wide - 30, top + tall - 22],
                  fill=(120, 72, 32))
    for cx1 in (left + 44, left + 130, left + 216, left + 268):
        pen.rectangle([cx1, top + tall - 58, cx1 + 26, top + tall - 34],
                      fill=(200, 170, 120))
        pen.rectangle([cx1 + 4, top + tall - 22, cx1 + 22, top + tall - 6],
                      fill=(160, 130, 90))


def flat_strait_attack(pen, left, top, wide, tall):
    pen.rectangle([left, top, left + wide, top + tall], fill=(30, 95, 138))
    pen.ellipse([left + 18, top + 12, left + 52, top + 40], fill=(255, 220, 120))
    # tanker, red waterline
    pen.rectangle([left + 60, top + 62, left + 250, top + 92], fill=(30, 30, 34))
    pen.rectangle([left + 60, top + 86, left + 250, top + 92], fill=(178, 34, 34))
    for cx1 in range(left + 74, left + 240, 34):
        pen.rectangle([cx1, top + 44, cx1 + 24, top + 62], fill=(220, 200, 160))
    pen.rectangle([left + 248, top + 34, left + 268, top + 62],
                  fill=(240, 240, 240))
    # blast, then two spiked mines under the water
    for dx0, dy0, r0 in [(0, 0, 16), (12, -8, 11), (-12, -6, 10), (6, 10, 9)]:
        pen.ellipse([left + 286 + dx0 - r0, top + 30 + dy0 - r0,
                     left + 286 + dx0 + r0, top + 30 + dy0 + r0],
                    fill=(255, 180, 40))
    pen.ellipse([left + 278, top + 22, left + 294, top + 38], fill=(255, 240, 160))
    for mx0, my0 in [(left + 34, top + 104), (left + 120, top + 110)]:
        pen.ellipse([mx0 - 7, my0 - 7, mx0 + 7, my0 + 7], fill=(16, 16, 16))
        for ang0 in range(0, 360, 45):
            pen.line([mx0, my0,
                      mx0 + int(11 * math.cos(math.radians(ang0))),
                      my0 + int(11 * math.sin(math.radians(ang0)))],
                     fill=(16, 16, 16), width=2)
    pen.arc([left + 8, top + 96, left + 90, top + 122], 180, 360,
            fill=(200, 230, 240), width=2)
    pen.arc([left + 150, top + 100, left + 240, top + 124], 180, 360,
            fill=(200, 230, 240), width=2)


def night_scene(pen, left, top, wide, tall):
    if not place_cover(pen, RENDERS, "kyiv", "png", left, top, wide, tall):
        flat_night_city(pen, left, top, wide, tall)


def summit_scene(pen, left, top, wide, tall):
    if not place_cover(pen, RENDERS, "cop31", "png", left, top, wide, tall):
        flat_empty_summit(pen, left, top, wide, tall)


def strait_scene(pen, left, top, wide, tall):
    if not place_cover(pen, RENDERS, "hormuz", "png", left, top, wide, tall):
        flat_strait_attack(pen, left, top, wide, tall)


def thumbnail(pen, left, top, wide, tall, kind):
    """Small flat illustration for the second-tier panels."""
    if place_cover(pen, RENDERS, kind, "png", left, top, wide, tall):
        return
    # Every panel sits on a quiet tint matched to the page. Loud
    # saturated grounds used to out-shout the hero photographs at
    # thumbnail size; these do not.
    ground = {
        "chart": (240, 235, 220),
        "pitch": (206, 224, 210),
        "court": (205, 219, 233),
        "badge": (234, 226, 198),
        "dome": (216, 224, 234),
        "refinery": (214, 214, 220),
        "fire": (233, 216, 205),
        "un": (205, 219, 233),
        "castle": (233, 210, 200),
        "ship": (205, 222, 231),
    }[kind]
    pen.rectangle([left, top, left + wide, top + tall], fill=ground)
    if kind == "chart":
        pts = [(left + 12, top + 18), (left + 50, top + 30), (left + 90, top + 22),
               (left + 130, top + 40), (left + 168, top + 48)]
        pen.line(pts, fill=SIGNAL_RED, width=4)
        pen.polygon(pts + [(left + 168, top + tall), (left + 12, top + tall)],
                    fill=(178, 34, 34, 60))
        pen.text((left + 12, top + tall - 20), "-3.7%",
                 font=face(SANS_BOLD, 16), fill=SIGNAL_RED)
    elif kind == "pitch":
        # pale lines disappear on the sage ground, so the pitch is
        # drawn in dark green ink instead of white
        pen.rectangle([left + 10, top + 8, left + wide - 10, top + tall - 8],
                      outline=(52, 110, 70), width=2)
        pen.line([left + wide // 2, top + 8, left + wide // 2, top + tall - 8],
                 fill=(52, 110, 70), width=2)
        pen.ellipse([left + wide // 2 - 14, top + tall // 2 - 14,
                     left + wide // 2 + 14, top + tall // 2 + 14],
                    fill=(240, 246, 240), outline=(52, 110, 70), width=2)
    elif kind == "court":
        pen.rectangle([left + 12, top + 8, left + wide - 12, top + tall - 8],
                      outline=(40, 80, 130), width=2)
        pen.line([left + wide // 2, top + 8, left + wide // 2, top + tall - 8],
                 fill=(40, 80, 130), width=2)
        pen.ellipse([left + wide // 2 - 7, top + 14, left + wide // 2 + 7,
                     top + 28], fill=(214, 196, 60))
    elif kind == "badge":
        cx0, cy0 = left + wide // 2, top + tall // 2
        pen.polygon([(cx0, cy0 - 20), (cx0 + 18, cy0 - 6), (cx0 + 12, cy0 + 16),
                     (cx0 - 12, cy0 + 16), (cx0 - 18, cy0 - 6)],
                    fill=(200, 160, 40))
        pen.text((cx0 - 5, cy0 - 8), "$", font=face(SANS_BOLD, 16),
                 fill=(255, 255, 255))
    elif kind == "dome":
        pen.rectangle([left + 20, top + tall - 16, left + wide - 20, top + tall - 8],
                      fill=(120, 140, 175))
        pen.pieslice([left + wide // 2 - 34, top + 6, left + wide // 2 + 34,
                      top + tall - 10], 180, 360, fill=(120, 140, 175))
        pen.rectangle([left + wide // 2 - 3, top + 2, left + wide // 2 + 3,
                       top + 12], fill=(40, 60, 120))
    elif kind == "refinery":
        for tx0 in (left + 20, left + 60, left + 100, left + 140):
            pen.rectangle([tx0, top + 18, tx0 + 22, top + tall - 10],
                          fill=(120, 120, 135))
        pen.polygon([(left + 118, top + 6), (left + 132, top + 22),
                     (left + 118, top + 34)], fill=(255, 150, 40))
        pen.ellipse([left + 150, top + 8, left + 168, top + 26],
                    fill=(255, 180, 60))
    elif kind == "fire":
        pen.polygon([(left + wide // 2, top + 6),
                     (left + wide // 2 + 22, top + 34),
                     (left + wide // 2 + 10, top + 50),
                     (left + wide // 2 - 10, top + 50),
                     (left + wide // 2 - 22, top + 34)], fill=(255, 120, 30))
        pen.ellipse([left + wide // 2 - 8, top + 30, left + wide // 2 + 8,
                     top + 48], fill=(255, 200, 60))
    elif kind == "un":
        pen.ellipse([left + wide // 2 - 22, top + 8, left + wide // 2 + 22,
                     top + 52], fill=(235, 242, 250))
        pen.text((left + wide // 2 - 12, top + 18), "UN",
                 font=face(SANS_BOLD, 18), fill=(30, 70, 140))
    elif kind == "castle":
        pen.rectangle([left + 30, top + 26, left + wide - 30, top + tall - 10],
                      fill=(250, 244, 236))
        pen.polygon([(left + 20, top + 28), (left + wide // 2, top + 6),
                     (left + wide - 20, top + 28)], fill=(160, 30, 30))
        pen.rectangle([left + wide // 2 - 5, top + 34, left + wide // 2 + 5,
                       top + tall - 10], fill=(120, 30, 30))
    elif kind == "ship":
        pen.polygon([(left + 20, top + 34), (left + wide - 20, top + 34),
                     (left + wide - 34, top + 50), (left + 34, top + 50)],
                    fill=(20, 20, 24))
        pen.rectangle([left + 70, top + 16, left + 110, top + 34],
                      fill=(220, 200, 160))
        pen.ellipse([left + wide - 44, top + 8, left + wide - 20, top + 32],
                    fill=(255, 220, 120))


# ---------------------------------------------------------------- stories
# Each lead is (dateline, desk, picture key, headline, standfirst,
# confidence, source). Each brief adds its story number up front.
LEADS = [
    (
        "SANTA CLARA, USA",
        "TECHNOLOGY",
        "nvidia",
        "Nvidia sinks 7% as " "AI doubt spreads",
        "Shares fall after the Huang-return rally fades; "
        "lawmakers question Trump's role in reinstating "
        "the CEO. Nikkei down 2.76%, S&P 500 down 0.50%.",
        "CONFIRMED",
        "ONETURN / REUTERS",
    ),
    (
        "STRAIT OF HORMUZ",
        "SHIPPING",
        "hormuz",
        "Two tankers hit mines " "in the Strait",
        "Iran's Revolutionary Guards say two tankers "
        "struck naval mines; Saudi strikes on Hodeidah "
        "and Houthi threats widen the Iran war.",
        "CONFIRMED",
        "AP / ONETURN",
    ),
    (
        "ANTALYA, TURKEY",
        "CLIMATE",
        "cop31",
        "After COP31's collapse, oil states " "push their fix",
        "Two days after the talks failed, producers press "
        "carbon capture at the IMO while Nepal leaves "
        "Antalya with no flood aid at all.",
        "CONFIRMED",
        "DAILY EDITION",
    ),
]

BRIEFS = [
    (
        4,
        "SPACE",
        "SPACEFLIGHT",
        "astronaut",
        "Pakistan's first astronaut " "reaches Tiangong",
        "Pakistan sends its first astronaut to China's "
        "space station.",
        "CONFIRMED",
        "WE NEWS",
    ),
    (
        5,
        "DAKAR",
        "FOOTBALL",
        "senegal",
        "Senegal regain the Africa " "Cup crown",
        "Sport's court returns the CAN-2025 title to "
        "Senegal, ten months after a chaotic final.",
        "REPORTED",
        "HORIZON",
    ),
    (
        6,
        "WASHINGTON",
        "POLITICS",
        "dome",
        "Democrats take the House, " "259+ seats",
        "Democrats win a House majority of at least "
        "259 seats.",
        "CONFIRMED",
        "ONETURN",
    ),
    (
        7,
        "SHANGHAI",
        "TECH",
        "badge",
        "Huawei convicted in US " "trade-secrets case",
        "Huawei found guilty of stealing trade secrets "
        "in a US sanctions and trade-secret trial.",
        "CONFIRMED",
        "DAILY EDITION",
    ),
    (
        8,
        "BENGHAZI",
        "WAR",
        "ship",
        "Ukraine hits Russian warship " "off Libya",
        "Ukraine strikes a Russian warship off Libya; "
        "two Libyan soldiers die in strikes on Russian ships.",
        "REPORTED",
        "HORIZON",
    ),
    (
        9,
        "INDONESIA",
        "DISASTER",
        "fire",
        "Dozens trapped in " "Indonesian mine",
        "Rescuers search for dozens trapped in a "
        "100-metre-deep mine after heavy rains.",
        "REPORTED",
        "ONETURN",
    ),
    (
        10,
        "CARTAGENA",
        "CRIME",
        "badge",
        "Cartagena hostages " "all freed",
        "Armed men held about 20 hostages in a "
        "supermarket; all freed without casualties.",
        "CONFIRMED",
        "HORIZON",
    ),
    (
        11,
        "DHAKA",
        "LABOUR",
        "chart",
        "Garment wage up 36% " "after protests",
        "Bangladesh raises the textile minimum wage by "
        "36% after weeks of protests.",
        "CONFIRMED",
        "HORIZON",
    ),
    (
        12,
        "HONG KONG",
        "SOCIETY",
        "fire",
        "A year on from the " "Tai Po fire",
        "Hong Kong marks a year since the Tai Po fire.",
        "CONFIRMED",
        "ONETURN",
    ),
    (
        13,
        "MARKETS",
        "ENERGY",
        "chart",
        "Oil slides 21% " "in a month",
        "Brent crude is down 21% over the month at "
        "$87.49; Nasdaq falls 1.48%.",
        "CONFIRMED",
        "HORIZON",
    ),
]


MORE = [
    (
        14,
        "Solomon Islands + Australia sign " "security treaty",
        "ONETURN",
    ),
    (
        15,
        "Kilmar Ábrego García leaves US " "for Spain",
        "ONETURN",
    ),
    (
        16,
        "China investigates Shanghai party chief " "Chen Jining",
        "ONETURN",
    ),
    (
        17,
        "Iran flogs singer 74 times over " "unveiled concert",
        "ONETURN",
    ),
    (
        18,
        "DR Congo aircraft missing; rebels " "claim downing",
        "ONETURN",
    ),
    (
        19,
        "Pentagon criticises Canada's " "military spending",
        "ONETURN",
    ),
    (
        20,
        "Spain heads to snap " "election",
        "ONETURN",
    ),
    (
        21,
        "Zambia indicts opposition leader on " "treason charges",
        "ONETURN",
    ),
    (
        22,
        "Drone attacks on Khartoum draw " "condemnation",
        "ONETURN",
    ),
    (
        23,
        "Venezuela reveals $237.5bn " "public debt",
        "ONETURN",
    ),
    (
        24,
        "Argentina enters technical " "recession",
        "ONETURN",
    ),
    (
        25,
        "Small plane crashes in Gulf of Mexico; " "six dead",
        "HORIZON",
    ),
    (
        26,
        "WHO chief: end the US fuel " "blockade on Cuba",
        "HORIZON",
    ),
    (
        27,
        "Yemen: Saudi-led coalition strikes " "Hodeidah port",
        "HORIZON",
    ),
    (
        28,
        "Israel: Democrats suspend " "coalition talks",
        "HORIZON",
    ),
    (
        29,
        "Gaza: Israeli strikes kill 7, incl. " "security official",
        "SRI",
    ),
    (
        30,
        "South Korea: Russian jets enter " "air defence zone",
        "SRI",
    ),
    (
        31,
        "UK: two arrested after break-in at " "William's home",
        "SRI",
    ),
    (
        32,
        "US Army to detonate degraded " "chemicals today",
        "SRI",
    ),
    (
        33,
        "Ukraine asks €115bn foreign " "aid for 2027",
        "VODOMERI",
    ),
    (
        34,
        "China: top Politburo member probed " "in Xi purge",
        "VODOMERI",
    ),
    (
        35,
        "Ecuador floods hit Galápagos amid " "El Niño worries",
        "VODOMERI",
    ),
    (
        36,
        "Nepal leaves COP31 without " "flood aid",
        "DAILY EDITION",
    ),
    (
        37,
        "World court Myanmar genocide ruling " "faces test",
        "DAILY EDITION",
    ),
    (
        38,
        "China answers Starlink " "with Qianfan",
        "DAILY EDITION",
    ),
    (
        39,
        "Anthropic, OpenAI staff fear unreleased " "models unsafe",
        "AXIOS",
    ),
    (
        40,
        "Bangladesh: Hasina sets Dec 16 " "return date",
        "VODOMERI",
    ),
    (
        41,
        "EU court: Poland violated Afghan " "migrant's rights",
        "VODOMERI",
    ),
    (
        42,
        "Russian drone briefly enters " "Polish territory",
        "VODOMERI",
    ),
    (
        43,
        "India stops 'cockroach' drive leader " "flying to London",
        "SRI",
    ),
    (
        44,
        "Rebel group retreats in DR Congo after " "heavy clashes",
        "SRI",
    ),
    (
        45,
        "Iran vows 'all means' to counter " "US blockade",
        "SRI",
    ),
    (
        46,
        "Markets: Sensex rises 1.8% as " "India gains",
        "ONETURN",
    ),
    (
        47,
        "Markets: Gold $3,516, " "down 1.29%",
        "HORIZON",
    ),
    (
        48,
        "Cyber: 112 ransomware claims " "in 48 hours",
        "RANSOMLOOK",
    ),
]

DAYLINE = [
    ("00:58", "Russian jets in Korea ADIZ"),
    ("02:01", "Ukraine hits Russian craft"),
    ("04:12", "Sudan RSF commander turns"),
    ("05:46", "Huang cheered in China"),
    ("06:52", "Australia warns on US-China"),
    ("WEDNESDAY", "Nikkei closes -2.76%"),
]

FIGURES = [
    ("-7%", "Nvidia shares fall"),
    ("2", "tankers hit mines, Hormuz"),
    ("-2.76%", "Nikkei 225, Wednesday"),
    ("$87.41", "Brent crude, Wednesday"),
    ("48", "stories, one day"),
    ("7", "regions covered"),
]

# Rough continent outlines, as (longitude, latitude) points.
LAND = [
    [
        (-168, 66), (-140, 70), (-120, 71), (-95, 69), (-80, 62),
        (-75, 45), (-80, 32), (-90, 21), (-97, 16), (-105, 20),
        (-115, 30), (-125, 42), (-150, 60), (-168, 66),
    ],
    [
        (-70, 12), (-55, 5), (-50, -5), (-40, -20), (-55, -35),
        (-65, -45), (-70, -30), (-78, -5), (-80, 5), (-70, 12),
    ],
    [
        (-10, 36), (0, 43), (10, 45), (20, 40), (28, 41),
        (30, 36), (10, 36), (-5, 36), (-10, 36),
    ],
    [
        (30, 70), (60, 70), (100, 75), (140, 72), (170, 66),
        (180, 65), (160, 60), (140, 40), (120, 30), (100, 10),
        (80, 8), (60, 25), (45, 30), (35, 45), (30, 70),
    ],
    [
        (35, 32), (45, 30), (55, 25), (60, 15), (45, 12),
        (40, 18), (35, 32),
    ],
    [
        (10, 35), (20, 32), (30, 31), (35, 28), (30, 15),
        (20, 5), (10, 5), (10, 20), (15, 30), (10, 35),
    ],
    [
        (110, -12), (130, -12), (145, -15), (153, -27), (150, -38),
        (135, -35), (115, -33), (110, -12),
    ],
]

# (story number, longitude, latitude) for the numbered map pins.
MARKERS = [
    (1, -122, 37),
    (2, 56, 26),
    (3, 30, 37),
    (4, 116, 40),
    (5, -17, 15),
    (6, -77, 39),
    (7, 121, 31),
    (8, 20, 32),
    (9, 106, -6),
    (10, -75, 10),
    (11, 90, 24),
    (12, 114, 22),
    (13, 139, 36),
]


def paint_map(pen, left, top, wide, tall):
    pen.rectangle([left, top, left + wide, top + tall], fill=(222, 232, 228))

    def to_xy(lon, lat):
        return (left + int((lon + 170) / 360.0 * wide),
                top + int((72 - lat) / 140.0 * tall))

    for shape in LAND:
        pen.polygon([to_xy(lon, lat) for lon, lat in shape],
                    fill=(170, 185, 140))
    for n, lon, lat in MARKERS:
        cx0, cy0 = to_xy(lon, lat)
        pen.ellipse([cx0 - 7, cy0 - 7, cx0 + 7, cy0 + 7], fill=SIGNAL_RED,
                    outline=(255, 255, 255))
        pen.text((cx0 - 3, cy0 - 6), str(n), font=face(SANS_BOLD, 9),
                 fill=(255, 255, 255))


def render_page():
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    global CANVAS
    CANVAS = sheet
    pen = ImageDraw.Draw(sheet)
    # Paper grain first: one-pixel dots on an 8-pixel grid, barely
    # darker than the page. Cards and bands drawn later cover most
    # of it; what shows in the margins is texture, never anything
    # sitting under text.
    pen.point([(gx, gy) for gx in range(4, PAGE_W, 8)
               for gy in range(4, PAGE_H, 8)], fill=GRAIN_DOT)
    margin = 22
    # Masthead band: deep navy, so the date is the first thing the
    # eye lands on. Kicker in gold, headline in cream-white.
    pen.rectangle([0, 0, PAGE_W, 123], fill=MASTHEAD)
    pen.text((margin, 10), "THE WORLD'S NEWS OF ONE DAY",
             font=face(SANS_BOLD, 13), fill=GOLD)
    strap = "48 STORIES  ·  7 REGIONS  ·  ALL FROM THIS WEDNESDAY"
    pen.text((PAGE_W - margin - pen.textlength(strap, font=face(SANS_BOLD, 13)),
              10), strap, font=face(SANS_BOLD, 13), fill=(220, 228, 238))
    pen.line([margin, 30, PAGE_W - margin, 30], fill=(120, 140, 175), width=1)
    headline = "Wednesday 25 November 2026"
    big = face(SERIF_BOLD, 56)
    pen.text(((PAGE_W - pen.textlength(headline, font=big)) / 2, 34),
             headline, font=big, fill=(250, 246, 236))
    standfirst = ("Nvidia sinks, Hormuz mines strike, COP31's collapse "
                  "echoes — every story here happened, or was first "
                  "reported, on this day.")
    italic = face(SERIF_ITALIC, 16)
    pen.text(((PAGE_W - pen.textlength(standfirst, font=italic)) / 2, 100),
             standfirst, font=italic, fill=(206, 216, 230))
    pen.rectangle([0, 123, PAGE_W, 126], fill=GOLD)
    # Timeline of the day, in UTC.
    pos_y = 126
    pen.text((margin, pos_y), "THE DAY IN UTC", font=face(SANS_BOLD, 11),
             fill=SIGNAL_RED)
    pen.line([margin + 92, pos_y + 6, PAGE_W - margin, pos_y + 6],
             fill=MUTED, width=1)
    pos_y += 16
    slot = (PAGE_W - 2 * margin) / len(DAYLINE)
    for i, (when, what) in enumerate(DAYLINE):
        centre = margin + slot * i + slot / 2
        pen.ellipse([centre - 3, pos_y, centre + 3, pos_y + 6],
                    fill=SIGNAL_RED)
        pen.text((centre - pen.textlength(when, font=face(SANS_BOLD, 10)) / 2,
                  pos_y + 9), when, font=face(SANS_BOLD, 10), fill=INK)
        label_w = pen.textlength(what, font=face(SANS_PLAIN, 9))
        pen.text((max(margin, min(PAGE_W - margin - label_w,
                                  centre - label_w / 2)), pos_y + 21),
                 what, font=face(SANS_PLAIN, 9), fill=(70, 70, 70))
    # Numbers strip on its own slightly darker band, so the six
    # figures read as one strip instead of six floating numbers.
    pos_y = 178
    pen.rectangle([margin, pos_y, PAGE_W - margin, pos_y + 58],
                  fill=NUMBERS_BAND)
    pen.line([margin, pos_y, PAGE_W - margin, pos_y], fill=BAND_LINE, width=1)
    pos_y += 6
    cell = (PAGE_W - 2 * margin) / 6
    for i, (figure, caption) in enumerate(FIGURES):
        cx0 = margin + cell * i
        big_num = face(SERIF_BOLD, 26)
        pen.text((cx0 + (cell - pen.textlength(figure, font=big_num)) / 2,
                  pos_y), figure, font=big_num, fill=INK)
        small_cap = face(SANS_PLAIN, 9)
        pen.text((cx0 + (cell - pen.textlength(caption, font=small_cap)) / 2,
                  pos_y + 32), caption, font=small_cap, fill=(70, 70, 70))
        if i:
            pen.line([cx0, pos_y + 2, cx0, pos_y + 44], fill=BAND_LINE, width=1)
    pos_y += 52
    pen.line([margin, pos_y, PAGE_W - margin, pos_y], fill=BAND_LINE, width=1)
    # Hero row, three across. Each hero sits on a white card with a
    # soft shadow, so the photos and headlines lift off the page
    # instead of floating on the same flat field as everything else.
    pos_y += 8
    hero_top = pos_y
    hero_w = (PAGE_W - 2 * margin - 16) / 3
    for i in range(3):
        left = margin + i * (hero_w + 8)
        pen.rectangle([left - 4, hero_top - 4, left + hero_w + 8,
                       hero_top + 262], fill=CARD_SHADE)
        pen.rectangle([left - 6, hero_top - 6, left + hero_w + 6,
                       hero_top + 260], fill=CARD, outline=CARD_EDGE, width=1)
    for i, (place, field, scene, headline, body, conf, src) in enumerate(LEADS):
        left = margin + i * (hero_w + 8)
        if not place_cover(pen, PHOTOS, scene, "jpg", int(left), hero_top,
                           int(hero_w), 118):
            thumbnail(pen, int(left), hero_top, int(hero_w), 118, "chart")
        pen.rectangle([left, hero_top + 118, left + hero_w, hero_top + 134],
                      fill=MASTHEAD)
        pen.text((left + 6, hero_top + 121), f"{i + 1}  {place}  ·  {field}",
                 font=face(SANS_BOLD, 10), fill=(255, 255, 255))
        text_y = hero_top + 140
        text_y = block(pen, left, text_y, headline, face(SERIF_BOLD, 21),
                       int(hero_w), leading=23, limit=3)
        text_y += 2
        text_y = block(pen, left, text_y, body, face(SANS_PLAIN, 11),
                       int(hero_w), leading=13, limit=4)
        text_y += 3
        pen.text((left, text_y), conf, font=face(SANS_BOLD, 10),
                 fill=SIGNAL_RED)
        pen.text((left + 74, text_y), src, font=face(SANS_BOLD, 10),
                 fill=(90, 90, 90))
    # Briefs, five across in two rows, on one white card behind all
    # ten, with hairline column dividers in the gaps. The briefs stop
    # competing with the heroes and read as one "more news" block.
    pos_y = hero_top + 268
    brief_w = (PAGE_W - 2 * margin - 32) / 5
    pen.rectangle([margin - 10, pos_y - 4, PAGE_W - margin + 10, pos_y + 270],
                  fill=CARD_SHADE)
    pen.rectangle([margin - 8, pos_y - 6, PAGE_W - margin + 8, pos_y + 268],
                  fill=CARD, outline=CARD_EDGE, width=1)
    for row in range(2):
        for col in range(5):
            n, place, field, kind, headline, body, conf, src = BRIEFS[row * 5 + col]
            left = margin + col * (brief_w + 8)
            top = pos_y + row * 132
            if kind in ("astronaut", "senegal"):
                if not place_cover(pen, PHOTOS, kind, "jpg", int(left), top,
                                   int(brief_w), 56):
                    thumbnail(pen, int(left), top, int(brief_w), 56, "chart")
            else:
                thumbnail(pen, int(left), top, int(brief_w), 56, kind)
            pen.text((left, top + 60), f"{n}  {place} · {field}",
                     font=face(SANS_BOLD, 9), fill=SIGNAL_RED)
            text_y = top + 74
            text_y = block(pen, left, text_y, headline, face(SERIF_BOLD, 14),
                           int(brief_w), leading=15, limit=2)
            text_y = block(pen, left, text_y + 1, body, face(SANS_PLAIN, 9),
                           int(brief_w), leading=11, limit=1)
            pen.text((left, top + 121), conf, font=face(SANS_BOLD, 9),
                     fill=SIGNAL_RED)
            pen.text((left + 62, top + 121), src, font=face(SANS_BOLD, 9),
                     fill=(90, 90, 90))
    for col in range(1, 5):
        div_x = margin + col * (brief_w + 8) - 4
        pen.line([div_x, pos_y + 2, div_x, pos_y + 260], fill=COLUMN_LINE,
                 width=1)
    # Bottom section — map and date check on the left, the 35-item
    # list on the right — on one pale blue-grey wash with a navy
    # top rule, so it reads as a closing section instead of more
    # text on the same field.
    pos_y = hero_top + 268 + 264 + 6
    pen.rectangle([margin - 8, pos_y - 6, PAGE_W - margin + 8, PAGE_H - 38],
                  fill=BOTTOM_WASH)
    pen.line([margin - 8, pos_y, PAGE_W - margin + 8, pos_y], fill=MASTHEAD,
             width=2)
    pos_y += 6
    pen.text((margin, pos_y), "WHERE IT HAPPENED", font=face(SANS_BOLD, 11),
             fill=SIGNAL_RED)
    pen.text((margin + 340, pos_y),
             "ALSO ON WEDNESDAY 25 NOVEMBER — 35 MORE STORIES",
             font=face(SANS_BOLD, 11), fill=SIGNAL_RED)
    pos_y += 16
    pen.rectangle([margin - 4, pos_y - 4, margin + 312, pos_y + 112],
                  fill=CARD, outline=CARD_EDGE, width=1)
    paint_map(pen, margin, pos_y, 308, 108)
    also_x = margin + 340
    col_w = (PAGE_W - margin - also_x - 12) / 2
    for idx, (n, text, src) in enumerate(MORE):
        col = idx // 18
        r = idx % 18
        left = also_x + col * (col_w + 12)
        yy = pos_y + r * 11
        pen.text((left, yy), f"{n}.", font=face(SANS_BOLD, 10),
                 fill=SIGNAL_RED)
        pen.text((left + 20, yy), text, font=face(SANS_PLAIN, 10), fill=INK)
    # Date check under the map, on white so the small text sits on
    # white rather than on the blue-grey wash.
    check_y = pos_y + 116
    pen.rectangle([margin, check_y, margin + 308, check_y + 62], fill=CARD)
    pen.rectangle([margin, check_y, margin + 308, check_y + 62],
                  outline=SIGNAL_RED, width=2)
    pen.text((margin + 6, check_y + 4), "DATE CHECK — LEFT OUT AS OLDER NEWS",
             font=face(SANS_BOLD, 10), fill=SIGNAL_RED)
    block(pen, margin + 6, check_y + 20,
          "COP31 collapse (Sun 22 Nov) · "
          "Kyiv region strikes (Mon 23 Nov) · Anthropic IPO $83 "
          "(Wed 18 Nov) · Shenzhen summit (Thu 19 Nov)",
          face(SANS_PLAIN, 10), 296, leading=12, limit=3)
    foot_y = PAGE_H - 26
    pen.line([margin, foot_y - 6, PAGE_W - margin, foot_y - 6],
             fill=HAIRLINE, width=1)
    pen.text((margin, foot_y),
             "Every story here happened, or was first reported, on "
             "Wednesday 25 November 2026. Claims are attributed. "
             "Sources named beside each story · photos: real news photos.",
             font=face(SANS_PLAIN, 9), fill=(70, 70, 70))
    sheet.save(TARGET, "PNG", optimize=True)
    print(f"wrote {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    render_page()
