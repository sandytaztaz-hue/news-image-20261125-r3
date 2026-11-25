#!/usr/bin/env python3
"""Render the Sum 25 broadsheet: one 1024x1024 PNG summing up the world news
of Wednesday 25 November 2026. 39 stories, 7 regions, every story dated that day.

Run: python3 render.py   -> writes entry.png next to this file.
Deterministic: fixed layout, fixed fonts, no randomness, no timestamps.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

NAVY = (15, 42, 77)
NAVY_D = (10, 30, 56)
RED = (176, 30, 36)
RED_D = (140, 20, 26)
GOLD = (201, 162, 39)
GOLD_L = (245, 214, 120)
INK = (20, 20, 20)
MUTED = (85, 85, 85)
FAINT = (150, 150, 150)
PAPER = (255, 255, 255)
PANEL = (243, 244, 246)
LINE = (200, 203, 208)
GREEN = (30, 122, 52)
AMBER = (178, 106, 0)
BLUE = (29, 78, 158)
TEAL = (14, 124, 123)
PURPLE = (106, 63, 160)
GREY = (102, 102, 102)

SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def F(path, size):
    return ImageFont.truetype(path, int(round(size)))


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit_size(draw, text, path, start, minimum, max_w):
    """Largest font size (<= start, >= minimum) whose text fits max_w."""
    size = start
    while size > minimum:
        f = F(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 0.5
    return F(path, minimum)


def draw_lines(draw, x, y, lines, font, fill, leading=None, align="left", width=None):
    """Draw lines starting at (x, y); returns y just below the last line."""
    if leading is None:
        leading = int(font.size * 1.22)
    for ln in lines:
        if align == "center" and width is not None:
            lx = x + (width - draw.textlength(ln, font=font)) / 2
        elif align == "right" and width is not None:
            lx = x + width - draw.textlength(ln, font=font)
        else:
            lx = x
        draw.text((lx, y), ln, font=font, fill=fill)
        y += leading
    return y


def text_block(draw, x, y, max_w, text, path, size, fill, max_lines,
               min_size=7.0, leading=None):
    """Wrap text into a box, shrinking the font until it fits max_lines.
    Returns the y just below the block."""
    size_now = size
    while size_now >= min_size:
        f = F(path, size_now)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            break
        size_now -= 0.5
    f = F(path, size_now)
    lines = wrap(draw, text, f, max_w)[:max_lines]
    return draw_lines(draw, x, y, lines, f, fill, leading=leading)


def chip(draw, x_right, y, label, fill):
    """Small verification chip, right-aligned at x_right. Returns its left x."""
    f = F(SANS_B, 8)
    tw = draw.textlength(label, font=f)
    w = int(tw) + 12
    h = 14
    x0 = int(x_right - w)
    draw.rounded_rectangle([x0, y, x_right, y + h], radius=4, fill=fill)
    draw.text((x0 + 6, y + 2.5), label, font=f, fill=(255, 255, 255))
    return x0


CHIP_FILL = {
    "CONFIRMED": GREEN, "REPORTED": AMBER, "OFFICIAL": BLUE,
    "CLAIM": GREY, "FORECAST": PURPLE, "SCHEDULED": TEAL,
    "SPORT": NAVY, "MKT": (46, 110, 46),
}


def label_panel(draw, cx, cy, text, max_w, size, fg, bg, pad_x=10, pad_y=5):
    """Big data label baked into a scene: centred at (cx, cy) on a panel."""
    f = fit_size(draw, text, SANS_B, size, 6.0, max_w)
    tw = draw.textlength(text, font=f)
    th = f.size
    x0 = cx - tw / 2 - pad_x
    y0 = cy - th / 2 - pad_y
    x1 = cx + tw / 2 + pad_x
    y1 = cy + th / 2 + pad_y + 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=bg)
    draw.text((cx - tw / 2, cy - th / 2), text, font=f, fill=fg)


def hline(draw, x0, x1, y, fill=LINE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def card_frame(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], outline=LINE, width=1)
    draw.line([(x0, y0), (x1, y0)], fill=NAVY, width=2)

# ---------------------------------------------------------------- data ----
STATS = [
    ("10/12", "HUAWEI COUNTS GUILTY"),
    ("\u2248500,000", "RUSSIANS KILLED (LEAKED)"),
    ("18th", "CREWED CHINA FLIGHT"),
    ("-15%", "SOFTBANK SHARES"),
    ("5,678", "EBOLA DEAD, CONGO"),
    ("A$740m", "SOLOMONS PACT"),
    ("11", "WOUNDED RIYADH"),
    ("$237.5bn", "VENEZUELA DEBT"),
]

TIMELINE = [
    ("00:18", "SHENZHOU LIFTS OFF"),
    ("02:46", "HODEIDAH STRIKES"),
    ("07:00", "GERMANY GDP FINAL"),
    ("13:30", "US DATA PILE"),
    ("17:20", "HUAWEI 10/12 VERDICT"),
    ("19:00", "BEIGE BOOK"),
    ("20:00", "UCL NIGHT"),
]

HEROES = [
    dict(num=1, scene="court", kicker="BROOKLYN, USA \u00b7 NORTH AMERICA",
         headline="Huawei guilty on 10 of 12 counts, and it will appeal",
         deck="A jury in Brooklyn ended an 11-week trial by convicting the "
              "telecom giant of bank fraud, sanctions violations and stealing "
              "trade secrets. Sentencing is set.",
         source="DOJ \u00b7 Bloomberg \u00b7 BBC", chip="CONFIRMED"),
    dict(num=2, scene="rocket", kicker="JIUQUAN, CHINA \u00b7 ASIA",
         headline="Shenzhou-24 lifts off with a Pakistani pilot aboard",
         deck="Long March 2F lifts off at 00:18 UTC with Tang Hongbo, Wu Yi "
              "and Pakistan's Muhammad Zeeshan Ali, 40. First Pakistani in "
              "orbit; first foreign astronaut on Tiangong. Beijing called "
              "the launch a complete success.",
         source="Xinhua / CMSA \u00b7 00:18 UTC", chip="CONFIRMED"),
    dict(num=3, scene="memorial", kicker="MOSCOW \u00b7 EUROPE",
         headline="Russia's own figures show nearly 500,000 war dead",
         deck="Data leaked from the state statistics service reveals how the "
              "invasion has changed mortality across Russia. Putin vows "
              "retaliation for strikes on refineries.",
         source="Mediazona \u00b7 Reuters", chip="REPORTED"),
]

SECONDS = [
    dict(num=4, scene="chart", kicker="SEOUL / TOKYO \u00b7 ASIA-PACIFIC",
         headline="Asia's AI stocks plunge again",
         deck="Seoul's Kospi sank about 6% and Tokyo's Nikkei about 3.8%; "
              "SoftBank fell 15%.",
         source="CNBC \u00b7 Al Jazeera", chip="CONFIRMED"),
    dict(num=5, scene="port", kicker="HODEIDAH, YEMEN \u00b7 MIDDLE EAST",
         headline="Saudi-led strikes hit Hodeidah port",
         deck="Raids early Wednesday; the Houthis threaten Jeddah and all "
              "Saudi Red Sea ports.",
         source="Arab News \u00b7 Reuters \u00b7 CNBC", chip="CONFIRMED"),
    dict(num=6, scene="treaty", kicker="HONIARA \u00b7 OCEANIA",
         headline="Solomons treaty puts Australia first",
         deck="A$740m and no foreign bases; Honiara told China it will not "
              "renew their 2022 pact.",
         source="ABC \u00b7 Reuters \u00b7 BBC", chip="CONFIRMED"),
    dict(num=7, scene="tariffs", kicker="WASHINGTON, USA \u00b7 NORTH AMERICA",
         headline="US readies Section 301 tariffs on 16 trading partners",
         deck="Levies up to 20% on China, 15% or less on the EU, Japan, "
              "South Korea and India.",
         source="Reuters \u00b7 AP", chip="REPORTED"),
    dict(num=8, scene="tower", kicker="RIYADH, SAUDI ARABIA \u00b7 MIDDLE EAST",
         headline="Houthi drone hits Riyadh tower, 11 hurt",
         deck="Drone hits the tallest tower; 11 wounded.",
         source="Al Jazeera", chip="CONFIRMED"),
    dict(num=9, scene="fire", kicker="FLINDERS ISLAND, TASMANIA \u00b7 OCEANIA",
         headline="Bushfire emergency: 'too late to leave'",
         deck="Emergency warning for Killiecrankie, Leeka and Mount Tanner; "
              "3,000 ha burning.",
         source="Tas Fire Service", chip="OFFICIAL"),
    dict(num=10, scene="ship", kicker="GULF OF FINLAND \u00b7 EUROPE",
         headline="Zelenskyy confirms Ukraine hit a Russian ship",
         deck="Kyiv claims a Saturday drone strike on a Russian cargo ship. "
              "Norway urges caution.",
         source="Reuters", chip="CONFIRMED"),
    dict(num=11, scene="city", kicker="GAZA CITY \u00b7 MIDDLE EAST",
         headline="Gaza City strike kills at least four",
         deck="Israeli air strike hit a Shati camp apartment block, outlets say.",
         source="Al Jazeera \u00b7 Mehr", chip="CONFIRMED"),
    dict(num=12, scene="clinic", kicker="DR CONGO \u00b7 AFRICA",
         headline="Congo's Ebola deaths reach 5,678",
         deck="11,613 confirmed cases; survey finds violence against women up.",
         source="ABC \u00b7 Bloomberg", chip="CONFIRMED"),
    dict(num=13, scene="market", kicker="CARTAGENA \u00b7 SOUTH AMERICA",
         headline="Hostages held in a supermarket on a second day",
         deck="At least 20 remain inside after a failed armoured-car raid; "
              "30 were held in the shop.",
         source="AP \u00b7 El Tiempo", chip="REPORTED"),
]

ALSO = [
    (14, "FORECAST", "Thanksgiving-eve data pile: GDP, PCE, claims"),
    (15, "FORECAST", "October CPI due"),
    (16, "CLAIM", "Warship sunk off Benghazi"),
    (17, "REPORTED", "Houthis 60 km from Aden"),
    (18, "CONFIRMED", "11 killed near Kyiv"),
    (19, "REPORTED", "CIA, ODNI cyber breach"),
    (20, "SCHEDULED", "EU-Balkans summit opens"),
    (21, "SCHEDULED", "Africa summit ends in Accra"),
    (22, "OFFICIAL", "47,000 women killed in 2025"),
    (23, "SCHEDULED", "Swedish vote on PM today"),
    (24, "SCHEDULED", "Germany Q3 GDP final due"),
    (25, "SCHEDULED", "Fed Beige Book at 19:00 UTC"),
    (26, "SPORT", "UCL Matchday 5: PSG v Roma"),
    (27, "REPORTED", "Iran braces for winter gas cuts"),
    (28, "REPORTED", "Trump may weigh NATO-like Kyiv deal"),
    (29, "REPORTED", "EU announces new Russia sanctions"),
    (30, "CLAIM", "Iran: three tankers hit by mines"),
    (31, "MKT", "Dell lifts forecasts on record AI qtr"),
    (32, "MKT", "Venezuela public debt $237.5bn"),
    (33, "REPORTED", "China probes Politburo member Chen"),
    (34, "REPORTED", "Israeli strike kills Hamas security chief"),
    (35, "REPORTED", "NATO vows space defence vs Russia"),
    (36, "REPORTED", "US consumer confidence nears 2-yr high"),
    (37, "OFFICIAL", "US to host Copa America again in 2028"),
    (38, "SPORT", "Real Madrid rout PSV 5-1 in UCL"),
    (39, "REPORTED", "Malaysia to return 6,500 Rohingya"),
]

DATE_CHECK = [
    ("GTA 6", "19 Nov"),
    ("COP31 failure", "23 Nov"),
    ("DR Congo vote", "22 Nov"),
    ("Midterm vote", "4 Nov"),
    ("Man Utd 3-2 Roma comeback", "3 Nov"),
    ("Nepal PM ends India visit", "22-23 Nov"),
]

# (lon, lat) of each story number, for the map pins.
PINS = {
    1: (-74, 41), 2: (98.5, 40), 3: (40, 56), 4: (127, 37.5), 5: (42.9, 14.8),
    6: (160, -9.4), 7: (-77, 39), 8: (46.7, 24.6), 9: (148, -40),
    10: (28, 59.5), 11: (33.5, 31.5), 12: (23, -3), 13: (-75.5, 10.4),
    14: (-87, 41), 15: (-95, 30), 16: (20, 32.1), 17: (49, 12.5),
    18: (30.5, 50.4), 19: (-105, 40), 20: (23, 42), 21: (-0.2, 5.6),
    22: (15, 46), 23: (18, 59.3), 24: (13.4, 52.5), 25: (-84, 33),
    26: (2.35, 48.85), 27: (51.4, 35.7), 28: (20, 52), 29: (4.4, 50.8),
    30: (54, 26.5), 31: (-97, 30), 32: (-66, 10), 33: (116.4, 39.9),
    34: (36.8, 33.8), 35: (8, 53), 36: (-122, 37), 37: (-100, 39),
    38: (-3.7, 40.4), 39: (101.7, 3.1),
}

# Simplified but recognisable continent coastlines, as (lon, lat) rings.
N_AMERICA = [(-168, 66), (-150, 70), (-130, 71), (-110, 70), (-95, 69),
             (-85, 66), (-80, 73), (-70, 62), (-60, 55), (-55, 47),
             (-65, 44), (-70, 42), (-75, 36), (-80, 32), (-81, 26),
             (-84, 30), (-90, 21), (-88, 15), (-84, 12), (-80, 8),
             (-83, 9), (-90, 14), (-96, 16), (-104, 19), (-110, 23),
             (-115, 29), (-121, 34), (-124, 42), (-125, 49), (-132, 56),
             (-145, 60), (-158, 58), (-165, 60), (-168, 66)]
S_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-78, -12),
             (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
             (-71, -50), (-66, -55), (-68, -52), (-63, -41), (-57, -38),
             (-49, -28), (-41, -23), (-36, -9), (-35, -6), (-43, -3),
             (-50, 0), (-54, 5), (-60, 8), (-70, 11), (-77, 8), (-79, 9)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (3, 53),
          (7, 54), (8, 57), (10, 59), (6, 61), (12, 56), (18, 56),
          (21, 55), (24, 59), (28, 61), (30, 70), (38, 68), (44, 68),
          (42, 63), (38, 58), (34, 54), (30, 50), (28, 46), (23, 40),
          (20, 42), (15, 44), (12, 45), (8, 44), (3, 43), (0, 39),
          (-2, 37), (-6, 36), (-10, 36)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58.5), (-1, 57), (0, 53), (-5, 50)]
SCAND = [(5, 58), (10, 59), (12, 61), (15, 64), (18, 66), (21, 68),
         (25, 70), (28, 70), (30, 68), (26, 64), (22, 60), (18, 58),
         (12, 57), (8, 58), (5, 58)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, -1),
          (12, -5), (13, -10), (12, -17), (14, -22), (16, -28), (19, -34),
          (26, -34), (32, -28), (35, -24), (40, -16), (40, -10), (42, -4),
          (46, -1), (51, 2), (51, 10), (44, 11), (40, 15), (38, 18),
          (35, 22), (32, 27), (30, 31), (25, 32), (19, 33), (11, 34),
          (10, 37), (5, 37), (-6, 35)]
ASIA = [(28, 41), (30, 46), (32, 50), (35, 55), (40, 60), (44, 68),
        (50, 70), (60, 72), (70, 73), (80, 73), (90, 75), (100, 77),
        (110, 76), (120, 73), (130, 72), (140, 72), (150, 70), (158, 66),
        (162, 60), (158, 52), (155, 50), (150, 45), (142, 45), (140, 40),
        (135, 35), (130, 33), (127, 35), (122, 38), (120, 32), (118, 25),
        (112, 22), (108, 18), (105, 10), (103, 5), (100, 8), (98, 14),
        (94, 17), (91, 22), (88, 22), (85, 19), (80, 13), (77, 8),
        (75, 15), (72, 20), (68, 23), (62, 25), (57, 26), (52, 26),
        (50, 29), (48, 30), (44, 29), (40, 30), (36, 33), (33, 36), (28, 41)]
JAPAN = [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
         (140, 44), (142, 45), (144, 44), (141, 40), (139, 37), (136, 35),
         (132, 33), (130, 31)]
BORNEO = [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -4),
          (110, -2), (109, 1)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9),
              (147, -9), (141, -8), (136, -6), (131, -1)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (137, -38), (140, -38),
             (145, -38), (147, -39), (150, -37), (153, -32), (153, -27),
             (150, -23), (146, -19), (142, -15), (142, -11), (141, -13),
             (136, -12), (135, -15), (132, -12), (130, -13), (126, -14),
             (122, -17), (118, -20), (113, -22)]
LAND = [N_AMERICA, S_AMERICA, EUROPE, UK, SCAND, AFRICA, ASIA, JAPAN,
        BORNEO, NEW_GUINEA, AUSTRALIA]

LEGEND = ["Americas", "Europe", "Asia-Pacific", "Middle East", "Oceania",
          "Africa", "Global"]

# --------------------------------------------------------------- scenes ---
def _stars(draw, box, n=26):
    x0, y0, x1, y1 = box
    import random
    rnd = random.Random(25)
    for _ in range(n):
        x = rnd.randint(x0 + 3, x1 - 3)
        y = rnd.randint(y0 + 3, y1 - 12)
        r = rnd.choice([1, 1, 2])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))


def _person(draw, x, y, s, robe, skin=(232, 190, 150)):
    """Simple seated/standing figure: head + shoulders, scaled by s."""
    draw.ellipse([x - 5 * s, y - 16 * s, x + 5 * s, y - 6 * s], fill=skin)
    draw.polygon([(x - 11 * s, y + 12 * s), (x - 7 * s, y - 6 * s),
                  (x + 7 * s, y - 6 * s), (x + 11 * s, y + 12 * s)], fill=robe)


def scene_court(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(232, 220, 200))
    draw.rectangle([x0, y0, x1, y0 + h * 0.42], fill=(122, 82, 48))
    for i in range(5):
        lx = x0 + 14 + i * 18
        draw.rectangle([lx, y0 + 8, lx + 9, y0 + h * 0.42 - 6], fill=(60, 60, 90))
    # flags flanking the bench
    for fx, cols in ((x0 + 26, ((176, 30, 36), (255, 255, 255))),
                     (x1 - 46, ((15, 42, 77), (255, 255, 255)))):
        draw.rectangle([fx, y0 + 12, fx + 20, y0 + 44], fill=cols[0])
        draw.rectangle([fx, y0 + 12, fx + 20, y0 + 20], fill=cols[1])
        draw.line([(fx + 10, y0 + 44), (fx + 10, y0 + h * 0.62)], fill=(60, 45, 30), width=2)
    # judge behind the bench
    _person(draw, (x0 + x1) // 2, y0 + h * 0.52, 1.5, (20, 20, 20))
    # bench
    draw.rectangle([x0 + 40, y0 + h * 0.62, x1 - 40, y0 + h * 0.82], fill=(90, 55, 28))
    draw.rectangle([x0 + 40, y0 + h * 0.62, x1 - 40, y0 + h * 0.68], fill=(120, 75, 38))
    # seated figures in the gallery
    for i, px in enumerate((0.22, 0.38, 0.62, 0.78)):
        _person(draw, x0 + w * px, y1 - 8, 1.0, (40, 60, 110) if i % 2 else (90, 40, 40))
    label_panel(draw, (x0 + x1) // 2, y0 + 26, "10/12", w - 40, 30,
                (255, 255, 255), NAVY)


def scene_rocket(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(10, 20, 48))
    _stars(draw, box)
    # small station, upper right
    sx, sy = x1 - 78, y0 + 22
    draw.rectangle([sx, sy, sx + 44, sy + 7], fill=(190, 195, 205))
    draw.rectangle([sx - 16, sy + 1, sx, sy + 6], fill=(60, 90, 160))
    draw.rectangle([sx + 44, sy + 1, sx + 60, sy + 6], fill=(60, 90, 160))
    # ground
    draw.rectangle([x0, y1 - 18, x1, y1], fill=(26, 43, 26))
    # launch tower
    tx = x0 + w * 0.30
    draw.rectangle([tx, y0 + 30, tx + 16, y1 - 18], fill=(120, 125, 135))
    for gy in range(int(y0 + 36), int(y1 - 22), 12):
        draw.line([(tx, gy), (tx + 16, gy + 6)], fill=(90, 95, 105), width=2)
    # rocket body
    rx = x0 + w * 0.52
    # rocket body: nose cone is a triangle centred on the body axis
    # (apex over the body centre, base spanning the full body width),
    # so the nose and the body read as one aligned shape.
    draw.polygon([(rx + 32.5, y0 + 12), (rx + 13, y0 + 30),
                  (rx + 52, y0 + 30)], fill=(176, 30, 36))
    draw.rectangle([rx + 13, y0 + 30, rx + 39, y1 - 34], fill=(240, 240, 240))
    draw.rectangle([rx + 39, y0 + 30, rx + 52, y1 - 34], fill=(210, 210, 210))
    draw.polygon([(rx + 13, y1 - 34), (rx + 26, y1 - 18), (rx + 39, y1 - 34)],
                 fill=(255, 140, 0))
    draw.polygon([(rx + 16, y1 - 18), (rx + 26, y1 - 6), (rx + 36, y1 - 18)],
                 fill=(255, 220, 80))
    # big "24" on the rocket body
    f = F(SANS_B, 26)
    draw.text((rx + 17, y0 + 52), "24", font=f, fill=NAVY)
    # booster, flush against the body (the old red side strip is gone)
    draw.rectangle([rx + 1, y1 - 62, rx + 13, y1 - 34], fill=(200, 200, 200))


def scene_memorial(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(16, 24, 40))
    _stars(draw, box, n=18)
    # city silhouette
    base = y1 - 26
    heights = [34, 52, 28, 62, 40, 70, 30, 48, 36, 58]
    bw = w / len(heights)
    for i, hh in enumerate(heights):
        draw.rectangle([x0 + i * bw, base - hh, x0 + (i + 1) * bw - 2, base],
                       fill=(30, 42, 58))
        for wy in range(int(base - hh + 6), int(base - 4), 10):
            draw.rectangle([x0 + i * bw + 4, wy, x0 + i * bw + 8, wy + 4],
                           fill=(245, 214, 120))
    # candles along the bottom
    for i in range(9):
        cx = x0 + 18 + i * (w - 36) / 8
        draw.rectangle([cx - 3, y1 - 16, cx + 3, y1 - 4], fill=(240, 235, 220))
        draw.polygon([(cx, y1 - 26), (cx - 4, y1 - 16), (cx + 4, y1 - 16)],
                     fill=(255, 190, 60))
    label_panel(draw, (x0 + x1) // 2, y0 + 26, "\u2248500,000", w - 30, 30,
                GOLD_L, (10, 20, 36))


def scene_chart(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(255, 255, 255))
    for gy in range(1, 4):
        draw.line([(x0 + 6, y0 + h * gy / 4), (x1 - 6, y0 + h * gy / 4)],
                  fill=(230, 230, 230), width=1)
    pts = [(x0 + 14, y0 + 12), (x0 + w * 0.3, y0 + 20), (x0 + w * 0.5, y0 + 34),
           (x0 + w * 0.7, y0 + 44), (x1 - 14, y1 - 12)]
    draw.line(pts, fill=(176, 30, 36), width=3, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(176, 30, 36))
    draw.rectangle([x0 + 10, y1 - 10, x1 - 10, y1 - 6], fill=(200, 200, 200))
    label_panel(draw, (x0 + x1) // 2, y0 + h * 0.38, "-15%", w - 60, 26,
                (255, 255, 255), RED)


def scene_port(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y0 + h * 0.6], fill=(191, 217, 232))
    draw.rectangle([x0, y0 + h * 0.6, x1, y1], fill=(46, 110, 158))
    # cranes
    for cx in (0.22, 0.55, 0.82):
        bx = x0 + w * cx
        draw.rectangle([bx - 3, y0 + 10, bx + 3, y0 + h * 0.6], fill=(60, 60, 60))
        draw.line([(bx, y0 + 12), (bx + 26, y0 + 26)], fill=(60, 60, 60), width=3)
        draw.line([(bx, y0 + 26), (bx + 20, y0 + 26)], fill=(60, 60, 60), width=2)
    # containers + ship
    draw.rectangle([x0 + 12, y0 + h * 0.62, x1 - 12, y0 + h * 0.8], fill=(40, 40, 40))
    for i, col in enumerate(((176, 30, 36), (201, 162, 39), (29, 78, 158))):
        draw.rectangle([x0 + 20 + i * 34, y0 + h * 0.52, x0 + 48 + i * 34,
                        y0 + h * 0.62], fill=col)
    # smoke
    for sx, sy, r in ((0.3, 0.22, 9), (0.36, 0.16, 7), (0.68, 0.2, 8)):
        draw.ellipse([x0 + w * sx - r, y0 + h * sy - r, x0 + w * sx + r,
                      y0 + h * sy + r], fill=(120, 120, 120))
    label_panel(draw, (x0 + x1) // 2, y0 + h * 0.42, "HODEIDAH PORT", w - 16, 15,
                (255, 255, 255), NAVY)


def scene_treaty(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(238, 232, 218))
    # two flags on poles
    for fx, field, stars in ((x0 + 30, (0, 40, 120), True),
                             (x1 - 62, (0, 90, 60), False)):
        draw.line([(fx, y0 + 8), (fx, y0 + h * 0.62)], fill=(90, 70, 40), width=2)
        draw.rectangle([fx, y0 + 8, fx + 32, y0 + 28], fill=field)
        if stars:
            for sx, sy in ((8, 6), (20, 10), (12, 14), (24, 16)):
                draw.ellipse([fx + sx - 1, y0 + sy - 1, fx + sx + 1, y0 + sy + 1],
                             fill=(255, 255, 255))
        else:
            draw.polygon([(fx, y0 + 8), (fx + 32, y0 + 18), (fx, y0 + 28)],
                         fill=(0, 140, 90))
    # table and document
    draw.rectangle([x0 + 14, y0 + h * 0.66, x1 - 14, y0 + h * 0.78], fill=(122, 82, 48))
    draw.rectangle([x0 + 14, y0 + h * 0.78, x1 - 14, y1 - 4], fill=(100, 66, 38))
    draw.rectangle([(x0 + x1) // 2 - 22, y0 + h * 0.58, (x0 + x1) // 2 + 22,
                    y0 + h * 0.66], fill=(255, 255, 255))
    draw.line([((x0 + x1) // 2 - 16, y0 + h * 0.61),
               ((x0 + x1) // 2 + 16, y0 + h * 0.61)], fill=(120, 120, 120), width=1)
    draw.line([((x0 + x1) // 2 - 16, y0 + h * 0.64),
               ((x0 + x1) // 2 + 8, y0 + h * 0.64)], fill=(120, 120, 120), width=1)
    _person(draw, x0 + w * 0.30, y0 + h * 0.62, 0.9, (30, 60, 110))
    _person(draw, x0 + w * 0.70, y0 + h * 0.62, 0.9, (60, 60, 60))
    label_panel(draw, (x0 + x1) // 2, y0 + 22, "A$740m", w - 60, 20,
                (255, 255, 255), NAVY)


def scene_tariffs(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(255, 255, 255))
    bars = [("CN", 20, RED), ("EU", 15, AMBER), ("JP", 12, (110, 110, 110)),
            ("IN", 10, (90, 130, 90))]
    bw = 26
    gap = (w - 4 * bw) / 5
    for i, (lab, val, col) in enumerate(bars):
        bx = x0 + gap + i * (bw + gap)
        bh = h * 0.42 * val / 20
        draw.rectangle([bx, y1 - 16 - bh, bx + bw, y1 - 16], fill=col)
        f = F(SANS_B, 8)
        draw.text((bx + bw / 2 - draw.textlength(lab, font=f) / 2, y1 - 14),
                  lab, font=f, fill=INK)
    draw.rectangle([x0 + 8, y1 - 16, x1 - 8, y1 - 13], fill=(180, 180, 180))
    # Data label pinned clear of the red number badge (top-left, 17px):
    # its left edge starts 2px right of the badge instead of centring it,
    # so the "U" of "UP TO 20%" is never clipped by the badge.
    lab = "UP TO 20% \u00b7 16 PARTNERS"
    lf = fit_size(draw, lab, SANS_B, 15, 6.0, w - 42)
    ltw = draw.textlength(lab, font=lf)
    label_panel(draw, x0 + 20 + 10 + ltw / 2, y0 + 13, lab,
                w - 42, 15, (255, 255, 255), RED)


def scene_tower(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for i, col in enumerate(((245, 170, 90), (220, 120, 110), (120, 90, 140),
                             (70, 60, 110))):
        draw.rectangle([x0, y0 + h * i / 4, x1, y0 + h * (i + 1) / 4], fill=col)
    # tower silhouette
    tx = (x0 + x1) // 2
    draw.polygon([(tx - 16, y1 - 6), (tx - 7, y0 + 8), (tx + 7, y0 + 8),
                  (tx + 16, y1 - 6)], fill=(35, 30, 50))
    for wy in range(int(y0 + 16), int(y1 - 8), 9):
        draw.rectangle([tx - 3, wy, tx + 3, wy + 4], fill=(245, 214, 120))
    # neighbouring blocks
    draw.rectangle([x0 + 8, y1 - 26, x0 + 44, y1 - 6], fill=(50, 45, 70))
    draw.rectangle([x1 - 44, y1 - 20, x1 - 8, y1 - 6], fill=(50, 45, 70))
    # smoke
    for sx, sy, r in ((0.62, 0.18, 8), (0.68, 0.12, 6), (0.56, 0.14, 5)):
        draw.ellipse([x0 + w * sx - r, y0 + h * sy - r, x0 + w * sx + r,
                      y0 + h * sy + r], fill=(200, 200, 200))
    label_panel(draw, x0 + 34, y0 + 22, "11", 60, 26, (255, 255, 255), NAVY_D)


def scene_fire(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(245, 196, 106))
    draw.polygon([(x0, y1 - 20), (x0 + w * 0.3, y0 + h * 0.42),
                  (x0 + w * 0.6, y1 - 20)], fill=(90, 110, 60))
    draw.polygon([(x0 + w * 0.45, y1 - 20), (x0 + w * 0.75, y0 + h * 0.34),
                  (x1, y1 - 20)], fill=(70, 90, 50))
    draw.rectangle([x0, y1 - 20, x1, y1], fill=(60, 45, 30))
    for i in range(6):
        fx = x0 + 16 + i * (w - 32) / 5
        fh = 14 + (i % 3) * 5
        draw.polygon([(fx - 9, y1 - 18), (fx, y1 - 18 - fh), (fx + 9, y1 - 18)],
                     fill=(255, 110, 0) if i % 2 else (255, 170, 30))
    for sx, sy, r in ((0.25, 0.2, 8), (0.7, 0.16, 9), (0.78, 0.24, 6)):
        draw.ellipse([x0 + w * sx - r, y0 + h * sy - r, x0 + w * sx + r,
                      y0 + h * sy + r], fill=(130, 130, 130))
    label_panel(draw, (x0 + x1) // 2, y0 + 14, "3,000 ha", w - 40, 17,
                (255, 255, 255), (140, 20, 26))


def scene_ship(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y0 + h * 0.55], fill=(191, 217, 232))
    draw.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(46, 110, 158))
    draw.line([(x0, y0 + h * 0.55), (x1, y0 + h * 0.55)], fill=(255, 255, 255), width=1)
    # cargo ship
    draw.polygon([(x0 + 16, y0 + h * 0.62), (x1 - 16, y0 + h * 0.62),
                  (x1 - 30, y0 + h * 0.82), (x0 + 30, y0 + h * 0.82)],
                 fill=(30, 30, 40))
    for i, col in enumerate(((176, 30, 36), (201, 162, 39), (29, 78, 158),
                             (30, 122, 52))):
        draw.rectangle([x0 + 26 + i * 32, y0 + h * 0.42, x0 + 54 + i * 32,
                        y0 + h * 0.62], fill=col)
    draw.rectangle([x1 - 52, y0 + h * 0.34, x1 - 30, y0 + h * 0.62], fill=(240, 240, 240))
    # drone
    dx, dy = x0 + w * 0.68, y0 + 12
    draw.line([(dx - 7, dy), (dx + 7, dy)], fill=(40, 40, 40), width=2)
    draw.line([(dx, dy - 7), (dx, dy + 7)], fill=(40, 40, 40), width=2)
    draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(40, 40, 40))
    label_panel(draw, x0 + 52, y0 + h * 0.30, "DRONE HIT", 110, 13,
                (255, 255, 255), NAVY)


def scene_city(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(217, 226, 236))
    blocks = [(0.04, 0.42, 0.20, 0.62), (0.22, 0.30, 0.18, 0.74),
              (0.42, 0.36, 0.20, 0.68), (0.64, 0.26, 0.18, 0.78),
              (0.84, 0.40, 0.14, 0.64)]
    for bx, by, bw, bh in blocks:
        draw.rectangle([x0 + w * bx, y0 + h * by, x0 + w * (bx + bw),
                        y0 + h * (by + bh)], fill=(110, 118, 130))
        for wy in range(2, int(bh * h / 8), 8):
            draw.rectangle([x0 + w * bx + 4, y0 + h * by + wy,
                            x0 + w * bx + 9, y0 + h * by + wy + 4],
                           fill=(245, 214, 120))
    for sx, sy, r in ((0.5, 0.22, 9), (0.58, 0.14, 7), (0.42, 0.16, 6)):
        draw.ellipse([x0 + w * sx - r, y0 + h * sy - r, x0 + w * sx + r,
                      y0 + h * sy + r], fill=(120, 120, 120))
    label_panel(draw, x0 + 40, y0 + h * 0.62, "\u22654", 64, 22,
                (255, 255, 255), NAVY_D)


def scene_clinic(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(214, 232, 220))
    # clinic building
    draw.rectangle([x0 + 14, y0 + h * 0.34, x0 + w * 0.62, y1 - 8],
                   fill=(250, 250, 250))
    draw.polygon([(x0 + 8, y0 + h * 0.34), (x0 + w * 0.31, y0 + h * 0.14),
                  (x0 + w * 0.62 + 6, y0 + h * 0.34)], fill=(176, 30, 36))
    cx = x0 + w * 0.31
    draw.rectangle([cx - 10, y0 + h * 0.40, cx + 10, y0 + h * 0.52], fill=(176, 30, 36))
    draw.rectangle([cx - 4, y0 + h * 0.40, cx + 4, y0 + h * 0.52], fill=(255, 255, 255))
    draw.rectangle([cx - 10, y0 + h * 0.45, cx + 10, y0 + h * 0.47], fill=(255, 255, 255))
    draw.rectangle([cx - 8, y1 - 26, cx + 8, y1 - 8], fill=(60, 80, 110))
    # map inset: small Africa shape
    ix, iy = x1 - 52, y0 + 8
    draw.rectangle([ix, iy, ix + 44, iy + 34], fill=(255, 255, 255),
                   outline=(120, 120, 120))
    draw.polygon([(ix + 10, iy + 6), (ix + 30, iy + 6), (ix + 36, iy + 16),
                  (ix + 28, iy + 28), (ix + 16, iy + 26), (ix + 8, iy + 16)],
                 fill=(46, 140, 80))
    label_panel(draw, x0 + w * 0.52, y0 + h * 0.78, "5,678", 110, 17,
                (255, 255, 255), GREEN)


def scene_market(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(235, 238, 242))
    # storefront
    draw.rectangle([x0 + 10, y0 + h * 0.30, x1 - 10, y1 - 6], fill=(250, 250, 250))
    for i in range(6):
        col = RED if i % 2 == 0 else (255, 255, 255)
        draw.polygon([(x0 + 10 + i * (w - 20) / 6, y0 + h * 0.30),
                      (x0 + 10 + (i + 1) * (w - 20) / 6, y0 + h * 0.30),
                      (x0 + 10 + (i + 1) * (w - 20) / 6, y0 + h * 0.44),
                      (x0 + 10 + i * (w - 20) / 6, y0 + h * 0.44)], fill=col)
    draw.rectangle([x0 + 20, y0 + h * 0.50, x0 + w * 0.52, y0 + h * 0.78],
                   fill=(170, 205, 225))
    draw.rectangle([x0 + w * 0.60, y0 + h * 0.50, x1 - 20, y1 - 6],
                   fill=(90, 70, 50))
    # sign band
    f = F(SANS_B, 9)
    t = "SUPERMARKET"
    draw.text(((x0 + x1) / 2 - draw.textlength(t, font=f) / 2, y0 + h * 0.06),
              t, font=f, fill=RED)
    # police figures
    _person(draw, x0 + w * 0.72, y1 - 6, 0.9, (20, 40, 90))
    _person(draw, x0 + w * 0.86, y1 - 6, 0.9, (20, 40, 90))
    label_panel(draw, x0 + w * 0.36, y0 + h * 0.62, "DAY 2", 90, 16,
                (255, 255, 255), NAVY)


SCENES = {"court": scene_court, "rocket": scene_rocket,
          "memorial": scene_memorial, "chart": scene_chart,
          "port": scene_port, "treaty": scene_treaty,
          "tariffs": scene_tariffs, "tower": scene_tower,
          "fire": scene_fire, "ship": scene_ship, "city": scene_city,
          "clinic": scene_clinic, "market": scene_market}

# --------------------------------------------------------------- layout ---
W, H, M = 1024, 1024, 12
CW = W - 2 * M  # 1000


def one_line(draw, text, font, max_w):
    """Truncate with an ellipsis so the text fits max_w on one line."""
    if draw.textlength(text, font=font) <= max_w:
        return text
    words = text.split()
    while words:
        words.pop()
        trial = " ".join(words) + "\u2026"
        if draw.textlength(trial, font=font) <= max_w:
            return trial
    return "\u2026"


def number_tab(draw, x, y, num, size=20):
    f = F(SANS_B, 11 if size >= 20 else 9)
    draw.rectangle([x, y, x + size, y + size], fill=RED)
    t = str(num)
    tw = draw.textlength(t, font=f)
    draw.text((x + (size - tw) / 2, y + (size - f.size) / 2 - 1), t,
              font=f, fill=(255, 255, 255))


def draw_masthead(draw):
    f = fit_size(draw, "Wednesday 25 November 2026", SERIF_B, 34, 20, CW)
    t = "Wednesday 25 November 2026"
    draw.text(((W - draw.textlength(t, font=f)) / 2, 12), t, font=f, fill=NAVY)
    k = "THE WORLD IN ONE DAY \u00b7 39 STORIES \u00b7 7 REGIONS \u00b7 " \
        "EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026"
    kf = fit_size(draw, k, SANS_B, 13, 8, CW)
    draw.text(((W - draw.textlength(k, font=kf)) / 2, 50), k, font=kf, fill=RED)
    draw.rectangle([M, 68, W - M, 71], fill=RED)


def draw_stats(draw, y0=72, h=44):
    draw.rectangle([M, y0, W - M, y0 + h], fill=RED)
    cell = CW / 8
    for i, (num, cap) in enumerate(STATS):
        cx = M + cell * i
        nf = fit_size(draw, num, SANS_B, 17, 9, cell - 10)
        tw = draw.textlength(num, font=nf)
        draw.text((cx + (cell - tw) / 2, y0 + 5), num, font=nf,
                  fill=(255, 255, 255))
        cf = F(SANS_B, 8)
        lines = wrap(draw, cap, cf, cell - 8)
        ly = y0 + 26
        for ln in lines[:2]:
            lw = draw.textlength(ln, font=cf)
            draw.text((cx + (cell - lw) / 2, ly), ln, font=cf,
                      fill=(255, 220, 220))
            ly += 9


def draw_timeline(draw, y0=120, h=38):
    col = CW / 7
    mid = y0 + 22
    draw.line([(M + 8, mid), (W - M - 8, mid)], fill=NAVY, width=2)
    for i, (tm, lab) in enumerate(TIMELINE):
        cx = M + col * i + col / 2
        draw.ellipse([cx - 4, mid - 4, cx + 4, mid + 4], fill=RED,
                     outline=(255, 255, 255))
        tf = F(SANS_B, 10)
        tw = draw.textlength(tm, font=tf)
        draw.text((cx - tw / 2, y0), tm, font=tf, fill=NAVY)
        lf = F(SANS_B, 8)
        lines = wrap(draw, lab, lf, col - 8)
        ly = mid + 7
        for ln in lines[:2]:
            lw = draw.textlength(ln, font=lf)
            draw.text((cx - lw / 2, ly), ln, font=lf, fill=INK)
            ly += 9


def draw_hero(draw, x0, y0, w, h, hero):
    card_frame(draw, x0, y0, x0 + w, y0 + h)
    sh = 124
    SCENES[hero["scene"]](draw, (x0 + 1, y0 + 2, x0 + w - 1, y0 + 2 + sh))
    number_tab(draw, x0 + 1, y0 + 2, hero["num"], 22)
    tx = x0 + 9
    tw = w - 18
    y = y0 + sh + 8
    kf = fit_size(draw, hero["kicker"], SANS_B, 11, 7, tw)
    draw.text((tx, y), hero["kicker"], font=kf, fill=RED)
    y += 15
    y = text_block(draw, tx, y, tw, hero["headline"], SERIF_B, 17, INK, 3,
                   min_size=12.0, leading=19)
    y += 3
    y = text_block(draw, tx, y, tw, hero["deck"], SANS, 10.5, (50, 50, 50), 3,
                   min_size=8.5, leading=12)
    sy = y0 + h - 14
    chip(draw, x0 + w - 9, sy, hero["chip"], CHIP_FILL[hero["chip"]])
    sf = F(SANS, 8.5)
    src = one_line(draw, hero["source"], sf, tw - 72)
    draw.text((tx, sy + 2), src, font=sf, fill=MUTED)


def draw_secondary(draw, x0, y0, w, h, card):
    card_frame(draw, x0, y0, x0 + w, y0 + h)
    sh = 52
    SCENES[card["scene"]](draw, (x0 + 1, y0 + 2, x0 + w - 1, y0 + 2 + sh))
    number_tab(draw, x0 + 1, y0 + 2, card["num"], 17)
    tx = x0 + 7
    tw = w - 14
    y = y0 + sh + 4
    kf = fit_size(draw, card["kicker"], SANS_B, 8.5, 6.5, tw)
    draw.text((tx, y), card["kicker"], font=kf, fill=RED)
    y += 12
    y = text_block(draw, tx, y, tw, card["headline"], SERIF_B, 12.5, INK, 2,
                   min_size=9.0, leading=14)
    y += 1
    y = text_block(draw, tx, y, tw, card["deck"], SANS, 9.5, (50, 50, 50), 2,
                   min_size=8.0, leading=10.5)
    sy = y0 + h - 14
    chip(draw, x0 + w - 7, sy, card["chip"], CHIP_FILL[card["chip"]])
    sf = F(SANS, 8)
    src = one_line(draw, card["source"], sf, tw - 66)
    draw.text((tx, sy + 2), src, font=sf, fill=MUTED)


def draw_also(draw, y0=712, h=134):
    draw.rectangle([M, y0, W - M, y0 + 20], fill=NAVY)
    tf = F(SANS_B, 12)
    draw.text((M + 8, y0 + 3), "ALSO TODAY \u2014 26 MORE STORIES",
              font=tf, fill=(255, 255, 255))
    rf = F(SANS_B, 10)
    r = "14\u201339 \u00b7 NUMBERED \u00b7 PINNED ON THE MAP BELOW"
    draw.text((W - M - 8 - draw.textlength(r, font=rf), y0 + 4), r,
              font=rf, fill=GOLD_L)
    cols = [ALSO[0:9], ALSO[9:18], ALSO[18:26]]
    col_w = CW / 3
    nf = F(SANS_B, 9.5)
    tf2 = F(SANS_B, 9.5)
    hf = F(SANS, 9.5)
    y = y0 + 24
    for ci, items in enumerate(cols):
        cx = M + col_w * ci + 4
        for j, (num, tag, head) in enumerate(items):
            yy = y + j * 12.5
            draw.text((cx, yy), str(num), font=nf, fill=RED)
            x = cx + 20
            tw = draw.textlength(tag, font=tf2)
            draw.text((x, yy), tag, font=tf2, fill=CHIP_FILL.get(tag, NAVY))
            x += tw + 5
            draw.text((x, yy), one_line(draw, head, hf, M + col_w * (ci + 1) - 6 - x),
                      font=hf, fill=INK)


def draw_map(draw, x0, y0, x1, y1):
    card_frame(draw, x0, y0, x1, y1)
    tf = F(SANS_B, 11)
    draw.text((x0 + 8, y0 + 5),
              "WHERE IT HAPPENED \u00b7 PINS = STORY NUMBERS",
              font=tf, fill=NAVY)
    mx0, my0, mx1, my1 = x0 + 8, y0 + 24, x1 - 8, y1 - 20
    draw.rectangle([mx0, my0, mx1, my1], fill=(226, 236, 244))
    # Latitude is cropped to the inhabited band so the continents keep a
    # recognisable shape in this wide, short strip.
    lon0, lon1, lat0, lat1 = -170, 190, -45, 80

    def proj(lon, lat):
        px = mx0 + (lon - lon0) / (lon1 - lon0) * (mx1 - mx0)
        py = my1 - (lat - lat0) / (lat1 - lat0) * (my1 - my0)
        return (px, py)

    for lon in range(-150, 181, 30):
        px = mx0 + (lon - lon0) / (lon1 - lon0) * (mx1 - mx0)
        draw.line([(px, my0), (px, my1)], fill=(255, 255, 255), width=1)
    for lat in range(-30, 81, 30):
        py = my1 - (lat - lat0) / (lat1 - lat0) * (my1 - my0)
        draw.line([(mx0, py), (mx1, py)], fill=(255, 255, 255), width=1)
    for ring, col in zip(LAND, [(178, 205, 175), (206, 192, 158),
                                (168, 188, 208), (168, 188, 208),
                                (168, 188, 208), (192, 202, 138),
                                (163, 196, 163), (163, 196, 163),
                                (163, 196, 163), (150, 190, 170),
                                (216, 200, 168)]):
        draw.polygon([proj(lon, lat) for lon, lat in ring],
                     fill=col, outline=(110, 140, 110))
    # Pins: nudge crowded ones apart (with a leader line) so every number
    # stays readable, e.g. the Europe / Levant clusters.
    nf = F(SANS_B, 6.5)
    placed = []
    for num in sorted(PINS):
        lon, lat = PINS[num]
        px, py = proj(lon, lat)
        ox, oy = px, py
        for dx, dy in [(0, 0), (10, 0), (-10, 0), (0, -10), (0, 10),
                       (10, -8), (-10, -8), (10, 8), (-10, 8),
                       (18, 0), (-18, 0), (0, -18), (0, 18)]:
            cx, cy = px + dx, py + dy
            if all((cx - qx) ** 2 + (cy - qy) ** 2 >= 12 ** 2
                   for qx, qy in placed):
                ox, oy = cx, cy
                break
        placed.append((ox, oy))
        if (ox, oy) != (px, py):
            draw.line([(px, py), (ox, oy)], fill=RED, width=1)
            draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=RED)
        r = 5
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=RED,
                     outline=(255, 255, 255))
        t = str(num)
        tw = draw.textlength(t, font=nf)
        draw.text((ox - tw / 2, oy - 4), t, font=nf, fill=(255, 255, 255))
    lf = F(SANS, 8.5)
    lx = x0 + 8
    ly = y1 - 15
    for name, col in zip(LEGEND, [BLUE, PURPLE, TEAL, AMBER, GREEN,
                                  (200, 110, 30), GREY]):
        draw.ellipse([lx, ly + 1, lx + 7, ly + 8], fill=col)
        lx += 11
        tw = draw.textlength(name, font=lf)
        draw.text((lx, ly), name, font=lf, fill=INK)
        lx += tw + 12


def draw_datecheck(draw, x0, y0, x1, y1):
    card_frame(draw, x0, y0, x1, y1)
    tf = F(SANS_B, 11)
    draw.text((x0 + 8, y0 + 5), "DATE CHECK \u00b7 NOT WEDNESDAY",
              font=tf, fill=RED)
    inf = F(SANS, 10.5)
    intro = "Left out on purpose \u2014 these happened on other days:"
    draw.text((x0 + 8, y0 + 24), intro, font=inf, fill=INK)
    hline(draw, x0 + 8, x1 - 8, y0 + 42)
    y = y0 + 46
    bf = F(SANS_B, 10.5)
    df = F(SANS, 10.5)
    for name, date in DATE_CHECK:
        draw.text((x0 + 8, y), "\u00d7", font=bf, fill=RED)
        draw.text((x0 + 22, y), name, font=df, fill=INK)
        tw = draw.textlength(date, font=bf)
        draw.text((x1 - 8 - tw, y), date, font=bf, fill=RED)
        y += 12
    hline(draw, x0 + 8, x1 - 8, y + 1)
    cf = F(SANS, 9)
    closing = "Every story above is dated 25 Nov 2026."
    draw.text((x0 + 8, y + 5), closing, font=cf, fill=MUTED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_stats(draw)
    draw_timeline(draw)
    hw = (CW - 2 * 11) // 3
    hy = 260
    for i, hero in enumerate(HEROES):
        draw_hero(draw, M + i * (hw + 11), 162, hw, hy, hero)
    sw = (CW - 4 * 10) // 5
    sh = 136
    for r in range(2):
        for c in range(5):
            card = SECONDS[r * 5 + c]
            draw_secondary(draw, M + c * (sw + 10), 428 + r * (sh + 6),
                           sw, sh, card)
    draw_also(draw)
    draw_map(draw, M, 852, 652, 1000)
    draw_datecheck(draw, 664, 852, W - M, 1000)
    ff = F(SANS, 9)
    f1 = ("Sources: Xinhua, CMSA, Tas Fire Service, BEA, US Labor Dept, "
          "Reuters, UN, ABC, Al Jazeera, Mediazona, CNBC, BBC, Guardian, AP "
          "\u2014 checked vs reports dated 25 Nov 2026. 39 stories; 7 regions.")
    draw.text(((W - draw.textlength(f1, font=ff)) / 2, 1002), f1, font=ff,
              fill=MUTED)
    f2 = "Drawn by an AI agent for make.fun \u00b7 Wednesday 25 November 2026 \u00b7 One page, one day"
    draw.text(((W - draw.textlength(f2, font=ff)) / 2, 1013), f2, font=ff,
              fill=MUTED)
    return img


if __name__ == "__main__":
    out = os.path.join(HERE, "entry.png")
    build().save(out, format="PNG")
    print("wrote", out)
