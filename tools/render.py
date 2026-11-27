#!/usr/bin/env python3
"""Render the 27 November 2026 world-news broadsheet as a 1024x1024 PNG.

Fresh code written for the make.fun news-image-20261127 bounty
("Sum up 27 November's world news in one image").
Deterministic: fixed text, fixed fonts, no clock, no randomness, no network.
Usage: python3 tools/render.py [output.png]   (default: entry.png)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 245, 238)
INK = (26, 26, 26)
NAVY = (18, 58, 92)
RED = (176, 42, 30)
GREY = (96, 96, 96)
RULE = (178, 170, 156)
LIGHT = (232, 228, 218)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
MARGIN = 28
COL_W = 312
COL_X = [28, 356, 684]
GRID_TOP = 452
GRID_BOTTOM = 968


def load(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, max_w, fill, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y, len(lines)


# ---------------------------------------------------------------- stories
LEAD_KICKER = "GULF WAR WIDENS  •  OIL NEAR $97"
LEAD_HEAD = ["Gulf war widens: refinery hit,", "two Italians killed in Kuwait"]
LEAD_DECK = (
    "A Houthi projectile strikes Aramco's Jazan refinery, killing a Nepali worker; "
    "an Iranian drone attack in Kuwait kills two Italian technicians; two missiles "
    "aimed at Riyadh are intercepted \u2014 as Brent crude climbs toward $97 a barrel."
)
MARKET_LINE = "BRENT $97.41   +4.5% ON THE WEEK   \u2022   WTI $85.88   \u2022   FIRST WEEKLY GAIN IN A MONTH"

TIMELINE = [
    ("26 NOV", "Houthis claim a strike on Ras Tanura, the kingdom's biggest refinery."),
    ("26 NOV EVE", "Jazan refinery hit; one worker killed; coalition vows a response."),
    ("26 NOV ~MIDNIGHT", "Two ballistic missiles aimed at Riyadh are intercepted."),
    ("27 NOV", "Kuwait drone attack confirmed; EU summit ends with no budget deal."),
]

COLUMNS = [
    ("MIDDLE EAST", [
        ("JAZAN REFINERY HIT",
         "Houthi projectile hits Aramco's Jazan refinery; one worker killed, several hurt, output halted."),
        ("KUWAIT DRONE ATTACK",
         "Two Italian Rheinmetall technicians killed at an air-defence site; four hurt by falling debris."),
        ("RIYADH TARGETED AGAIN",
         "Two ballistic missiles aimed at Riyadh intercepted around midnight; launch platform destroyed."),
        ("50 TARGETS DESTROYED",
         "Coalition hits 50 Houthi military targets in Sanaa, Hodeidah and Saada, including arms depots."),
        ("RAS TANURA CLAIMED",
         "Houthis claim a strike on the kingdom's biggest refinery; coalition confirms four drones downed."),
        ("GAZA STRIKES KILL 10",
         "Israeli strikes kill 10 Palestinians, including senior Hamas official Khaled Abu Nada."),
    ]),
    ("AFRICA", [
        ("EBOLA PASSES 12,000",
         "Congo's Ebola outbreak reaches 12,021 cases and 5,904 deaths; fighting forces responders out."),
        ("NIGER GUNMEN KILL 30",
         "Gunmen kill 30 people and burn homes in Niger State, Nigeria."),
        ("HUNGER WARNING",
         "UN agencies warn hunger will worsen in 16 hotspots through May, with famine risk in Sudan."),
    ]),
    ("EUROPE", [
        ("155 DRONES AT UKRAINE",
         "Russia launches 155 drones overnight, 83 of them jet-powered Shaheds; 110 downed, one killed."),
        ("NATO JETS SCRAMBLED",
         "Estonia issues an air-threat warning and scrambles NATO jets over possible drone activity."),
        ("EU BUDGET: NO DEAL",
         "EU leaders fail to agree the 2028\u20132034 budget after 12+ hours; talks resume in December."),
        ("\u20ac45BN UKRAINE LOAN",
         "24 states back a \u20ac45bn loan for Ukraine in 2027, but no final decision until December."),
        ("NEW ECB CHIEF",
         "Spain's Pablo Hern\u00e1ndez de Cos elected European Central Bank president, succeeding Lagarde."),
        ("TRUMP SOFTENS NATO LINE",
         "Trump appears to soften the wording of a joint NATO statement and urges Putin to end the war."),
    ]),
    ("AMERICAS", [
        ("THANKSGIVING STORM",
         "A Thanksgiving storm cuts power to more than 800,000 customers on the US East Coast."),
        ("HUANG BACK AT NVIDIA",
         "Nvidia reinstates Jensen Huang as president and chief executive less than two weeks after he quit."),
        ("TRUMP CALLS GDP \u2018FAKE\u2019",
         "Trump calls election-year GDP figures \u2018fake\u2019 and seeks a Commerce Department review."),
    ]),
    ("ASIA\u2013PACIFIC", [
        ("INDONESIA MINE FLOOD",
         "Flooding at an illegal gold mine kills 13; 13 more feared trapped underground."),
        ("CHINA STOCKS SURGE",
         "Chinese stocks post their biggest daily rise in about two years after Beijing urges investment."),
        ("KARACHI COLLAPSE: 7 DEAD",
         "Death toll from the Baloch Colony building collapse rises to seven; 14 still missing."),
        ("CAIRO TANKER FIRE: 31 DEAD",
         "A fuel tanker overturns and catches fire on Cairo's Ring Road; 31 killed, 21 injured."),
        ("NZ DEADLOCK",
         "New Zealand's final count leaves parliament deadlocked: the coalition holds 65 of 130 seats."),
        ("DUTERTE TRIAL OPENS MONDAY",
         "The ICC trial of former Philippine president Rodrigo Duterte opens Monday in The Hague."),
    ]),
    ("SPORT & MARKETS", [
        ("ALCARAZ WINS ATP FINALS",
         "Carlos Alcaraz beats Alexander Zverev 6\u20132, 7\u20136(9\u20137) to win his first ATP Finals title."),
        ("BRENT NEAR $97",
         "Brent crude trades near $97 a barrel, up about 4.5% on the week; WTI around $86."),
        ("UK VETERANS CALLED",
         "Britain contacts 100,000 veterans over military readiness."),
    ]),
]

# Column order on the page: each page column holds two regions.
PAGE_COLUMNS = [
    [COLUMNS[0], COLUMNS[1]],
    [COLUMNS[2], COLUMNS[3]],
    [COLUMNS[4], COLUMNS[5]],
]


def draw_column(draw, x, blocks, scale):
    """Draw one page column (two region blocks). Returns the bottom y used."""
    title_f = load("DejaVuSans-Bold.ttf", round(14 * scale))
    body_f = load("DejaVuSans.ttf", round(12 * scale))
    head_f = load("DejaVuSans-Bold.ttf", round(15 * scale))
    title_lead = round(17 * scale)
    body_lead = round(15 * scale)
    y = GRID_TOP
    for header, items in blocks:
        draw.rectangle([x, y, x + COL_W, y + 26], fill=NAVY)
        draw.text((x + 8, y + 5), header, font=head_f, fill=(255, 255, 255))
        y += 26 + 8
        for title, body in items:
            y, _ = text_block(draw, x, y, title, title_f, COL_W, INK, title_lead, max_lines=1)
            y, _ = text_block(draw, x, y, body, body_f, COL_W, (60, 60, 60), body_lead, max_lines=3)
            y += round(8 * scale)
            if y > GRID_BOTTOM:
                raise ValueError("column overflow at %r (y=%d)" % (title, y))
        y += round(6 * scale)
    return y


def draw_board(scale):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Masthead
    draw.line([(MARGIN, 14), (W - MARGIN, 14)], fill=INK, width=2)
    title_f = load("DejaVuSerif-Bold.ttf", 56)
    draw.text((W // 2, 24), "THE WORLD TODAY", font=title_f, fill=INK, anchor="ma")
    date_f = load("DejaVuSans.ttf", 16)
    draw.text((W // 2, 94), "FRIDAY, 27 NOVEMBER 2026  \u2022  ONE IMAGE, THE WHOLE DAY",
              font=date_f, fill=GREY, anchor="ma")
    draw.line([(MARGIN, 116), (W - MARGIN, 116)], fill=INK, width=2)

    # Lead
    kick_f = load("DejaVuSans-Bold.ttf", 15)
    draw.text((MARGIN, 126), LEAD_KICKER, font=kick_f, fill=RED)
    head_f = load("DejaVuSerif-Bold.ttf", 36)
    y = 148
    for line in LEAD_HEAD:
        draw.text((MARGIN, y), line, font=head_f, fill=INK)
        y += 44
    deck_f = load("DejaVuSans.ttf", 16)
    y, _ = text_block(draw, MARGIN, y + 6, LEAD_DECK, deck_f, W - 2 * MARGIN,
                      (40, 40, 40), 21, max_lines=3)

    # Market strip
    draw.rectangle([MARGIN, 314, W - MARGIN, 344], fill=NAVY)
    mkt_f = load("DejaVuSans-Bold.ttf", 14)
    draw.text((W // 2, 322), MARKET_LINE, font=mkt_f, fill=(255, 255, 255), anchor="ma")

    # Timeline
    tl_label_f = load("DejaVuSans-Bold.ttf", 13)
    draw.text((MARGIN, 354), "THE DAY IN TIME", font=tl_label_f, fill=RED)
    box_w = 232
    gap = 12
    tl_date_f = load("DejaVuSans-Bold.ttf", 12)
    tl_body_f = load("DejaVuSans.ttf", 12)
    for i, (when, what) in enumerate(TIMELINE):
        bx = MARGIN + i * (box_w + gap)
        draw.rectangle([bx, 372, bx + box_w, 440], outline=RULE, width=1)
        draw.text((bx + 8, 378), when, font=tl_date_f, fill=NAVY)
        text_block(draw, bx + 8, 396, what, tl_body_f, box_w - 16,
                   (60, 60, 60), 14, max_lines=3)

    # Body columns
    for x, blocks in zip(COL_X, PAGE_COLUMNS):
        draw_column(draw, x, blocks, scale)

    # Footer
    draw.line([(MARGIN, 976), (W - MARGIN, 976)], fill=RULE, width=1)
    foot_f = load("DejaVuSans.ttf", 11)
    draw.text((MARGIN, 984),
              "Sources: Reuters, Associated Press, CNN, The Wall Street Journal, Morningstar, AFP \u2014 "
              "compiled 27 November 2026. Figures as reported; disputed attributions are labelled.",
              font=foot_f, fill=GREY)
    draw.text((MARGIN, 1000),
              "news-image-20261127  \u2022  make.fun  \u2022  Entry: povtalks-ai/makefun-news-image-20261127",
              font=foot_f, fill=GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    last_err = None
    for scale in (1.0, 0.93, 0.87):
        try:
            img = draw_board(scale)
        except ValueError as exc:
            last_err = exc
            continue
        img.save(out, format="PNG")
        print("rendered %s at scale %.2f (%dx%d)" % (out, scale, W, H))
        return 0
    print("render failed: column overflow even at smallest scale: %s" % last_err)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
