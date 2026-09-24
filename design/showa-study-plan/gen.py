# Generates the 純喫茶 溫習庫 study-plan canvas (fixed A4 artboards).
import json, re, html, math, os, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canvas')
PROJ = os.path.join(ROOT, 'project')
os.makedirs(PROJ, exist_ok=True)

W, H = 794, 1123
PADX = 52
CW = W - 2 * PADX  # 690

# ---------------------------------------------------------------- metrics
M = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metrics.json')))
def _in_jp_range(c):
    o = ord(c)
    return (0x20 <= o <= 0x7E) or (0xA0 <= o <= 0xFF) or (0x2010 <= o <= 0x2026) or (0x3041 <= o <= 0x30FF)
def cw(c, font):
    tbl = M[{'k': 'KaiseiDecol-Regular', 'kb': 'KaiseiDecol-Bold', 'd': 'DarumadropOne-Regular'}[font]]['w']
    if _in_jp_range(c) and c in tbl:
        return tbl[c]
    o = ord(c)
    if 0x2E80 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or 0x3000 <= o <= 0x303F or 0x2460 <= o <= 0x24FF:
        return 1.0
    return 0.6
TOK = re.compile(r'[A-Za-z0-9_./:+%\-–()\[\],;&=@#\'"!?*<>²₀χ]+|\s|.')
def lines(text, width, size, font='k'):
    n, cur = 1, 0.0
    for t in TOK.findall(text):
        tw = sum(cw(c, font) for c in t) * size
        if t.isspace():
            if cur > 0: cur += tw
            continue
        if cur + tw <= width:
            cur += tw
        elif tw > width:  # long token: break by chars
            for c in t:
                w1 = cw(c, font) * size
                if cur + w1 > width:
                    n += 1; cur = 0
                cur += w1
        else:
            n += 1; cur = tw
    return n
def th(text, width, size, lh, font='k'):
    return lines(text, width, size, font) * size * lh

EST = {}

# ---------------------------------------------------------------- tokens
INK = '#5B3B34'; INK2 = '#86605A'
BG = '#FFF7F3'; PAPER = '#FFFDFB'
LINE = '#EBCFD5'; LINE2 = '#E7C6CD'; OUT = '#D9AEB4'
CHERRY = '#F27289'; CHERRY_INK = '#B23A56'; CHERRY_W = '#FEE5EA'; STAMP = '#B8395A'
BERRY = '#FFA6BE'; BERRY_W = '#FFEDF2'; PINKSHADOW = '#FFC7D4'
MELON = '#7ED0A5'; MELON_INK = '#2B7650'; MELON_W = '#E0F6EA'; MELON_WW = '#F2FBF6'
VANILLA = '#FFE9B8'; VANILLA_W = '#FFF6E2'; CARAMEL = '#D9A15B'
SODA = '#9CCDEB'; GRAPE = '#C0AEE8'
BODY = "'Kaisei Decol', 'Chiron GoRound TC', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif"
DISP = "'Darumadrop One', 'Chiron GoRound TC', 'PingFang TC', 'Noto Sans TC', sans-serif"
TC = "'Chiron GoRound TC', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif"

SUBJ = {
    '1068': dict(w='#FEE5EA', b='#F27289', ink='#B23A56', kw='函數・極限・微積分'),
    '2306': dict(w='#E0F6EA', b='#7ED0A5', ink='#2B7650', kw='抽樣・概率・分佈'),
    '2311': dict(w='#FBEDD8', b='#D9A15B', ink='#8A5A1C', kw='置信區間・假設檢定・迴歸'),
    '2376': dict(w='#E6F3FB', b='#9CCDEB', ink='#2C6A94', kw='Python・pandas'),
    '2383': dict(w='#F0EBFC', b='#C0AEE8', ink='#6550A3', kw='網絡・AI・資料庫'),
}

def esc(s):
    return html.escape(s, quote=False)

def hl(s):
    """escape, then tint every SEHSxxxx mention in its subject colour"""
    s = esc(s)
    def rep(m):
        c = SUBJ[m.group(1)]
        return f'<span style="color: {c["ink"]}; font-weight: 700;">SEHS{m.group(1)}</span>'
    s = re.sub(r'SEHS(\d{4})', rep, s)
    return s.replace('H0', 'H<sub>0</sub>')

def fn(s):
    return esc(s).replace('_', '_<wbr>')

def st(**kw):
    return '; '.join(f'{k.replace("_", "-")}: {v}' for k, v in kw.items())

# ---------------------------------------------------------------- ornaments
def flower(size=22, petal=CHERRY, center=VANILLA):
    pts = []
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        pts.append((20 + 10.5 * math.cos(a), 20 + 10.5 * math.sin(a)))
    petals = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8"></circle>' for x, y in pts)
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 40 40" aria-hidden="true" style="flex-shrink: 0; display: block;">'
            f'<g fill="{petal}">{petals}</g>'
            f'<circle cx="20" cy="20" r="6.5" fill="{center}" stroke="{INK}" stroke-width="2"></circle></svg>')

def star_points(n=12, R=24, r=19, cx=25, cy=25):
    p = []
    for i in range(2 * n):
        a = math.radians(-90 + 180 / n * i)
        rr = R if i % 2 == 0 else r
        p.append(f'{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}')
    return ' '.join(p)
STAR = star_points()

def burst(text='注意', size=46, fill=STAMP, fs=13):
    return (f'<div style="{st(position="relative", width=f"{size}px", height=f"{size}px", flex_shrink="0", display="flex", align_items="center", justify_content="center")}">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 50 50" aria-hidden="true" style="position: absolute; left: 0; top: 0;">'
            f'<polygon points="{STAR}" fill="{fill}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"></polygon></svg>'
            f'<span style="{st(position="relative", font_family=TC, font_weight="900", font_size=f"{fs}px", line_height="1", color="#FFFFFF", letter_spacing="0.04em")}">{text}</span></div>')

def check_icon(color=MELON_INK, size=13):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 16 16" aria-hidden="true" style="flex-shrink: 0; display: inline-block; vertical-align: -1px;">'
            f'<path d="M3 8.5 L6.5 12 L13 4.5" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"></path></svg>')

def arrow_icon(color=OUT, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 20 20" aria-hidden="true" style="flex-shrink: 0; display: block;">'
            f'<path d="M4 10 H15 M10.5 5.5 L15 10 L10.5 14.5" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"></path></svg>')

def cream_soda(w=150):
    S = f'stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"'
    h = round(w * 116 / 100)
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 100 116" fill="none" aria-hidden="true" style="position: relative; display: block;">'
            f'<path d="M35 8 L45 48" stroke="{SODA}" stroke-width="6.5" stroke-linecap="round"></path>'
            f'<path d="M35 8 L45 48" stroke="{PAPER}" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="4 7"></path>'
            f'<path d="M35 8 L45 48" {S} stroke-width="2" opacity="0.45"></path>'
            f'<path d="M25 50 L31 99 Q32 106 39 106 L61 106 Q68 106 69 99 L75 50 Z" fill="{MELON_W}" {S}></path>'
            f'<path d="M26.2 60 L31 99 Q32 106 39 106 L61 106 Q68 106 69 99 L73.8 60 Z" fill="{MELON}" opacity="0.85"></path>'
            f'<circle cx="41" cy="74" r="3.6" fill="{PAPER}" opacity="0.75"></circle>'
            f'<circle cx="57" cy="83" r="2.8" fill="{PAPER}" opacity="0.7"></circle>'
            f'<circle cx="46" cy="93" r="2.2" fill="{PAPER}" opacity="0.6"></circle>'
            f'<path d="M35 60 L38 100" stroke="{PAPER}" stroke-width="3.5" stroke-linecap="round" opacity="0.55"></path>'
            f'<path d="M25 50 L31 99 Q32 106 39 106 L61 106 Q68 106 69 99 L75 50 Z" {S}></path>'
            f'<path d="M31 49 C25 35 35 22 50 22 C65 22 75 35 69 49 C60 54 40 54 31 49 Z" fill="#FFFBF4" {S}></path>'
            f'<path d="M39 40 c3 -5 8 -6 11 -3" stroke="{VANILLA}" stroke-width="3" stroke-linecap="round"></path>'
            f'<ellipse cx="50" cy="50" rx="25" ry="5.5" fill="{PAPER}" {S} opacity="0.95"></ellipse>'
            f'<path d="M64 17 C63 9 57 6 53 7" stroke="#3E9B6C" stroke-width="2.4" stroke-linecap="round"></path>'
            f'<circle cx="66" cy="22" r="7" fill="{CHERRY}" {S}></circle>'
            f'<circle cx="63.6" cy="19.6" r="1.9" fill="{PAPER}" opacity="0.85"></circle>'
            f'<ellipse cx="50" cy="108" rx="31" ry="6" fill="{PAPER}" {S}></ellipse>'
            f'</svg>')

def pudding(w=120):
    S = f'stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"'
    h = round(w * 116 / 100)
    def drip(x, ln):
        return f'<path d="M{x - 3.4:.1f} 54 v{ln} a3.4 3.4 0 0 0 6.8 0 v-{ln} z" fill="{CARAMEL}" {S}></path>'
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 100 116" fill="none" aria-hidden="true" style="display: block; flex-shrink: 0;">'
            f'<ellipse cx="50" cy="97" rx="39" ry="9" fill="{PAPER}" {S}></ellipse>'
            f'<ellipse cx="50" cy="95" rx="27" ry="5.5" fill="{BERRY_W}" stroke="{BERRY}" stroke-width="1.8"></ellipse>'
            f'<path d="M27 52 L73 52 L65 86 Q64 92 57 92 L43 92 Q36 92 35 86 Z" fill="{VANILLA}" {S}></path>'
            + drip(37, 14) + drip(50, 20) + drip(62, 11) +
            f'<ellipse cx="50" cy="52" rx="23.5" ry="7" fill="{CARAMEL}" {S}></ellipse>'
            f'<ellipse cx="43" cy="50" rx="6" ry="2.4" fill="{VANILLA_W}" opacity="0.5"></ellipse>'
            f'<path d="M50 44 C50 35 44 31 39 32" stroke="#3E9B6C" stroke-width="2.4" stroke-linecap="round"></path>'
            f'<circle cx="52" cy="46" r="7.5" fill="{CHERRY}" {S}></circle>'
            f'<circle cx="49.4" cy="43.4" r="2" fill="{PAPER}" opacity="0.9"></circle>'
            f'<path d="M78 74 c5 0 8 4 8 8 c0 5 -5 10 -8 10 c-3 0 -8 -5 -8 -10 c0 -4 3 -8 8 -8 z" fill="{CHERRY}" {S}></path>'
            f'<path d="M73 74 l5 -4 l5 4 z" fill="#3E9B6C" {S}></path>'
            f'<circle cx="76" cy="81" r="1.1" fill="{PAPER}"></circle>'
            f'<circle cx="81" cy="84" r="1.1" fill="{PAPER}"></circle>'
            f'<circle cx="77.5" cy="87" r="1.1" fill="{PAPER}"></circle>'
            f'</svg>')

