# -*- coding: utf-8 -*-
"""표준사전 CSV 넷을 사람이 보는 통합 엑셀 한 권으로 묶는다."""
import csv, os, glob
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 저장소 뿌리
OUT  = os.path.join(BASE, "design", "standard-dict")
FONT = "Apple SD Gothic Neo"
HEAD = PatternFill("solid", fgColor="1F3864")
ZEBRA = PatternFill("solid", fgColor="F2F5FA")
THIN = Side(style="thin", color="D0D7E5")
BOX  = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

SHEETS = [
    ("표준단어정의서", "표준단어정의서.csv"),
    ("표준도메인정의서", "표준도메인정의서.csv"),
    ("표준용어정의서", "표준용어정의서.csv"),
    ("표준코드정의서", "표준코드정의서.csv"),
    ("사유코드정의서", "사유코드정의서.csv"),
    ("ref 테이블정의서", "ref테이블정의서.csv"),
    ("svc 테이블정의서", "svc테이블정의서.csv"),
    ("인덱스정의서", "인덱스정의서.csv"),
    ("제약정의서", "제약정의서.csv"),
]

COVER = [
    ("주소정제 솔루션 — 표준 사전", ""),
    ("", ""),
    ("무엇인가", "테이블 17개·칼럼 100개의 물리명을 행정안전부 공통표준단어·공통표준용어와 대조한 결과다"),
    ("재료", "erd-physical.drawio · 공통표준단어 3,284건 · 공통표준용어 13,176건 (2025-11-01 배포)"),
    ("서식", "「공공기관의 데이터베이스 표준화 지침」 별지 원문을 못 열어 우리 서식으로 냈다"),
    ("적용 의무", "지침의 적용 대상은 공공기관이다. 이 솔루션은 민간이라 의무가 아니다"),
    ("", ""),
    ("이번에 채운 것", ""),
    ("허용오타횟수", "prm_typo_nmtm   허용 PRM + 오타 TYPO + 횟수 NMTM"),
    ("후보상한", "cand_uplmt      후보 CAND + 상한 UPLMT"),
    ("페이지크기", "page_sz         쪽 PAGE + 크기 SZ   ← 「쪽」의 이음동의어에 페이지가 있다"),
    ("", ""),
    ("이번에 바로잡은 것", "표준에 없던 우리 조어 둘을 표준 약어로 바꿨다"),
    ("대표 rep → rprs", "ref.building의 대표지번 칼럼 넷"),
    ("설정 cfg → stng", "svc.config의 설정식별자와 svc.request의 외래키"),
    ("", ""),
    ("프로젝트 신규 표준단어 여섯", "동(棟) BLK · 호 HO · 접미사 SFX · 전 BFR · 오타 TYPO · 후보 CAND"),
    ("", ""),
    ("코드값을 적는 방식", "값 목록을 확정하지 않는다. 구분 기준·값의 범위·형식 세 층으로 적는다"),
    ("", "값을 더하는 것은 구현이 해도 된다. 빼는 것은 과거 줄이 뜻을 잃으므로 설계로 돌아온다"),
]

def style_header(ws, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF", size=11)
        cell.fill = HEAD
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BOX
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(ncol)}{ws.max_row}"

def autosize(ws, ncol, cap=52):
    for c in range(1, ncol + 1):
        w = max((len(str(ws.cell(row=r, column=c).value or "")) for r in range(1, ws.max_row + 1)),
                default=8)
        ws.column_dimensions[get_column_letter(c)].width = min(max(w * 1.35 + 2, 9), cap)

wb = Workbook()
ws = wb.active; ws.title = "읽는 법"
for i, (a, b) in enumerate(COVER, start=1):
    ws.cell(row=i, column=1, value=a).font = Font(name=FONT, bold=(b == "" and a != ""), size=14 if i == 1 else 11)
    ws.cell(row=i, column=2, value=b).font = Font(name=FONT, size=11)
    ws.cell(row=i, column=2).alignment = Alignment(vertical="center")
ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 96
ws.sheet_view.showGridLines = False

for name, fn in SHEETS:
    rows = list(csv.reader(open(os.path.join(OUT, fn), encoding="utf-8-sig")))
    s = wb.create_sheet(name)
    for r in rows: s.append(r)
    n = len(rows[0])
    for r in range(2, s.max_row + 1):
        for c in range(1, n + 1):
            cell = s.cell(row=r, column=c)
            cell.font = Font(name=FONT, size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BOX
            if r % 2 == 0: cell.fill = ZEBRA
    style_header(s, n)
    autosize(s, n)

path = os.path.join(OUT, "표준사전.xlsx")
wb.save(path)
print("냈다:", path)
for name, fn in SHEETS:
    print(f"  {name}: {sum(1 for _ in open(os.path.join(OUT, fn), encoding='utf-8-sig')) - 1}행")
