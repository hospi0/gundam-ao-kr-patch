# -*- coding: utf-8 -*-
r"""건담 외전 II 결과 화면·시나리오 제목 그림 한글(2026-10-10, 1편 tools/scgfx.py 에서) — 무압축 4비트 그림 제자리 덮어쓰기.
  팔레트: 16단계 회색(0 = 흰색 … 15 = 검정), 그림마다 앞 0x20 B 에 팔레트. 글자 = 흰색 안티에일리어스 → 덮인 정도로 색 번호(15 − 15×덮임).
  · SC_1.BIN 한마디 288×80 21장(교관 평가 + 실패 메시지) — 틀(바깥 3 px)은 두고 안쪽 지우고 다시 씀
  · SC_1.BIN 항목 이름 240×80(16곳 같은 그림) — 글자 자리(왼쪽 이름·오른쪽 단위)만
  · SC_1.BIN 단위 열 40×80(17곳) — 点 → 점
  · S0_1.BIN 시나리오 제목 240×32 5장(TITLE_BASE + n×0xF20) — 기울인 굵은 글씨
  python tools/scgfx.py   → work/gfx/*.png 미리보기(위 원본 · 아래 한글)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
NG = r'C:\claude\utils\font\nanum-gothic'

COMMENTS = [   # (위치, 한국어) — 2편 21장(1편 14장 + 0x4D4A8 부터 7장), 실패 5장은 1편과 같은 그림
    (0x5820, '소문 이상의 실력이군. 그 기세로 연방을 승리로 이끌어 주게.'),
    (0xBD88, '꽤 좋은 실력이다. 앞으로도 크게 활약해 주게.'),
    (0xEAA8, '아직 멀었군. 전장에서는 늘 주위 상황을 파악하고 있지 않으면 살아남지 못한다.'),
    (0x117C8, '이 작전의 성공은 자네 어깨에 달려 있다. 부탁한다, 기적을 일으켜 주게.'),
    (0x144E8, '일단은 성공이다. 하지만 방심하지 마라, 지금부터가 진짜다.'),
    (0x17208, '그래서야 적 미사일 기지 작전이 걱정이군. 이제 신에게라도 빌어야 하나.'),
    (0x19F28, '위기는 넘겼다. 잘해 주었다. 자네와 블루는 연방의 구세주다.'),
    (0x1CC48, '위기는 넘겼다. 이로써 소탕 작전은 성공한 것이나 다름없다.'),
    (0x1F968, '위기는 넘겼다. 하지만 지금 그대로는 블루를 완전히 다룰 수 없다.'),
    (0x22688, '자기 파손율 높음.|전투 속행 불능입니다.'),
    (0x253A8, '작전 행동 중 전선을 이탈.|적전 도망으로 간주합니다.'),
    (0x280C8, '적의 공격으로 방어 지점이|파괴되었습니다.'),
    (0x2ADE8, '작전 시간 초과.|임무 실패입니다.'),
    (0x2DB08, 'EXAM 시스템 가동 임계점 돌파.|전투 속행 불능.'),
    (0x4D4A8, '자네가 참전한다는 소식에 아군의 사기도 올랐다. 승리가 눈앞이다.'),
    (0x501C8, '이로써 지구 연방군의 지상 승리가 거의 결정됐군.'),
    (0x52EE8, '모빌슈트 파일럿으로서는 아직 미숙하다. 장갑 너머로 적의 기척을 느껴라.'),
    (0x55C08, '이제 자네 이름을 듣고도 도망치지 않는 건 지온의 붉은 혜성 정도뿐이겠지.'),
    (0x58928, '자네 전적은 훌륭하다. 뭐, 제13독립부대에는 못 미치지만. 앞으로도 힘내 주게.'),
    (0x5B648, '작전은 성공했지만 아군 피해도 막심하다. 좀 더 실력을 갈고닦아 주게.'),
    (0x5E368, '적의 공격으로 조사대 헬기가|격추되었습니다.'),
]
TITLES = ['푸른 운명', '그 이름은 블루', '타임 리미트', '지온 소탕 작전', '숙명의 대결']
TITLE_BASE = 0x16A0          # S0_1 240×32 5장(간격 0xF20)
LABELS = ['전술득점', '피탄율', '종합전적']
LABEL_POS = [0x3280]          # 대표(같은 그림 16곳은 build 에서 전부)


def get4(d, o, w, h):
    b = np.frombuffer(d[o:o + w * h // 2], np.uint8)
    return np.stack([b >> 4, b & 15], 1).ravel().reshape(h, w).copy()


def put4(d, o, px):
    f = px.ravel().astype(np.uint8)
    d[o:o + len(f) // 2] = ((f[0::2] << 4) | f[1::2]).tobytes()


def cover(lines, font, size, w, h, align='left', x0=0, y0=0, lh=None, shear=0.0, center_block=True):
    """흰 글자 덮임(0‥1) — lines 를 (x0,y0) 부터 lh 간격, 블록 가로 가운데"""
    F = ImageFont.truetype(os.path.join(NG, font), size)
    big = Image.new('L', (w * 4, h * 4), 0); d = ImageDraw.Draw(big)
    F4 = ImageFont.truetype(os.path.join(NG, font), size * 4)
    lh = lh or size + 6
    widths = [d.textlength(t, font=F4) for t in lines]; bw = max(widths)
    bx = (w * 4 - bw) / 2 if center_block else x0 * 4
    for i, t in enumerate(lines):
        x = bx + ((bw - widths[i]) / 2 if align == 'center' else 0)
        d.text((x, (y0 + i * lh) * 4), t, font=F4, fill=255)
    if shear:
        big = big.transform(big.size, Image.AFFINE, (1, shear, -shear * big.size[1] / 2, 0, 1, 0), Image.BICUBIC)
    return np.asarray(big.resize((w, h), Image.LANCZOS), np.float32) / 255


def wrap(text, font, size, maxw):
    F = ImageFont.truetype(os.path.join(NG, font), size); d = ImageDraw.Draw(Image.new('L', (1, 1)))
    out = []
    for part in text.split('|'):
        cur = ''
        for wd in part.split(' '):
            t = (cur + ' ' + wd).strip()
            if d.textlength(t, font=F) <= maxw: cur = t
            else: out.append(cur); cur = wd
        out.append(cur)
    return out


def ink(px, cov, box):
    """box(x0,y0,x1,y1) 안을 배경 15 로 지우고 덮임만큼 흰색"""
    x0, y0, x1, y1 = box
    px[y0:y1, x0:x1] = 15
    idx = np.clip(np.round(15 - 15 * cov), 0, 15).astype(np.uint8)
    m = cov > 0.03
    sub = px[y0:y1, x0:x1]; sub[m[y0:y1, x0:x1]] = idx[y0:y1, x0:x1][m[y0:y1, x0:x1]]
    return px


def comment(px, text):
    lines = wrap(text, 'NanumGothicBold.ttf', 16, 272)
    assert len(lines) <= 3, (text, lines)
    lh = 23; top = (80 - (lh * (len(lines) - 1) + 18)) // 2 - 1
    cov = cover(lines, 'NanumGothicBold.ttf', 16, 288, 80, y0=top, lh=lh)
    return ink(px, cov, (4, 4, 284, 76)), lines


def title(px, text):
    cov = cover([text], 'NanumGothicExtraBold.ttf', 24, 240, 32, align='center', y0=2, shear=0.18)
    return ink(px, cov, (0, 0, 240, 32))


ROWS = [(7, 24), (30, 47), (54, 71)]   # 원본 글자 줄 8‥22·31‥45·55‥69(구분선 26·49·74 는 안 건드림)


def label(px):
    for (y0, y1), t in zip(ROWS, LABELS):
        cov = cover([t], 'NanumGothicBold.ttf', 15, 240, 80, x0=14, y0=y0, center_block=False)
        px = ink(px, cov, (12, y0, 82, y1))
    for (y0, y1), t in zip(ROWS, ('점', None, '점')):
        if not t: continue
        cov = cover([t], 'NanumGothicBold.ttf', 15, 240, 80, x0=204, y0=y0, center_block=False)
        px = ink(px, cov, (200, y0, 224, y1))
    return px


def unit(px):
    """40×80 = «評価» 칸(위 글자만) → 평가"""
    cov = cover(['평가'], 'NanumGothicBold.ttf', 15, 40, 80, align='center', y0=7)
    return ink(px, cov, (3, 5, 37, 25))


def same_spots(d, o, w, h):
    """같은 그림이 있는 모든 위치(첫 줄 + 가운데 줄이 같은 곳)"""
    img = d[o:o + w * h // 2]; out = []; i = d.find(img)
    while i >= 0: out.append(i); i = d.find(img, i + 1)
    return out


def patch_sc1(sc1):
    d = bytearray(sc1); log = []
    for o, t in COMMENTS:
        px, lines = comment(get4(d, o, 288, 80), t); put4(d, o, px); log.append((hex(o), lines))
    lab = get4(sc1, 0x3280, 240, 80); new = label(lab.copy())
    spots = same_spots(sc1, 0x3280, 240, 80)
    for o in spots: put4(d, o, new)
    un = get4(sc1, 0x20, 40, 80); nu = unit(un.copy())
    uspots = same_spots(sc1, 0x20, 40, 80)
    for o in uspots: put4(d, o, nu)
    return bytes(d), log, len(spots), len(uspots)


def patch_s01(s01):
    d = bytearray(s01)
    for n, t in enumerate(TITLES):
        o = TITLE_BASE + n * 0xF20; put4(d, o, title(get4(d, o, 240, 32), t))
    return bytes(d)


def preview():
    import disc
    sc1 = disc.read('/SC_1.BIN'); s01 = disc.read('/S0_1.BIN')
    n1, log, ns, nu = patch_sc1(sc1); n0 = patch_s01(s01)
    gray = lambda a: (255 - a.astype(np.int32) * 17).astype(np.uint8)
    os.makedirs(os.path.join(ROOT, 'work', 'gfx'), exist_ok=True)
    rows = []
    for o, _ in COMMENTS:
        rows += [np.hstack([gray(get4(sc1, o, 288, 80)), np.full((80, 6), 128, np.uint8), gray(get4(n1, o, 288, 80))]), np.full((6, 582), 128, np.uint8)]
    Image.fromarray(np.vstack(rows)).resize((582 * 2, len(rows) // 2 * 86 * 2), Image.NEAREST).save(os.path.join(ROOT, 'work', 'gfx', 'comments.png'))
    rows = []
    for n in range(5):
        o = TITLE_BASE + n * 0xF20
        rows += [np.hstack([gray(get4(s01, o, 240, 32)), np.full((32, 6), 128, np.uint8), gray(get4(n0, o, 240, 32))]), np.full((6, 486), 128, np.uint8)]
    rows += [np.hstack([gray(get4(sc1, 0x3280, 240, 80)), np.full((80, 6), 128, np.uint8), gray(get4(n1, 0x3280, 240, 80))])]
    rows += [np.full((6, 486), 128, np.uint8), np.hstack([gray(get4(sc1, 0x20, 40, 80)), np.full((80, 6), 128, np.uint8), gray(get4(n1, 0x20, 40, 80)), np.full((80, 400), 128, np.uint8)])]
    a = np.vstack(rows); Image.fromarray(a).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST).save(os.path.join(ROOT, 'work', 'gfx', 'titles_labels.png'))
    for l in log: print(l)
    print('항목 이름 그림 %d곳 · 단위 열 %d곳' % (ns, nu))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    preview()
