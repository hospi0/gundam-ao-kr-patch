# -*- coding: utf-8 -*-
r"""건담 외전 II 훅 주소(2026-10-10, tools/port_find.py 로 1편 주소에서 옮김 — 함수 머리 32 B 일치·리터럴 하나뿐)
  1편(gundam-blue) VBI 0x060449D6/리터럴 0x06044BE8 · VIN 0x0604487E/0x06044BE4 · DMA 끝 0x0604486C/0x06044BF4 · 견본 리터럴 0x06048474 · 스트림 0x06014220
  TPL = 1편 견본(0x3C1 B 0 구간 안 +0x271)과 같은 자리 · RES‥END = S0_1 끝(0x2568D4)‥가장 이른 Sn_1 적재
  NT = 스트림 표 칸 수(SS_SND 6번부터)
"""
VBI = 0x60468EE
VBI_LIT = 0x6046B00
VIN = 0x6046796
VIN_LIT = 0x6046AFC
DMAE = 0x6046784
DMAE_LIT = 0x6046B0C
TPL = 0x603DB18
TPL_LIT = 0x604A38C
TPL_OLD = 0x8604A372
STREAM = 0x6014220
RES = 0x256A00
END = 0x25B000
NT = 64
S01END = 0x2568D4