def sunburst(size=250, rays=18, c1='#FFF3D2'):
    cx = cy = size / 2; R = size
    polys = []
    for i in range(rays):
        a0 = math.radians(360 / rays * i); a1 = math.radians(360 / rays * (i + 0.5))
        polys.append(f'<polygon points="{cx:.0f},{cy:.0f} {cx + R * math.cos(a0):.1f},{cy + R * math.sin(a0):.1f} {cx + R * math.cos(a1):.1f},{cy + R * math.sin(a1):.1f}"></polygon>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="position: absolute; left: 0; top: 0;">'
            f'<g fill="{c1}">{"".join(polys)}</g></svg>')

def awning(sw=26, sh=26):
    r = sw // 2
    stripes = f'repeating-linear-gradient(90deg, {CHERRY} 0px, {CHERRY} {sw}px, {PAPER} {sw}px, {PAPER} {2 * sw}px)'
    sc1 = f'radial-gradient(circle at {r}px 0px, {CHERRY} 0px, {CHERRY} {r - 2}px, {OUT} {r - 2}px, {OUT} {r}px, transparent {r + 0.5}px)'
    sc2 = f'radial-gradient(circle at {r}px 0px, {PAPER} 0px, {PAPER} {r - 2}px, {OUT} {r - 2}px, {OUT} {r}px, transparent {r + 0.5}px)'
    return (f'<div aria-hidden="true" style="{st(position="absolute", left="0px", top="0px", width=f"{W}px", height=f"{sh + r + 3}px")}">'
            f'<div style="{st(height=f"{sh}px", background=stripes, border_bottom=f"2px solid {OUT}")}"></div>'
            f'<div style="{st(height=f"{r + 1}px", background_image=f"{sc1}, {sc2}", background_size=f"{2 * sw}px {r + 1}px, {2 * sw}px {r + 1}px", background_position=f"0px 0px, {sw}px 0px", background_repeat="repeat-x")}"></div>'
            f'</div>')

# ---------------------------------------------------------------- small parts
def chip(code, big=16, small=12):
    c = SUBJ[code]
    return (f'<span style="{st(display="inline-flex", align_items="baseline", gap="3px", padding="1px 9px 2px", border_radius="99px", border=f"1.5px solid {c["b"]}", background=c["w"], color=c["ink"], white_space="nowrap", font_family=DISP, line_height="1.25")}">'
            f'<span style="font-size: {small}px; letter-spacing: 0.04em;">SEHS</span><span style="font-size: {big}px;">{code}</span></span>')

def mini_chip(code, size=15):
    c = SUBJ[code]
    return (f'<span style="{st(display="inline-block", padding="0px 8px 1px", border_radius="99px", border=f"1.5px solid {c["b"]}", background=c["w"], color=c["ink"], font_family=DISP, font_size=f"{size}px", line_height="1.3")}">{code}</span>')

def pending(text, size=12.5):
    return (f'<span style="{st(display="inline-block", padding="1px 8px", border=f"1.5px dashed #C9A0A8", border_radius="8px", color=INK2, font_size=f"{size}px", line_height="1.5")}">{esc(text)}</span>')

def pill(text, bg, bd, ink, size=13, font=TC, weight='700'):
    return (f'<span style="{st(display="inline-flex", align_items="center", padding="2px 11px", border_radius="99px", background=bg, border=f"1.5px solid {bd}", color=ink, font_family=font, font_weight=weight, font_size=f"{size}px", line_height="1.4", white_space="nowrap")}">{text}</span>')

def section_head(kana, title, lede=None, lede_w=CW, title_size=34, side=None, right=None):
    """side=(title_w): title and lede sit in one row, lede to the right."""
    h = 22 + 6 + title_size * 1.2
    kana_row = (f'<div style="{st(display="flex", align_items="center", gap="9px")}">{flower(22)}'
                f'<span style="{st(font_family=DISP, font_size="16px", letter_spacing="0.14em", color=CHERRY_INK, white_space="nowrap")}">{kana}</span>'
                f'<span style="{st(flex_grow="1", border_top=f"2px dotted {LINE2}")}"></span></div>')
    h2 = (f'<h2 style="{st(margin="0px", font_family=DISP, font_weight="900", font_size=f"{title_size}px", line_height="1.2", letter_spacing="0.02em", color=INK, text_shadow=f"2px 2px 0px {PINKSHADOW}", text_wrap="balance", flex_shrink="0")}">{title}</h2>')
    out = [f'<div style="{st(display="flex", flex_direction="column", gap="6px")}">', kana_row]
    if lede and side:
        lw = CW - side - 20
        out.append(f'<div style="{st(display="flex", align_items="flex-start", gap="20px")}">{h2}'
                   f'<p style="{st(margin="4px 0px 0px", flex_grow="1", min_width="0px", font_size="14.5px", line_height="1.65", color=INK, text_wrap="pretty")}">{hl(lede)}</p></div>')
        h = 22 + 6 + max(title_size * 1.2, 4 + th(lede, lw, 14.5, 1.65))
    else:
        if right:
            out.append(f'<div style="{st(display="flex", align_items="flex-end", justify_content="space-between", gap="16px")}">{h2}{right}</div>')
        else:
            out.append(h2)
        if lede:
            out.append(f'<p style="{st(margin="2px 0px 0px", font_size="15px", line_height="1.7", color=INK, text_wrap="pretty")}">{hl(lede)}</p>')
            h += 2 + 6 + th(lede, lede_w, 15, 1.7)
    out.append('</div>')
    return ''.join(out), h

def sub_head(title, kana=None):
    k = (f'<span style="{st(font_family=DISP, font_size="14px", letter_spacing="0.12em", color=CHERRY_INK)}">{kana}</span>' if kana else '')
    return (f'<div style="{st(display="flex", align_items="center", gap="9px")}">'
            f'<span style="{st(width="12px", height="12px", border_radius="50%", background=CHERRY, box_shadow=f"0px 0px 0px 3px {CHERRY_W}", flex_shrink="0")}"></span>'
            f'<h3 style="{st(margin="0px", font_family=DISP, font_weight="900", font_size="20px", line_height="1.3", color=INK)}">{title}</h3>{k}</div>'), 26

def card_style(radius=22, pad='16px 18px', bg=PAPER, shadow=3, bw=2):
    return st(background=bg, border=f"{bw}px solid {OUT}", border_radius=f"{radius}px", box_shadow=f"{shadow}px {shadow}px 0px {OUT}", padding=pad, box_sizing="border-box")

TOTAL_PAGES = 11

def footer(n):
    return (f'<div style="{st(position="absolute", left=f"{PADX}px", right=f"{PADX}px", bottom="22px", display="flex", align_items="center", gap="12px", font_size="12px", color=INK2)}">'
            f'<span style="{st(font_family=TC, font_weight="700", letter_spacing="0.2em", white_space="nowrap")}">純喫茶 溫習庫</span>'
            f'<span style="{st(flex_grow="1", border_top=f"2px dotted {LINE2}")}"></span>'
            f'<span style="white-space: nowrap;">2026/27 Sem 1 溫習計劃（更新版）</span>'
            f'<span style="{st(font_family=DISP, font_size="15px", line_height="1.3", color=INK, background=PAPER, border=f"2px solid {OUT}", border_radius="99px", padding="1px 12px", box_shadow=f"2px 2px 0px {OUT}", white_space="nowrap")}">{n:02d} / {TOTAL_PAGES:02d}</span>'
            f'</div>')

HELMET = """<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chiron+GoRound+TC:wght@400;500;700;900&amp;display=swap">
<style>
@font-face{font-family:'Darumadrop One';font-style:normal;font-weight:400;font-display:swap;src:url(/_blob/bd799787547967050115ccb445b85597) format('woff');unicode-range:U+0020-007E,U+00A0-00FF,U+2010-2026,U+3041-30FF;}
@font-face{font-family:'Kaisei Decol';font-style:normal;font-weight:400;font-display:swap;src:url(/_blob/29885a270ebf445293888cb3aa1b4779) format('woff');unicode-range:U+0020-007E,U+00A0-00FF,U+2010-2026,U+3041-30FF;}
@font-face{font-family:'Kaisei Decol';font-style:normal;font-weight:700;font-display:swap;src:url(/_blob/9e003a538acdf32ac7e57723b77a2c25) format('woff');unicode-range:U+0020-007E,U+00A0-00FF,U+2010-2026,U+3041-30FF;}
body{margin:0;background:#FFF7F3;font-synthesis:none;-webkit-font-smoothing:antialiased;}
h1,h2,h3,p,ul{margin:0}
table{border-collapse:separate;border-spacing:0}
a{color:#B23A56}a:hover{color:#8E2A42}
input.tick{appearance:none;-webkit-appearance:none;margin:0;flex-shrink:0;width:20px;height:20px;border:2px solid #D9AEB4;border-radius:6px;background:#FFFDFB;display:inline-grid;place-content:center;cursor:pointer}
input.stamp{appearance:none;-webkit-appearance:none;margin:0;flex-shrink:0;width:34px;height:34px;border:2px dashed #D9AEB4;border-radius:50%;background:#FFFDFB;display:inline-grid;place-content:center;cursor:pointer}
input.tick:checked,input.stamp:checked{background:#F27289;border:2px solid #B8395A}
input.tick:checked::after,input.stamp:checked::after{content:"";width:9px;height:5px;border-left:2.6px solid #FFFFFF;border-bottom:2.6px solid #FFFFFF;transform:translateY(-1px) rotate(-45deg)}
input.stamp:checked::after{width:12px;height:6px;border-left-width:3px;border-bottom-width:3px}
</style>
</helmet>"""

GINGHAM = st(background_color=BG,
             background_image="linear-gradient(rgba(242, 114, 137, 0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(242, 114, 137, 0.07) 1px, transparent 1px)",
             background_size="22px 22px")

def page(title, n, content, top=64, aw=(26, 26), lang='zh-Hant', gap=18):
    root = st(position="relative", width=f"{W}px", height=f"{H}px", overflow="hidden", box_sizing="border-box",
              font_family=BODY, color=INK) + '; ' + GINGHAM
    inner = st(position="absolute", left=f"{PADX}px", right=f"{PADX}px", top=f"{top}px", bottom="60px",
               display="flex", flex_direction="column", gap=f"{gap}px")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
{HELMET}
<div style="{root}">
{awning(*aw)}
<div style="{inner}">
{content}
</div>
{footer(n)}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
"""

PAGES = []  # (file, board title, html)
def add(file, btitle, html_src, est):
    PAGES.append((file, btitle, html_src))
    EST[file] = est

# ================================================================ P01 cover
def p01():
    toc = [
        ('本週重點及整體安排', 'こんしゅうのおすすめ', 2),
        ('評核總表', 'テストのおしながき', 3),
        ('本週每日時間表（9/23–9/27）', 'まいにちのよてい', 5),
        ('Week 4–7 每週計劃', 'しゅうかんメニュー', 6),
        ('Week 8–12 及考試前計劃', 'これからのよてい', 8),
        ('應試策略及操練清單', 'ひっしょうレシピ', 9),
        ('缺漏教材追蹤', 'おとりよせリスト', 11),
    ]
    sign = (f'<span style="{st(align_self="flex-start", display="inline-flex", align_items="center", gap="8px", background=INK, color=BG, border_radius="99px", padding="6px 18px 6px 12px", font_family=TC, font_weight="700", font_size="14px", letter_spacing="0.24em", line_height="1.4")}">'
            f'{flower(18, BERRY, VANILLA)}純喫茶 溫習庫</span>')
    left = (f'<div style="{st(flex_grow="1", min_width="0px", display="flex", flex_direction="column", gap="10px")}">'
            f'{sign}'
            f'<span style="{st(font_family=DISP, font_size="22px", letter_spacing="0.12em", color=CHERRY_INK, line_height="1.3")}">おべんきょう メニュー</span>'
            f'<h1 style="{st(margin="0px", font_family=TC, font_weight="900", font_size="88px", line_height="1.05", letter_spacing="0.04em", color=INK, text_shadow=f"4px 4px 0px {BERRY}")}">溫習計劃</h1>'
            f'<div style="{st(display="flex", align_items="center", gap="12px", flex_wrap="wrap")}">'
            f'<span style="{st(font_family=DISP, font_size="40px", line_height="1.1", color=CHERRY_INK)}">2026/27</span>'
            f'<span style="{st(font_family=DISP, font_size="40px", line_height="1.1", color=MELON_INK)}">Sem 1</span>'
            f'{pill("更新版", VANILLA, CARAMEL, INK, 16)}</div>'
            f'<span style="{st(font_family=DISP, font_size="16px", color=INK2, letter_spacing="0.06em")}">Sep 23, 2026</span>'
            f'</div>')
    medal = (f'<div style="{st(position="relative", width="250px", height="250px", flex_shrink="0", border_radius="50%", background=VANILLA, border=f"2.5px solid {OUT}", box_shadow=f"5px 5px 0px {OUT}", display="flex", align_items="center", justify_content="center", overflow="hidden")}">'
             f'{sunburst(250)}{cream_soda(148)}</div>')
    mast = f'<div style="{st(display="flex", align_items="center", gap="24px")}">{left}{medal}</div>'

    cards = []
    for code, c in SUBJ.items():
        cards.append(f'<div style="{st(background=c["w"], border=f"2px solid {c["b"]}", border_radius="16px", box_shadow=f"2px 2px 0px {c["b"]}", padding="10px 12px 12px", display="flex", flex_direction="column", gap="4px")}">'
                     f'<div style="{st(display="flex", align_items="baseline", gap="3px", font_family=DISP, color=c["ink"], line_height="1.1")}"><span style="font-size: 13px;">SEHS</span><span style="font-size: 28px;">{code}</span></div>'
                     f'<span style="{st(font_family=BODY, font_size="12.5px", line_height="1.45", color=INK, font_weight="700")}">{esc(c["kw"])}</span></div>')
    subj = (f'<div style="{st(display="flex", flex_direction="column", gap="10px")}">'
            f'<div style="{st(display="flex", align_items="center", gap="9px")}">{flower(20, MELON, VANILLA)}'
            f'<span style="{st(font_family=DISP, font_size="16px", letter_spacing="0.14em", color=CHERRY_INK)}">ラインナップ</span>'
            f'<span style="{st(font_family=TC, font_weight="900", font_size="16px", color=INK)}">本學期五科</span>'
            f'<span style="{st(flex_grow="1", border_top=f"2px dotted {LINE2}")}"></span></div>'
            f'<div style="{st(display="grid", grid_template_columns="repeat(5, minmax(0, 1fr))", gap="10px")}">{"".join(cards)}</div></div>')

    rows = []
    for i, (t, k, pg) in enumerate(toc):
        border = '' if i == len(toc) - 1 else f'; border-bottom: 2px dotted {LINE}'
        rows.append(f'<div style="{st(display="flex", align_items="center", gap="12px", padding="8px 0px")}{border}">'
                    f'<span style="{st(width="30px", height="30px", flex_shrink="0", border_radius="50%", background=CHERRY_W, border=f"2px solid {CHERRY}", color=CHERRY_INK, font_family=DISP, font_size="16px", line_height="26px", text_align="center", box_sizing="border-box")}">{i + 1}</span>'
                    f'<span style="{st(display="flex", flex_direction="column", gap="0px", min_width="0px")}">'
                    f'<span style="{st(font_family=DISP, font_weight="700", font_size="17px", line_height="1.35", color=INK)}">{esc(t)}</span>'
                    f'<span style="{st(font_family=DISP, font_size="12px", letter_spacing="0.12em", color=INK2, line_height="1.3")}">{k}</span></span>'
                    f'<span style="{st(flex_grow="1", border_bottom=f"2.5px dotted {OUT}", align_self="center", margin_top="8px")}"></span>'
                    f'<span style="{st(font_family=DISP, font_size="22px", color=CHERRY_INK, line_height="1")}">P.{pg:02d}</span></div>')
    toc_card = (f'<div style="{card_style(26, "18px 26px 12px", PAPER, 5, 2.5)}; position: relative;">'
                f'<div style="{st(display="flex", align_items="baseline", gap="12px", margin_bottom="4px")}">'
                f'<span style="{st(font_family=DISP, font_size="26px", color=CHERRY_INK, line_height="1.2")}">おしながき</span>'
                f'<span style="{st(font_family=TC, font_weight="900", font_size="18px", color=INK)}">目錄</span></div>'
                f'{"".join(rows)}</div>')
    content = mast + subj + toc_card
    est = 118 + 255 + 26 + (24 + 10 + 95) + 26 + (18 + 38 + 7 * 55 + 12)
    add('Main.dc.html', '01 封面 · おしながき', page('溫習計劃 封面', 1, content, top=118, aw=(34, 56), gap=26), est)

# ================================================================ P02 本週重點及整體安排
def p02():
    head, hh = section_head('こんしゅうのおすすめ', '本週重點及整體安排')
    tickets = [
        ('1', '交 SEHS1068 ICE1', None),
        ('2', '補回 Week 1–2 進度', '約 13 小時'),
        ('3', '完成 Week 3 本身的內容', None),
    ]
    tk = []
    for n, t, sub in tickets:
        subh = f'<span style="{st(font_family=DISP, font_size="15px", color=CHERRY_INK)}">{esc(sub)}</span>' if sub else ''
        tk.append(f'<div style="{st(background=BERRY_W, border=f"2px solid {OUT}", border_radius="16px", padding="12px 14px", display="flex", align_items="flex-start", gap="10px")}">'
                  f'<span style="{st(width="38px", height="38px", flex_shrink="0", border_radius="50%", background=PAPER, border=f"2px solid {CHERRY}", color=CHERRY_INK, font_family=DISP, font_size="22px", line_height="34px", text_align="center", box_sizing="border-box")}">{n}</span>'
                  f'<span style="{st(display="flex", flex_direction="column", gap="2px", padding_top="3px")}">'
                  f'<span style="{st(font_family=BODY, font_weight="700", font_size="16px", line_height="1.45", color=INK)}">{hl(t)}</span>{subh}</span></div>')
    ribbon = (f'<span style="{st(display="inline-block", background=STAMP, color="#FFFFFF", border=f"2px solid {INK}", border_radius="99px", padding="2px 14px", font_family=DISP, font_size="15px", letter_spacing="0.1em", box_shadow=f"2px 2px 0px {OUT}", line_height="1.4")}">ほんじつのおすすめ</span>')
    must = ('下週 SEHS2306 ICE1 考 Ch1 抽樣概念，所以 SEHS2306 Week 1 溫習包必須在週日前完成。')
    focus = (f'<div style="{card_style(26, "20px 22px", PAPER, 4, 2)}; display: flex; flex-direction: column; gap: 14px;">'
             f'<div style="{st(display="flex", align_items="center", gap="12px", flex_wrap="wrap")}">{ribbon}'
             f'<span style="{st(font_family=DISP, font_size="28px", line_height="1.1", color=INK)}">Week 3</span>'
             f'<span style="{st(font_family=DISP, font_size="18px", color=INK2)}">9/21–9/27</span>'
             f'</div>'
             f'<h3 style="{st(margin="0px", font_family=TC, font_weight="900", font_size="21px", line_height="1.35", color=INK)}">本週要同時做三件事</h3>'
             f'<div style="{st(display="grid", grid_template_columns="repeat(3, minmax(0, 1fr))", gap="12px")}">{"".join(tk)}</div>'
             f'<div style="{st(display="flex", align_items="center", gap="14px", background=VANILLA_W, border=f"2px dashed {CARAMEL}", border_radius="16px", padding="10px 16px 10px 10px")}">'
             f'{burst("週日前", 58, STAMP, 13)}'
             f'<p style="{st(margin="0px", font_size="15px", line_height="1.65", color=INK, font_weight="700")}">{hl(must)}</p></div>'
             f'</div>')
    focus_h = 20 + 32 + 14 + 28 + 14 + 96 + 14 + 70 + 20

    sh, shh = sub_head('整體安排', 'ぜんたいのながれ')
    para = '這份更新版取代舊計劃內「教材未上載」的安排：Week 1–7 每科都已有溫習包（PDF），每週計劃直接寫明讀哪一份、哪幾個 Part。舊版計劃保留不變，可作對照。'
    ph = th(para, CW, 15, 1.7)
    steps = [('Part A', '講義內容', CHERRY_W, CHERRY), ('Part B/C', '教材練習或歷屆試題詳解', VANILLA_W, CARAMEL),
             ('新練習題', '連答案', MELON_W, MELON), ('總結卡', '一頁', '#E6F3FB', SODA)]
    sp = []
    for i, (a, b, bg, bd) in enumerate(steps):
        if i: sp.append(arrow_icon())
        sp.append(f'<div style="{st(flex="1 1 0px", min_width="0px", background=bg, border=f"2px solid {bd}", border_radius="14px", padding="9px 10px", display="flex", flex_direction="column", gap="2px", text_align="center")}">'
                  f'<span style="{st(font_family=DISP, font_size="18px", line_height="1.2", color=INK)}">{esc(a)}</span>'
                  f'<span style="{st(font_size="13px", line_height="1.45", color=INK)}">{esc(b)}</span></div>')
    struct = (f'<div style="{card_style(20, "14px 16px", PAPER, 3, 2)}; display: flex; flex-direction: column; gap: 10px;">'
              f'<span style="{st(font_family=TC, font_weight="900", font_size="15px", color=INK)}">每份溫習包的結構</span>'
              f'<div style="{st(display="flex", align_items="center", gap="6px")}">{"".join(sp)}</div>'
              f'<span style="{st(font_size="13px", line_height="1.5", color=INK2)}">每份首頁「How to use this pack」已列出各部分時間。</span></div>')
    struct_h = 14 + 22 + 10 + 64 + 10 + 20 + 14
    info = [
        ('溫習包位置', f'<span style="{st(display="inline-block", font_size="13px", line_height="1.55", background=BERRY_W, border=f"1.5px solid {LINE2}", border_radius="8px", padding="3px 8px", color=INK, overflow_wrap="anywhere")}">Downloads/2026:27 Sem1/<wbr>Study Packs/<wbr>Week 01 至 Week 07</span>'
                       f'<span style="{st(font_size="13.5px", line_height="1.6", color=INK)}">每週有五科單科 PDF 及一份合併版。</span>'),
        ('每週平均時數', f'<span style="{st(display="flex", align_items="baseline", gap="6px", color=CHERRY_INK)}"><span style="{st(font_family=TC, font_size="14px", font_weight="700")}">約</span><span style="{st(font_family=DISP, font_size="40px", line_height="1")}">10–13</span><span style="{st(font_family=TC, font_size="14px", font_weight="700")}">小時</span></span>'
                         f'<span style="{st(font_size="13.5px", line_height="1.6", color=INK)}">本週因補進度約 20 小時。</span>'),
        ('Week 8 起', f'<span style="{st(font_size="13.5px", line_height="1.6", color=INK)}">溫習包未製作，教材上載後按週製作（見「Week 8–12」一節）。</span>'),
    ]
    ic = []
    for t, body in info:
        ic.append(f'<div style="{card_style(18, "12px 14px", PAPER, 2, 2)}; display: flex; flex-direction: column; gap: 8px;">'
                  f'<span style="{st(font_family=DISP, font_weight="900", font_size="15px", color=INK, border_bottom=f"2px dotted {LINE}", padding_bottom="6px")}">{esc(t)}</span>{body}</div>')
    info_row = f'<div style="{st(display="grid", grid_template_columns="repeat(3, minmax(0, 1fr))", gap="12px")}">{"".join(ic)}</div>'
    info_h = 12 + 28 + 8 + 70 + 12
    para_html = f'<p style="{st(margin="0px", font_size="15px", line_height="1.7", color=INK, text_wrap="pretty")}">{hl(para)}</p>'
    content = head + focus + sh + para_html + struct + info_row
    est = 64 + hh + 18 + focus_h + 18 + shh + 18 + ph + 18 + struct_h + 18 + info_h
    add('P02-Focus.dc.html', '02 本週重點及整體安排', page('本週重點及整體安排', 2, content), est)

# ================================================================ P03/P04 評核總表
A_ROWS = [
    # week, date, code, name, weight_html, weight_plain, scope, pack, pending
    ('W3', '9/21–9/27', '1068', 'ICE1', 'w:10%', '24 小時 take-home，tutorial 後開始', 'Week 3（線性代數）；Week 1–2 概率如在範圍內', False),
    ('W4', '9/28–10/4', '2306', 'ICE1', 'w:10%', 'Sample survey 及數據整理', 'Week 1–3（Ch1–3）', False),
    ('W4–W13', '', '2306', 'Online Assignment ①–⑥', 'p:合共|10%', 'Sessions 4, 5, 7, 9, 11, 13', '當週溫習包', False),
    ('W5', '10/5–10/11', '1068', 'ICE2', 'w:10%', '24 小時 take-home', 'Week 4–5（定義域、函數、三角）', False),
    ('W5', '10/5–10/11', '2311', 'In-class Assignment 1', 'w:10%', '估計及假設檢定基礎', 'Week 1, 3–5', False),
    ('W5', '10/5–10/11', '2376', 'ICE1（Tutorial 5）', 'p:三次 ICE 合共|30%', 'Open book，寫完整程式', 'Week 1–5', False),
    ('W6', '10/12–10/18', '2376', 'Take-home Assignment 1', 'w:20%', 'Python 應用程式', 'Week 3–6', False),
    ('W7', '10/19–10/25', '1068', 'Quiz 1', 'w:15%', 'Closed book 45 分鐘，只可用 HKEAA 認可計數機', 'Week 7 極限（實際範圍要留意 e-Learning）', False),
    ('W7', '10/19–10/25', '2306', 'Individual Assignment 1', 'w:10%', '圖表 + 詮釋 + 概率計算（Ch2–7）', 'Week 2–7；Week 7 Part B 評分清單', False),
    ('W8', '10/26–11/1', '2311', 'Mid-term Test', 'w:20%', '估計及假設檢定（Lecture 3–7）', 'Week 3–7', False),
    ('W8', '10/26–11/1', '2376', 'ICE2（Tutorial 8）', 't:見上', 'pandas DataFrame', 'Week 6–7', False),
    ('W9', '11/2–11/8', '1068', 'ICE3', 't:—', '24 小時 take-home', '待製作（Week 8–9）', True),
    ('W10', '11/9–11/15', '2376', 'Take-home Assignment 2', 'w:20%', '髒資料、日期時間、摘要', '待製作（Week 8–10）', True),
    ('W11', '11/16–11/22', '1068', 'Individual Assignment（手寫，課堂上交）', 'w:30%', '不可大量抄用 AI 內容', '各週方法框及相似例題', False),
    ('W11', '11/16–11/22', '1068', 'ICE4', 't:—', '24 小時 take-home', '待製作', True),
    ('W11', '11/16–11/22', '2376', 'ICE3（Tutorial 11）', 't:見上', '表格及視覺化', '待製作', True),
    ('W12', '11/23–11/29', '1068', 'Quiz 2', 'w:15%', 'Closed book 45 分鐘', '待製作（積分）', True),
    ('W12', '11/23–11/29', '2306', 'ICE2', 'w:10%', '隨機變數', 'Week 6–7', False),
    ('W12', '11/23–11/29', '2311', 'In-class Assignment 2', 'w:10%', '簡單線性迴歸', '待製作', True),
    ('W14', '', '2376', 'Test', 'w:30%', 'Closed book，Week 1–13', 'Week 1–7 及後續溫習包', False),
    ('未公布', '', '2383', 'Group Project、Individual Assignment 1–2、In-class Exercises', 'l:16%、8%、8%、8%', 'Assignment 2 為資料庫實作', 'Week 1–7；資料庫見 Week 7', False),
]
ACOLS = [('週次', 90), ('科目', 102), ('評核', 124), ('比重', 72), ('範圍／形式', 152), ('準備用溫習包', 146)]  # sum 686
TD = st(padding="8px 9px", vertical_align="top", font_size="13px", line_height="1.5", color=INK)

def weight_html(w):
    kind, val = w.split(':', 1)
    if kind == 'w':
        return f'<span style="{st(font_family=DISP, font_size="19px", line_height="1.2", color=CHERRY_INK)}">{esc(val)}</span>', 25
    if kind == 'p':
        a, b = val.split('|')
        return (f'<span style="{st(display="flex", flex_direction="column", gap="0px")}"><span style="{st(font_family=TC, font_weight="700", font_size="12px", line_height="1.45", color=INK2)}">{esc(a)}</span>'
                f'<span style="{st(font_family=DISP, font_size="19px", line_height="1.2", color=CHERRY_INK)}">{esc(b)}</span></span>'), th(a, ACOLS[3][1] - 18, 12, 1.45) + 25
    if kind == 'l':
        return f'<span style="{st(font_family=DISP, font_size="16px", line_height="1.4", color=CHERRY_INK)}">{esc(val)}</span>', 4 * 22.4
    return f'<span style="{st(font_family=TC, font_size="13px", color=INK2)}">{esc(val)}</span>', 20

def a_table(rows, final=False):
    # group consecutive rows by week label
    groups = []
    for r in rows:
        if groups and groups[-1][0][0] == r[0]:
            groups[-1].append(r)
        else:
            groups.append([r])
    colg = ''.join(f'<col style="width: {w}px;">' for _, w in ACOLS)
    head = ''.join(f'<th scope="col" style="{st(padding="9px 9px", text_align="left", font_family=TC, font_weight="700", font_size="13px", color=INK, background=CHERRY_W, border_bottom=f"2px solid {OUT}", white_space="nowrap")}">{t}</th>' for t, _ in ACOLS)
    body = []
    est = 40
    inner = [w - 18 for _, w in ACOLS]
    for gi, g in enumerate(groups):
        last_group = (gi == len(groups) - 1) and not final
        for ri, r in enumerate(g):
            wk, date, code, name, w, scope, pack, pend = r
            last_in_group = ri == len(g) - 1
            if last_in_group and last_group:
                bb = 'none'
            elif last_in_group:
                bb = f'2px solid {LINE2}'
            else:
                bb = f'2px dotted {LINE}'
            cells = []
            if ri == 0:
                if wk == '未公布':
                    wkh = f'<span style="{st(font_family=TC, font_weight="900", font_size="15px", color=INK)}">未公布</span>'
                else:
                    fs = '15px' if len(wk) > 4 else '22px'
                    wkh = f'<span style="{st(display="block", font_family=DISP, font_size=fs, line_height="1.15", color=INK)}">{esc(wk)}</span>'
                    if date:
                        wkh += f'<span style="{st(display="block", font_family=DISP, font_size="12px", line_height="1.3", color=INK2, margin_top="2px", white_space="nowrap")}">{esc(date)}</span>'
                gb = 'none' if last_group else f'2px solid {LINE2}'
                cells.append(f'<td rowspan="{len(g)}" style="{TD}; background: {BERRY_W}; border-bottom: {gb}; border-right: 2px solid {LINE2};">{wkh}</td>')
            wh, wheight = weight_html(w)
            packh = pending(pack) if pend else esc(pack)
            cells.append(f'<td style="{TD}; border-bottom: {bb};">{chip(code, 15, 12)}</td>')
            cells.append(f'<td style="{TD}; border-bottom: {bb}; font-weight: 700;">{esc(name)}</td>')
            cells.append(f'<td style="{TD}; border-bottom: {bb};">{wh}</td>')
            cells.append(f'<td style="{TD}; border-bottom: {bb};">{esc(scope)}</td>')
            cells.append(f'<td style="{TD}; border-bottom: {bb};">{packh}</td>')
            body.append('<tr>' + ''.join(cells) + '</tr>')
            hs = [th(name, inner[2], 13, 1.5, 'kb'), wheight, th(scope, inner[4], 13, 1.5), th(pack, inner[5] - (18 if pend else 0), 13 if not pend else 12.5, 1.5) + (4 if pend else 0), 22]
            est += max(hs) + 16 + 2
    if final:
        fin = (f'<tr><td colspan="6" style="{st(padding="12px 14px", background=VANILLA_W)}">'
               f'<div style="{st(display="flex", align_items="center", gap="16px")}">'
               f'{burst("期末", 54, STAMP, 14)}'
               f'<span style="{st(display="flex", flex_direction="column", gap="2px")}">'
               f'<span style="{st(font_family=DISP, font_size="22px", line_height="1.15", color=INK)}">Final Exam</span>'
               f'<span style="{st(font_family=DISP, font_size="14px", color=INK2)}">12/12–12/31</span></span>'
               f'<span style="{st(display="flex", gap="5px", flex_wrap="wrap", align_items="center")}">{mini_chip("1068")}{mini_chip("2306")}{mini_chip("2311")}{mini_chip("2383")}</span>'
               f'<span style="flex-grow: 1;"></span>'
               f'<span style="{st(display="flex", flex_direction="column", align_items="flex-end", gap="1px")}">'
               f'<span style="{st(font_family=DISP, font_size="24px", line_height="1.1", color=CHERRY_INK)}">各 60%</span>'
               f'<span style="{st(font_size="12.5px", color=INK, line_height="1.45")}">確切日期待定・全部溫習包</span></span>'
               f'</div></td></tr>')
        body.append(fin)
        est += 80
    tbl = (f'<div style="{st(background=PAPER, border=f"2px solid {OUT}", border_radius="20px", box_shadow=f"3px 3px 0px {OUT}", overflow="hidden")}">'
           f'<table style="{st(width="100%", table_layout="fixed")}"><colgroup>{colg}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')
    return tbl, est

def p03():
    head, hh = section_head('テストのおしながき', '評核總表',
                            '下表按週次列出五科所有評核（百分比為該項佔該科總成績比重），最後一欄是準備時要用的溫習包。「週次」指教學週；Week 1 = 9/7–9/13。')
    tbl, te = a_table(A_ROWS[:11])
    content = head + tbl
    add('P03-Assessments-1.dc.html', '03 評核總表 ①', page('評核總表（一）', 3, content), 64 + hh + 18 + te)

def p04():
    head, hh = section_head('テストのおしながき・つづき', '評核總表（續）')
    tbl, te = a_table(A_ROWS[11:], final=True)
    notes = ['SEHS2376 沒有獨立期末考，100% 由持續評核組成。',
             'SEHS2306 及 SEHS2383 的評核指引列明，持續評核及考試兩邊都要取得 D 或以上才合格。']
    lis = ''.join(f'<li style="{st(display="flex", gap="8px", align_items="flex-start", font_size="14px", line_height="1.65", color=INK)}">'
                  f'<span style="{st(width="8px", height="8px", border_radius="50%", background=CARAMEL, flex_shrink="0", margin_top="8px")}"></span><span>{hl(n)}</span></li>' for n in notes)
    note = (f'<div style="{st(display="flex", gap="14px", align_items="flex-start", background=VANILLA_W, border=f"2px solid {CARAMEL}", border_radius="18px", padding="12px 16px", box_shadow=f"2px 2px 0px {CARAMEL}")}">'
            f'<span style="{st(font_family=DISP, font_size="15px", letter_spacing="0.1em", color="#8A5A1C", white_space="nowrap", padding_top="1px")}">おしらせ</span>'
            f'<ul style="{st(list_style="none", padding="0px", display="flex", flex_direction="column", gap="4px")}">{lis}</ul></div>')
    nh = 24 + sum(th(n, CW - 32 - 90, 14, 1.65) for n in notes) + 4
    content = head + tbl + note
    add('P04-Assessments-2.dc.html', '04 評核總表 ②', page('評核總表（二）', 4, content), 64 + hh + 18 + te + 18 + nh)

# ================================================================ P05 本週每日時間表
def p05():
    head, hh = section_head('まいにちのよてい', '本週每日時間表（9/23–9/27）',
                            '週一、二已過，餘下五日共約 20 小時。排序原則：先完成有截止時間的 ICE1，再補作為後續課題基礎的 SEHS2311 及 SEHS2376，週日前完成下週 ICE1 需要的 SEHS2306 Ch1。')
    days = [
        ('週三', '9/23', 'Tutorial 後即做 SEHS1068 ICE1（24 小時內交）；第一步先溫 Week 3 線性代數總結卡', 'Week 03 SEHS1068；如 ICE1 含概率，加 Week 01 SEHS1068 Part A6–A8', '3–4'),
        ('週四', '9/24', '交 ICE1；補 SEHS2311 Lecture 01（概率分佈、z 表）；補 SEHS2376 Lecture 1', 'Week 01 SEHS2311 Part A–B；Week 01 SEHS2376 Part A–B', '4'),
        ('週五', '9/25', '補 SEHS2376 Lecture 2；補 SEHS1068 Week 1–2 概率；補 SEHS2306 Ch1', 'Week 02 SEHS2376；Week 01–02 SEHS1068 Part A–C；Week 01 SEHS2306', '5'),
        ('週六', '9/26', '補 SEHS2306 Ch2 及 SEHS2311 Lecture 02；再完成本週 SEHS2306 Ch3 及 SEHS2311 Lecture 03', 'Week 02 SEHS2306、SEHS2311；Week 03 SEHS2306、SEHS2311', '5'),
        ('週日', '9/27', '補 SEHS2383 Module 1 及 C++ Lab 1–2；完成 Week 3 SEHS2376 及 SEHS2383；用 SEHS2306 Week 1 Part C 自測一次，作為 ICE1 熱身', 'Week 01–02 SEHS2383；Week 03 SEHS2376、SEHS2383', '3–4'),
    ]
    STUB, PACKW, HRW = 86, 212, 74
    planw = CW - 4 - STUB - PACKW - HRW - 28
    cols = f'<div style="{st(display="flex", align_items="center", gap="0px", font_family=TC, font_weight="700", font_size="12.5px", color=INK2, padding="0px 4px")}">' \
           f'<span style="width: {STUB}px; text-align: center;">日子</span><span style="flex-grow: 1; padding-left: 14px;">安排</span>' \
           f'<span style="width: {PACKW}px; padding-left: 14px;">溫習包及部分</span><span style="width: {HRW}px; text-align: center;">時數</span></div>'
    rows = []
    est_rows = 0
    for d, dt, plan, pack, hr in days:
        rows.append(f'<div style="{st(display="flex", background=PAPER, border=f"2px solid {OUT}", border_radius="18px", box_shadow=f"3px 3px 0px {OUT}", overflow="hidden")}">'
                    f'<div style="{st(width=f"{STUB}px", flex_shrink="0", background=VANILLA_W, border_right=f"2.5px dashed {OUT}", display="flex", flex_direction="column", align_items="center", justify_content="center", gap="0px", padding="10px 4px", box_sizing="border-box")}">'
                    f'<span style="{st(font_family=TC, font_weight="900", font_size="17px", line_height="1.3", color=INK)}">{d}</span>'
                    f'<span style="{st(font_family=DISP, font_size="24px", line_height="1.1", color=CHERRY_INK)}">{dt}</span></div>'
                    f'<p style="{st(margin="0px", flex_grow="1", min_width="0px", padding="10px 14px", font_size="14px", line_height="1.6", color=INK)}">{hl(plan)}</p>'
                    f'<p style="{st(margin="0px", width=f"{PACKW}px", flex_shrink="0", box_sizing="border-box", padding="10px 14px", background="#FFF9F7", border_left=f"2px dotted {LINE}", font_size="12.5px", line_height="1.55", color=INK)}">{esc(pack)}</p>'
                    f'<div style="{st(width=f"{HRW}px", flex_shrink="0", display="flex", flex_direction="column", align_items="center", justify_content="center", border_left=f"2px dotted {LINE}")}">'
                    f'<span style="{st(font_family=DISP, font_size="24px", line_height="1.1", color=CHERRY_INK)}">{hr}</span>'
                    f'<span style="{st(font_family=DISP, font_size="13px", color=INK2)}">hr</span></div></div>')
        est_rows += max(th(plan, planw, 14, 1.6), th(pack, PACKW - 28, 12.5, 1.55), 60) + 20 + 4
    days_html = f'<div style="{st(display="flex", flex_direction="column", gap="10px")}">{cols}{"".join(rows)}</div>'
    est_rows += 18 + 10 * 5

    stamps = ['SEHS1068 ICE1 已交', 'Week 1 五科完成', 'Week 2 五科完成', 'Week 3 五科完成']
    sitems = ''.join(f'<label style="{st(display="flex", align_items="center", gap="10px", font_size="14px", line_height="1.45", color=INK, font_weight="700", cursor="pointer")}">'
                     f'<input type="checkbox" class="stamp"><span>{hl(s)}</span></label>' for s in stamps)
    stamp_card = (f'<div style="{card_style(22, "14px 18px 16px", PAPER, 3, 2)}; flex: 1 1 0px; min-width: 0px; display: flex; flex-direction: column; gap: 10px;">'
                  f'<div style="{st(display="flex", align_items="baseline", gap="10px")}">'
                  f'<span style="{st(font_family=DISP, font_size="20px", color=CHERRY_INK)}">スタンプカード</span>'
                  f'<span style="{st(font_size="12.5px", color=INK2)}">完成後打剔</span></div>'
                  f'<div style="{st(display="grid", grid_template_columns="repeat(2, minmax(0, 1fr))", gap="10px 12px")}">{sitems}</div></div>')
    def grp(label, bg, bd, ink, items):
        lis = ''.join(f'<li style="{st(display="flex", gap="8px", align_items="flex-start", font_size="13.5px", line_height="1.55", color=INK)}">'
                      f'<span style="{st(width="7px", height="7px", border_radius="50%", background=bd, flex_shrink="0", margin_top="8px")}"></span><span>{hl(i)}</span></li>' for i in items)
        return (f'<div style="{st(display="flex", flex_direction="column", gap="4px")}">{pill(label, bg, bd, ink, 12.5)}'
                f'<ul style="{st(list_style="none", padding="0px", display="flex", flex_direction="column", gap="2px")}">{lis}</ul></div>')
    short_card = (f'<div style="{card_style(22, "14px 18px 16px", PAPER, 3, 2)}; flex: 1 1 0px; min-width: 0px; display: flex; flex-direction: column; gap: 8px;">'
                  f'<h3 style="{st(margin="0px", font_family=TC, font_weight="900", font_size="16px", color=INK)}">如果時間不足</h3>'
                  f'{grp("可延後", MELON_W, MELON, MELON_INK, ["SEHS2383 Module 1（概論性質，可移到下週）", "各溫習包的新練習題部分"])}'
                  f'{grp("不可延後", CHERRY_W, CHERRY, CHERRY_INK, ["SEHS2311 Lecture 01（z 表）", "SEHS2306 Ch1"])}</div>')
    bottom = f'<div style="{st(display="flex", gap="14px", align_items="stretch")}">{stamp_card}{short_card}</div>'
    bh = max(14 + 28 + 10 + 2 * 40 + 10 + 16, 14 + 22 + 8 + 2 * (26 + 4 + th("SEHS2383 Module 1（概論性質，可移到下週）", 290, 13.5, 1.55) + 22) + 8 + 16)
    content = head + days_html + bottom
    add('P05-This-Week.dc.html', '05 本週每日時間表', page('本週每日時間表', 5, content), 64 + hh + 18 + est_rows + 18 + bh)

# ================================================================ P06/P07 Week 4–7
WEEKS = [
    dict(n='4', date='9/28–10/4', alert='SEHS2306 ICE1（10%）；Online Assignment ① 開始計分。', total='12.5',
         rows=[('1068', '定義域、值域、有理函數、部分分數', 'Week04_SEHS1068_Functions_Domain_Range', '3'),
               ('2306', '計數法則 + ICE1 準備（Ch1–3）', 'Week04_SEHS2306_Ch4_Counting_Rules_ICE1', '3'),
               ('2311', '大樣本 CI、比例 CI、t CI', 'Week04_SEHS2311_Confidence_Intervals_I', '2.5'),
               ('2376', 'list、tuple、dict、set', 'Week04_SEHS2376_Lists_Dictionaries', '2.5'),
               ('2383', '網絡類型、OSI/TCP-IP、網絡設備', 'Week04_SEHS2383_Networks_Data_Communications', '1.5')],
         tip='週一、二 SEHS2306 ICE1 準備（Week 1–3 總結卡 + Week 4 溫習包的 ICE1 部分）；週三至五 SEHS1068、SEHS2311；週末 SEHS2376、SEHS2383。'),
    dict(n='5', date='10/5–10/11', alert='三個評核同週：SEHS1068 ICE2（10%）、SEHS2311 In-class Assignment 1（10%）、SEHS2376 ICE1（Tutorial 5）；另有 SEHS2306 Online Assignment ②。', total='13.5',
         rows=[('1068', '三角函數、奇偶函數、圖像變換；ICE2', 'Week05_SEHS1068_Trig_EvenOdd_Transformations', '3.5'),
               ('2306', '條件概率、貝葉斯定理', 'Week05_SEHS2306_Ch5_Probability_Theory', '2.5'),
               ('2311', '兩樣本 CI、方差 CI；Assignment 1', 'Week05_SEHS2311_Confidence_Intervals_II_Assignment1', '3'),
               ('2376', '完整程式寫法 + ICE1 模擬題', 'Week05_SEHS2376_Applications_II_InClassEx1', '3'),
               ('2383', 'AI、機器學習、AI 倫理', 'Week05_SEHS2383_AI_Concepts_Ethics', '1.5')],
         tip='週一、二先做 SEHS2311 及 SEHS2376 的模擬題；SEHS1068 ICE2 在 tutorial 後 24 小時內完成；週末 SEHS2306、SEHS2383。'),
    dict(n='6', date='10/12–10/18', alert='SEHS2376 Take-home Assignment 1（20%）交。', total='13.5',
         rows=[('1068', '合成函數、反函數、指數對數（考試 A3）', 'Week06_SEHS1068_Composite_Inverse_ExpLog', '3'),
               ('2306', '隨機變數、期望值、方差', 'Week06_SEHS2306_Ch6_Random_Variables', '2.5'),
               ('2311', '假設檢定、P 值、z/t 檢定', 'Week06_SEHS2311_Hypothesis_Testing_I', '2.5'),
               ('2376', '函數、模組、pandas 入門；Assignment 1', 'Week06_SEHS2376_Functions_Modules_Pandas_Intro', '4'),
               ('2383', '軟件、雲端、資訊保安', 'Week06_SEHS2383_Software_Cloud_Security', '1.5')],
         tip='Assignment 1 在上週末開始，本週週一至三完成並檢查；其餘將 SEHS1068 放週四、五，其他週末。'),
    dict(n='7', date='10/19–10/25', alert='SEHS1068 Quiz 1（15%）；SEHS2306 Individual Assignment 1（10%）及 Online Assignment ③。', total='14.5',
         total_extra='+ Assignment',
         rows=[('1068', '極限；Part C 歷屆試題限時操練', 'Week07_SEHS1068_Limits', '4'),
               ('2306', '二項、泊松等分佈；Assignment 1 評分清單', 'Week07_SEHS2306_Ch7_Discrete_Distributions', '3|+ Assignment'),
               ('2311', '兩樣本及配對檢定；開始 Mid-term 準備', 'Week07_SEHS2311_Hypothesis_Testing_II', '3'),
               ('2376', 'loc/iloc、篩選、排序；ICE2 模擬題', 'Week07_SEHS2376_DataFrame_Manipulation', '3'),
               ('2383', '資料庫、SQL、資訊系統', 'Week07_SEHS2383_Databases_Information_Systems', '1.5')],
         tip='週一、二 SEHS1068 限時操練；週三 Quiz 1；週四、五完成並交 SEHS2306 Assignment 1；週末 SEHS2311（準備下週 Mid-term）及 SEHS2376 ICE2 模擬題。'),
]
WCOLS = [('科目', 96), ('溫習包', 262), ('重點', 226), ('時數', 70)]  # inner width 654

def week_card(wk):
    STUBW = 96
    total_extra = wk.get('total_extra', '')
    stub = (f'<div style="{st(width=f"{STUBW}px", flex_shrink="0", box_sizing="border-box", background=CHERRY_W, border_right=f"2.5px dashed {OUT}", display="flex", flex_direction="column", align_items="center", justify_content="center", gap="0px", padding="12px 6px", text_align="center")}">'
            f'<span style="{st(font_family=DISP, font_size="14px", letter_spacing="0.18em", line_height="1.3", color=CHERRY_INK)}">WEEK</span>'
            f'<span style="{st(font_family=DISP, font_size="58px", line_height="1", color=INK)}">{wk["n"]}</span>'
            f'<span style="{st(font_family=DISP, font_size="13px", line_height="1.3", color=INK2, white_space="nowrap")}">{wk["date"]}</span>'
            f'<span style="{st(margin_top="12px", padding_top="8px", border_top=f"2px dotted {OUT}", display="flex", flex_direction="column", align_items="center", gap="0px", align_self="stretch")}">'
            f'<span style="{st(font_family=TC, font_weight="700", font_size="12px", line_height="1.4", color="#8A5A1C")}">合計</span>'
            f'<span style="{st(font_family=DISP, font_size="19px", line_height="1.15", color="#8A5A1C", white_space="nowrap")}">{wk["total"]} hr</span>'
            + (f'<span style="{st(font_size="12px", line_height="1.3", color="#8A5A1C")}">{esc(total_extra)}</span>' if total_extra else '') +
            '</span></div>')
    notch = lambda pos: (f'<span aria-hidden="true" style="{st(position="absolute", left=f"{STUBW - 11}px", **{pos: "-12px"}, width="20px", height="20px", border_radius="50%", background=BG, border=f"2px solid {OUT}")}"></span>')
    body_w = CW - 4 - STUBW - 3 - 32
    alert = (f'<div style="{st(display="flex", align_items="center", gap="10px", background=BERRY_W, border=f"2px solid {BERRY}", border_radius="14px", padding="6px 12px 6px 6px")}">'
             f'{burst("注意", 38, STAMP, 11)}'
             f'<p style="{st(margin="0px", font_size="13.5px", line_height="1.55", font_weight="700", color=INK)}">{hl(wk["alert"])}</p></div>')
    ah = max(38, th(wk['alert'], body_w - 4 - 18 - 38 - 10, 13.5, 1.55, 'kb')) + 12 + 4
    rows = []
    rh_total = 0
    TXT_W = body_w - 92 - 70 - 20
    for i, (code, focus, pack, hr) in enumerate(wk['rows']):
        bb = '' if i == len(wk['rows']) - 1 else f'; border-bottom: 2px dotted {LINE}'
        if '|' in hr:
            a, b = hr.split('|')
            hrh = (f'<span style="{st(font_family=DISP, font_size="20px", line_height="1.15", color=CHERRY_INK, white_space="nowrap")}">{a}<span style="font-size: 13px; color: {INK2};"> hr</span></span>'
                   f'<span style="{st(font_size="12px", line_height="1.3", color=CHERRY_INK, white_space="nowrap")}">{esc(b)}</span>')
        else:
            hrh = f'<span style="{st(font_family=DISP, font_size="20px", line_height="1.15", color=CHERRY_INK, white_space="nowrap")}">{hr}<span style="font-size: 13px; color: {INK2};"> hr</span></span>'
        rows.append(f'<div style="{st(display="flex", align_items="flex-start", gap="10px", padding="4px 0px")}{bb}">'
                    f'<span style="{st(width="92px", flex_shrink="0", padding_top="1px")}">{chip(code, 15, 12)}</span>'
                    f'<span style="{st(flex_grow="1", min_width="0px", display="flex", flex_direction="column", gap="1px")}">'
                    f'<span style="{st(font_size="13.5px", line_height="1.45", font_weight="700", color=INK)}">{esc(focus)}</span>'
                    f'<span style="{st(font_size="12px", line_height="1.4", color=INK2, overflow_wrap="anywhere")}">{fn(pack)}</span></span>'
                    f'<span style="{st(width="70px", flex_shrink="0", display="flex", flex_direction="column", align_items="flex-end")}">{hrh}</span></div>')
        rh_total += max(th(focus, TXT_W, 13.5, 1.45, 'kb') + 1 + th(pack, TXT_W, 12, 1.4), 24, 40 if '|' in hr else 0) + 8 + 2
    rows_html = f'<div style="{st(display="flex", flex_direction="column", gap="0px")}">{"".join(rows)}</div>'
    tip = (f'<div style="{st(display="flex", align_items="flex-start", gap="10px", background=MELON_WW, border=f"2px solid {MELON}", border_radius="14px", padding="8px 12px")}">'
           f'{pill("建議", MELON_W, MELON, MELON_INK, 12.5)}'
           f'<p style="{st(margin="0px", font_size="13px", line_height="1.6", color=INK)}">{hl(wk["tip"])}</p></div>')
    tiph = th(wk['tip'], body_w - 4 - 24 - 50 - 10, 13, 1.6) + 16 + 4
    body = (f'<div style="{st(flex_grow="1", min_width="0px", padding="12px 16px", display="flex", flex_direction="column", gap="8px")}">'
            f'{alert}{rows_html}{tip}</div>')
    card = (f'<div style="{st(position="relative", display="flex", background=PAPER, border=f"2px solid {OUT}", border_radius="22px", box_shadow=f"3px 3px 0px {OUT}", overflow="hidden")}">'
            f'{stub}{body}{notch("top")}{notch("bottom")}</div>')
    return card, 12 + ah + 8 + rh_total + 8 + tiph + 12 + 4

def p06():
    head, hh = section_head('しゅうかんメニュー', 'Week 4–7 每週計劃',
                            '每週的溫習包都已完成。原則：上課前先讀 Part A（講義內容），上課後做教材練習或歷屆試題部分，週末用新練習題自測。時數已包括當週評核。',
                            title_size=32, side=300)
    c4, h4 = week_card(WEEKS[0]); c5, h5 = week_card(WEEKS[1])
    add('P06-Week4-5.dc.html', '06 Week 4・Week 5', page('Week 4–7 每週計劃（一）', 6, head + c4 + c5, gap=14), 64 + hh + 14 + h4 + 14 + h5)

def p07():
    head, hh = section_head('しゅうかんメニュー・つづき', 'Week 4–7 每週計劃（續）', title_size=28)
    c6, h6 = week_card(WEEKS[2]); c7, h7 = week_card(WEEKS[3])
    add('P07-Week6-7.dc.html', '07 Week 6・Week 7', page('Week 4–7 每週計劃（二）', 7, head + c6 + c7, gap=16), 64 + hh + 16 + h6 + 16 + h7)

# ================================================================ P08 Week 8–12
G_ROWS = [
    ('W8', '10/26–11/1', ['SEHS2311 Mid-term（20%）', 'SEHS2376 ICE2'],
     [('單側極限與連續性', 'y'), ('Ch7 延續', ''), ('總溫習 Week 3–7 溫習包', ''), ('DataFrame 摘要', ''), ('', 'n')]),
    ('W9', '11/2–11/8', ['SEHS1068 ICE3', 'SEHS2306 Online ④'],
     [('微分 I', 'y'), ('Ch8 連續分佈', 'n'), ('Lecture 08 χ²、F 檢定', 'y'), ('變數轉換、合併', ''), ('', 'n')]),
    ('W10', '11/9–11/15', ['SEHS2376 Assignment 2（20%）'],
     [('微分 II', 'y'), ('Ch8 延續', ''), ('Lecture 09–10 無母數檢定', 'y'), ('髒資料、日期時間', ''), ('', 'n')]),
    ('W11', '11/16–11/22', ['SEHS1068 Individual Assignment（30%）+ ICE4', 'SEHS2306 Online ⑤', 'SEHS2376 ICE3'],
     [('不定積分', 'y'), ('Ch9 抽樣分佈', 'n'), ('Lecture 11 迴歸 I', 'y'), ('表格及視覺化', ''), ('', 'n')]),
    ('W12', '11/23–11/29', ['SEHS1068 Quiz 2', 'SEHS2306 ICE2', 'SEHS2311 In-class Assignment 2'],
     [('定積分', 'y'), ('Ch10 推論統計', 'n'), ('迴歸 II', ''), ('Vibe coding', ''), ('', 'n')]),
    ('W13', '11/30–12/5', ['SEHS2306 Online ⑥'],
     [('數學歸納法', 'y'), ('Ch10 延續', ''), ('Course revision', ''), ('資料私隱', ''), ('', 'n')]),
]
GCOLS = [('週次', 72), ('評核', 162), ('1068', 98), ('2306', 98), ('2311', 100), ('2376', 86), ('2383', 70)]  # 686

def status_tag(kind, mt='4px'):
    if kind == 'y':
        return (f'<span style="{st(display="inline-flex", align_items="center", gap="3px", margin_top=mt, padding="0px 7px 0px 5px", border_radius="99px", background=MELON_W, border=f"1.5px solid {MELON}", color=MELON_INK, font_family=TC, font_weight="700", font_size="12px", line_height="1.5", white_space="nowrap")}">'
                f'{check_icon(MELON_INK, 11)}有教材</span>')
    return (f'<span style="{st(display="inline-block", margin_top=mt, padding="0px 7px", border_radius="99px", border="1.5px dashed #C9A0A8", color=INK2, font_family=TC, font_weight="700", font_size="12px", line_height="1.5", white_space="nowrap")}">待教材</span>')

def p08():
    legend = (f'<div style="{st(display="flex", align_items="center", gap="8px", flex_wrap="wrap", justify_content="flex-end", font_size="12.5px", color=INK2, padding_bottom="6px")}">'
              f'{status_tag("y", "0px")}<span>已在資料夾</span><span style="width: 6px;"></span>{status_tag("n", "0px")}<span>仍未上載</span></div>')
    head, hh = section_head('これからのよてい', 'Week 8–12 及考試前計劃', right=legend, lede=
                            '這幾週的溫習包未製作。SEHS1068（Week 8–13 講義及歷屆試題）和 SEHS2311（Lecture 08–11 連 Tutorial 答案）的教材已在資料夾，隨時可以製作；SEHS2306 Ch8 起、SEHS2376 Lecture 4 起及 SEHS2383 Lecture 4 起仍未上載。建議每週週五前製作下一週的溫習包。')
    colg = ''.join(f'<col style="width: {w}px;">' for _, w in GCOLS)
    ths = []
    for t, w in GCOLS:
        if t in SUBJ:
            c = SUBJ[t]
            ths.append(f'<th scope="col" style="{st(padding="8px 6px", text_align="left", background=c["w"], border_bottom=f"2px solid {OUT}", border_left=f"2px dotted {LINE}")}">'
                       f'<span style="{st(display="block", font_family=DISP, font_size="12px", line_height="1.2", color=c["ink"], font_weight="400")}">SEHS</span>'
                       f'<span style="{st(display="block", font_family=DISP, font_size="19px", line_height="1.1", color=c["ink"], font_weight="400")}">{t}</span></th>')
        else:
            ths.append(f'<th scope="col" style="{st(padding="8px 8px", text_align="left", vertical_align="bottom", font_family=TC, font_weight="700", font_size="13px", color=INK, background=CHERRY_W, border_bottom=f"2px solid {OUT}")}">{t}</th>')
    pts = {'W8': '週一至三用 Week 3–7 SEHS2311 溫習包的總結卡及 Tutorial 題目總溫習；週末準備 SEHS2376 ICE2（Week 7 Part F）。',
           'W10': 'SEHS1068 Individual Assignment 建議從本週開始，分段完成；SEHS2376 Assignment 2 在 Week 9 尾開始。',
           'W11': '全學期最重的一週。週一至三專注 SEHS1068 Individual Assignment，其餘科目只維持課堂進度。',
           'W12': '三個評核同週；週一、二 SEHS1068 積分操練，其後 SEHS2306 ICE2（Week 6–7 溫習包）及 SEHS2311 迴歸。'}
    trs = []
    est = 50
    for i, (wk, date, items, cells) in enumerate(G_ROWS):
        last = i == len(G_ROWS) - 1
        has_pt = wk in pts
        bb = f'2px dotted {LINE}' if has_pt else ('none' if last else f'2px solid {LINE2}')
        td = st(padding="8px 7px", vertical_align="top", font_size="12.5px", line_height="1.5", color=INK, border_bottom=bb)
        wkh = (f'<span style="{st(display="block", font_family=DISP, font_size="21px", line_height="1.15")}">{wk}</span>'
               f'<span style="{st(display="block", font_family=DISP, font_size="12px", line_height="1.3", color=INK2, margin_top="2px")}">{date}</span>')
        its = ''.join(f'<li style="{st(font_weight="700")}">{hl(x)}</li>' for x in items)
        row = [f'<td style="{td}; background: {BERRY_W}; border-right: 2px solid {LINE2};">{wkh}</td>',
               f'<td style="{td}"><ul style="{st(list_style="none", padding="0px", display="flex", flex_direction="column", gap="3px")}">{its}</ul></td>']
        hs = [sum(th(x, GCOLS[1][1] - 14, 12.5, 1.5, 'kb') for x in items) + 3 * (len(items) - 1)]
        for j, (txt, kind) in enumerate(cells):
            w = GCOLS[2 + j][1]
            parts = []
            if txt:
                parts.append(f'<span style="display: block;">{esc(txt)}</span>')
            if kind:
                parts.append(status_tag(kind))
            bg = f'; background: {MELON_WW}' if kind == 'y' else ''
            row.append(f'<td style="{td}; border-left: 2px dotted {LINE}{bg};">{"".join(parts)}</td>')
            hs.append((th(txt, w - 14, 12.5, 1.5) if txt else 0) + (22 if kind else 0))
        est += max(hs + [40]) + 16 + 2
        trs.append('<tr>' + ''.join(row) + '</tr>')
        if has_pt:
            hot = wk == 'W11'
            pbb = 'none' if last else f'2px solid {LINE2}'
            lab = pill('重點安排', VANILLA, CARAMEL, '#8A5A1C', 12)
            extra = burst('最重', 38, STAMP, 11) if hot else ''
            trs.append(f'<tr><td colspan="7" style="{st(padding="7px 12px 8px", background=VANILLA_W, border_bottom=pbb)}">'
                       f'<div style="{st(display="flex", align_items="center", gap="10px")}">{lab}'
                       f'<p style="{st(margin="0px", flex_grow="1", font_size="13px", line_height="1.6", color=INK)}">{hl(pts[wk])}</p>{extra}</div></td></tr>')
            est += max(th(pts[wk], CW - 4 - 24 - 80 - 10 - (48 if hot else 0), 13, 1.6), 38 if hot else 0) + 15 + 2
    grid = (f'<div style="{st(background=PAPER, border=f"2px solid {OUT}", border_radius="20px", box_shadow=f"3px 3px 0px {OUT}", overflow="hidden")}">'
            f'<table style="{st(width="100%", table_layout="fixed")}"><colgroup>{colg}</colgroup><thead><tr>{"".join(ths)}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>')
    content = head + grid
    add('P08-Week8-12.dc.html', '08 Week 8–12', page('Week 8–12 及考試前計劃', 8, content, gap=16), 64 + hh + 16 + est)

# ================================================================ P09 Week 13 之後 + 應試策略 ①
D_ROWS = [
    ('1068', 'ICE1–ICE4', 'tutorial 後即開始；先用總結卡溫一次公式', '當週 Part F/G 總結卡', '24 小時限時，答案要寫步驟'),
    ('1068', 'Quiz 1', 'Basic Limit 歷屆題限時做（每題約 4–5 分鐘）', 'Week 7 Part C', 'Closed book 45 分鐘；寫出方法句子（如「有理化」）'),
    ('1068', 'Individual Assignment', '只用各週方法框及相似例題，自己完成', 'Week 5–6 及後續', '答案要精確值；大量抄用 AI 內容屬抄襲'),
    ('2306', 'ICE1', '定義題（population、parameter、sample、statistic）、數據類型、抽樣方法、圖表讀數', 'Week 1–3', 'Population 要寫「All …」；nominal 不要拼錯'),
    ('2306', 'Individual Assignment 1', '按評分準則列表逐項檢查', 'Week 7 Part B', '圖表要專業；詮釋要具批判性'),
    ('2306', 'ICE2', '隨機變數期望值、方差及離散分佈', 'Week 6–7', '先判斷用哪個分佈'),
    ('2311', 'In-class Assignment 1', '置信區間公式、z/t 表查法', 'Week 1, 3–5', '帶齊小計數機及公式'),
    ('2311', 'Mid-term', '先用決策表選檢定，再做 Tutorial 04–07', 'Week 7 Part E、Week 6 Part E', 'H0 永遠含等號；結論要用文字'),
    ('2376', 'ICE1–ICE3', '限時寫完整程式並在 Colab 執行', 'Week 5 模擬題、Week 7 Part F', 'Open book；先想清流程才寫'),
    ('2376', 'Test', '每週總結卡及練習題', 'Week 1–13', 'Closed book，要能記起語法'),
    ('2383', 'Exam', '定義題及 C++ 程式追蹤', 'Week 1–7 Part 練習題', '英文術語要準確'),
    (None, '期末考（四科）', '模擬考卷限時做', '全部', '每科至少做兩份完整模擬'),
]
DCOLS = [('評核', 150), ('操練內容', 200), ('溫習包', 140), ('注意', 196)]  # 686

def d_table(rows):
    colg = ''.join(f'<col style="width: {w}px;">' for _, w in DCOLS)
    ths = ''.join(f'<th scope="col" style="{st(padding="9px 10px", text_align="left", font_family=TC, font_weight="700", font_size="13px", color=INK, background=CHERRY_W if t != "注意" else VANILLA_W, border_bottom=f"2px solid {OUT}")}">{t}</th>' for t, _ in DCOLS)
    trs = []
    est = 40
    for i, (code, name, drill, pack, note) in enumerate(rows):
        nxt = rows[i + 1][0] if i + 1 < len(rows) else 'END'
        if i == len(rows) - 1:
            bb = 'none'
        elif nxt != code:
            bb = f'2px solid {LINE2}'
        else:
            bb = f'2px dotted {LINE}'
        td = st(padding="8px 10px", vertical_align="top", font_size="13px", line_height="1.55", color=INK, border_bottom=bb)
        if code:
            nm = f'<span style="{st(display="flex", flex_direction="column", align_items="flex-start", gap="4px")}">{chip(code, 15, 12)}<span style="font-weight: 700;">{esc(name)}</span></span>'
            nh = 24 + 4 + th(name, DCOLS[0][1] - 20, 13, 1.55, 'kb')
        else:
            nm = f'<span style="{st(font_family=TC, font_weight="900", font_size="14px", color=INK)}">{esc(name)}</span>'
            nh = 22
        trs.append(f'<tr><td style="{td}">{nm}</td><td style="{td}">{esc(drill)}</td><td style="{td}">{esc(pack)}</td>'
                   f'<td style="{td}; background: #FFFBF0;">{hl(note)}</td></tr>')
        est += max(nh, th(drill, DCOLS[1][1] - 20, 13, 1.55), th(pack, DCOLS[2][1] - 20, 13, 1.55), th(note, DCOLS[3][1] - 20, 13, 1.55)) + 16 + 2
    tbl = (f'<div style="{st(background=PAPER, border=f"2px solid {OUT}", border_radius="20px", box_shadow=f"3px 3px 0px {OUT}", overflow="hidden")}">'
           f'<table style="{st(width="100%", table_layout="fixed")}"><colgroup>{colg}</colgroup><thead><tr>{ths}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>')
    return tbl, est

def p09():
    sh, shh = sub_head('Week 13 之後', 'しけんまえ')
    def step(tag, title, date, body_html, bh, bg, bd):
        return (f'<div style="{st(flex="1 1 0px", min_width="0px", background=bg, border=f"2px solid {bd}", border_radius="18px", box_shadow=f"2px 2px 0px {bd}", padding="12px 14px", display="flex", flex_direction="column", gap="6px")}">'
                f'<span style="{st(font_family=DISP, font_size="12.5px", letter_spacing="0.12em", color=INK2)}">{tag}</span>'
                f'<span style="{st(font_family=DISP, font_size="20px", line_height="1.2", color=INK)}">{title}</span>'
                + (f'<span style="{st(font_family=DISP, font_size="14px", color=CHERRY_INK)}">{date}</span>' if date else '') +
                f'<div style="{st(border_top=f"2px dotted {bd}", padding_top="6px", font_size="13px", line_height="1.6", color=INK, display="flex", flex_direction="column", gap="4px")}">{body_html}</div></div>')
    colw = (CW - 2 * 26) / 3 - 32
    b1 = '<span>' + hl('SEHS2376 Test（30%，closed book，Week 1–13）。用各週 SEHS2376 溫習包的總結卡及練習題復習。') + '</span>'
    b2 = ('<span>' + hl('SEHS1068：用 Pastpaper by Semester（2021–2026 共十二份連答案）限時模擬，配合 Pastpaper by Topic 較弱的課題。') + '</span>'
          '<span>' + hl('SEHS2306、SEHS2311、SEHS2383：各週溫習包的總結卡 + 每週 Tutorial 答案。') + '</span>')
    b3 = '<span>' + hl('SEHS1068、SEHS2306、SEHS2311、SEHS2383 期末考各佔 60%，確切日期待學校公布。') + '</span>'
    arrow = f'<div style="{st(display="flex", align_items="center", flex_shrink="0")}">{arrow_icon(OUT, 20)}</div>'
    steps = (f'<div style="{st(display="flex", align_items="stretch", gap="3px")}">'
             f'{step("テスト", "Week 14", "", b1, 0, "#E6F3FB", SODA)}{arrow}'
             f'{step("ふくしゅう", "Revision Period", "12/7–12/11", b2, 0, VANILLA_W, CARAMEL)}{arrow}'
             f'{step("しけん", "Exam Period", "12/12–12/31", b3, 0, CHERRY_W, CHERRY)}</div>')
    bmax = max(th('SEHS2376 Test（30%，closed book，Week 1–13）。用各週 SEHS2376 溫習包的總結卡及練習題復習。', colw, 13, 1.6),
               th('SEHS1068：用 Pastpaper by Semester（2021–2026 共十二份連答案）限時模擬，配合 Pastpaper by Topic 較弱的課題。', colw, 13, 1.6) + 4 +
               th('SEHS2306、SEHS2311、SEHS2383：各週溫習包的總結卡 + 每週 Tutorial 答案。', colw, 13, 1.6),
               th('SEHS1068、SEHS2306、SEHS2311、SEHS2383 期末考各佔 60%，確切日期待學校公布。', colw, 13, 1.6))
    steps_h = 24 + 18 + 6 + 24 + 6 + 20 + 6 + 8 + bmax + 4
    head, hh = section_head('ひっしょうレシピ', '應試策略及操練清單', '每個評核前一週，按下表完成操練。「溫習包」欄指週次及部分。', title_size=30, side=280)
    tbl, te = d_table(D_ROWS[:5])
    content = sh + steps + head + tbl
    est = 64 + shh + 16 + steps_h + 16 + hh + 16 + te
    add('P09-Week13-Drills.dc.html', '09 Week 13 之後・應試策略 ①', page('Week 13 之後及應試策略', 9, content, gap=16), est)

# ================================================================ P10 應試策略 ② + 通用原則
def p10():
    head, hh = section_head('ひっしょうレシピ・つづき', '應試策略及操練清單（續）', title_size=28)
    tbl, te = d_table(D_ROWS[5:])
    rule = '每週週末用該週溫習包的新練習題自測，答錯的題目記在一頁「錯題表」，評核前先看錯題表。'
    rule_card = (f'<div style="{st(display="flex", align_items="center", gap="20px", background=VANILLA_W, border=f"2.5px solid {CARAMEL}", border_radius="26px", box_shadow=f"5px 5px 0px {CARAMEL}", padding="18px 24px 18px 18px")}">'
                 f'{pudding(112)}'
                 f'<div style="{st(display="flex", flex_direction="column", gap="6px", min_width="0px")}">'
                 f'<span style="{st(font_family=DISP, font_size="15px", letter_spacing="0.14em", color="#8A5A1C")}">おみせのルール ・ まちがいノート</span>'
                 f'<h3 style="{st(margin="0px", font_family=TC, font_weight="900", font_size="22px", line_height="1.3", color=INK)}">通用原則</h3>'
                 f'<p style="{st(margin="0px", font_size="16px", line_height="1.7", color=INK, font_weight="700")}">{hl(rule)}</p></div></div>')
    rh = max(130, 22 + 30 + 12 + th(rule, CW - 50 - 112 - 20, 16, 1.7, 'kb')) + 36 + 5
    content = head + tbl + rule_card
    est = 64 + hh + 18 + te + 26 + rh
    add('P10-Drills-2.dc.html', '10 應試策略 ②・通用原則', page('應試策略及操練清單（續）', 10, content, gap=18), est)

# ================================================================ P11 缺漏教材追蹤 + back cover
def p11():
    mhead, mh = section_head('おとりよせリスト', '缺漏教材追蹤',
                             '下列溫習包的部分內容是按課程大綱及標準教科書撰寫的（PDF 內有粉紅框標明）。把教材放入對應資料夾後，說一聲「更新 Week X」，就會用正式教材重寫。補上後請在左邊打剔。')
    items = ['SEHS2306 Ch4 講義（Week 4；現只有 Tutorial 及 Counting Rules Summary）',
             'SEHS2306 Ch5 及 Ch7 Tutorial（Week 5、7）',
             'SEHS2306 Individual Assignment 1 題目（Week 7；只用作檢查評分清單，不會代做）',
             'SEHS2306 Ch8–Ch10（Week 9–13）',
             'SEHS2311 Lecture 05 及 Tutorial 05（Week 5）',
             'SEHS2376 Lecture 4–7 的 PDF 及 notebooks（Week 4–7）',
             'SEHS2376 Lecture 8 起（Week 8–13）',
             'SEHS2383 Week 4–7 講義（網絡、AI 倫理、軟件雲端保安、資料庫；現時主題是按大綱推斷）',
             'SEHS2383 Week 8 起講義及各評核交期']
    lis = []
    ih = 0
    for i, it in enumerate(items):
        bb = '' if i == len(items) - 1 else f'; border-bottom: 2px dotted {LINE}'
        lis.append(f'<label style="{st(display="flex", align_items="flex-start", gap="12px", padding="8px 0px", font_size="14px", line_height="1.55", color=INK, cursor="pointer")}{bb}">'
                   f'<input type="checkbox" class="tick" style="margin-top: 1px;"><span>{hl(it)}</span></label>')
        ih += max(th(it, CW - 44 - 32, 14, 1.55), 22) + 18
    order = (f'<div style="{card_style(22, "8px 22px 10px", PAPER, 3, 2)}; display: flex; flex-direction: column;">'
             f'<div style="{st(display="flex", align_items="baseline", gap="10px", padding="6px 0px 8px", border_bottom=f"2px solid {LINE2}")}">'
             f'<span style="{st(font_family=DISP, font_size="18px", color=CHERRY_INK)}">ちゅうもんひょう</span>'
             f'<span style="{st(font_size="12.5px", color=INK2)}">補上後打剔</span></div>{"".join(lis)}</div>')
    code = lambda t: f'<span style="{st(background=BERRY_W, border=f"1.5px solid {LINE2}", border_radius="6px", padding="0px 6px", color=INK, white_space="nowrap")}">{t}</span>'
    tail = (f'<p style="{st(margin="0px", font_size="13.5px", line_height="1.8", color=INK)}">完整清單（連已指出的教材錯處）在 {code("Study Packs/MISSING_MATERIALS.md")}'
            f'，亦已存入 Project。重建溫習包用的工具包在 {code("Study Packs/_build")}。</p>')
    tlh = th('完整清單（連已指出的教材錯處）在 Study Packs/MISSING_MATERIALS.md ，亦已存入 Project。重建溫習包用的工具包在 Study Packs/_build 。', CW, 13.5, 1.8)
    sign = (f'<div style="{st(margin_top="auto", display="flex", flex_direction="column", align_items="center", gap="10px", padding_bottom="4px")}">'
            f'<div style="{st(display="flex", align_items="flex-end", gap="18px")}">{flower(30, BERRY, VANILLA)}{pudding(96)}{cream_soda(84)}{flower(30, MELON, VANILLA)}</div>'
            f'<span style="{st(font_family=DISP, font_size="22px", letter_spacing="0.16em", color=CHERRY_INK)}">ごちそうさまでした</span>'
            f'<span style="{st(display="inline-flex", align_items="center", gap="8px", background=INK, color=BG, border_radius="99px", padding="5px 18px 5px 12px", font_family=TC, font_weight="700", font_size="13px", letter_spacing="0.24em")}">{flower(16, BERRY, VANILLA)}純喫茶 溫習庫</span></div>')
    signh = 112 + 10 + 30 + 10 + 30
    content = mhead + order + tail + sign
    est = 64 + mh + 18 + 20 + 32 + ih + 18 + tlh + 30 + signh
    add('P11-Materials.dc.html', '11 缺漏教材追蹤', page('缺漏教材追蹤', 11, content, gap=18), est)

for f in (p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11):
    f()

# ---------------------------------------------------------------- write
for fname, _, src in PAGES:
    open(os.path.join(PROJ, fname), 'w', encoding='utf-8').write(src)

boards = {}
order = []
PER_ROW = 6
for i, (fname, bt, _) in enumerate(PAGES):
    r, c = divmod(i, PER_ROW)
    boards[fname] = {"x": c * (W + 80), "y": r * (H + 120), "w": W, "h": H, "title": bt}
    if fname in ('P05-This-Week.dc.html', 'P11-Materials.dc.html'):
        boards[fname]["is_interactive"] = True
    order.append(fname)
now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": now}, "title": "溫習計劃 昭和喫茶",
          "launch": {"view": "canvas"}, "pages": [], "boards": boards, "order": order, "notes": {}, "designSystems": []}
json.dump(canvas, open(os.path.join(PROJ, 'canvas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

LIMIT = H - 60
for fname, _, src in PAGES:
    e = EST[fname]
    print(f'{fname:32s} est bottom {e:7.0f}  limit {LIMIT}  {"OVER" if e > LIMIT - 20 else "ok"}  {len(src)//1024}KB')
