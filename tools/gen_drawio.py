#!/usr/bin/env python3
# 물리 ERD — draw.io 파일 생성기 (혼자 돈다)
# 근거: 02-data-model.md 6-4절. 자리와 배선은 이 파일이 정한다.
# 한 줄에 PK · 논리명 · 물리명 · 자료형 넷을 적는다.
#
# 주의 — draw.io에서 상자를 옮겨 저장한 뒤에는 erd-physical.drawio가 정본이다.
#        이 파일을 다시 돌리면 옮긴 자리가 사라진다.

# ── 명세 ──────────────────────────────────────────────
# 테이블: 키 -> (표시이름, [(칼럼, 자료형, 키표시, 비고)])
TABLES = {'region': ('region · 행정구역',
            [('stdg_cd', 'varchar(10)', 'PK', ''),
             ('up_stdg_cd', 'varchar(10)', '', '상위 법정동코드'),
             ('stp', 'smallint', '', '1시도 2시군구 3읍면동 4리'),
             ('admdst_nm', 'varchar(40)', '', 'NOT NULL')]),
 'road': ('road · 도로명',
          [('road_nm_cd', 'varchar(12)', 'PK', ''),
           ('road_nm', 'varchar(80)', '', 'NOT NULL'),
           ('up_road_nm_no', 'varchar(7)', '', ''),
           ('use_yn', 'varchar(1)', '', '0이 사용')]),
 'token': ('token · 주소표기 (파생)',
           [('tkn', 'varchar(100)', 'PK', ''),
            ('tkn_se', 'varchar(1)', 'PK', 'R 도로명 J 법정동 B 건물이름 H 행정동')]),
 'road_emd': ('road_emd · 도로명이 지나는 읍면동',
              [('road_nm_cd', 'varchar(12)', 'PK', ''),
               ('emd_sn', 'varchar(2)', 'PK', ''),
               ('emd_cd', 'varchar(3)', '', '법정동 기준'),
               ('emd_se', 'varchar(1)', '', ''),
               ('ancmnt_ymd', 'date', '', '고시일자')]),
 'lot': ('lot · 지번',
         [('stdg_cd', 'varchar(10)', 'PK', ''),
          ('mtn_yn', 'varchar(1)', 'PK', ''),
          ('mno', 'smallint', 'PK', ''),
          ('sno', 'smallint', 'PK', '')]),
 'address': ('address · 등록주소',
             [('road_nm_addr_mng_no', 'varchar(26)', 'PK', ''),
              ('road_nm_cd', 'varchar(12)', '', 'NOT NULL'),
              ('udgd_yn', 'varchar(1)', '', 'NOT NULL'),
              ('bmno', 'integer', '', 'NOT NULL'),
              ('bsno', 'integer', '', 'NOT NULL'),
              ('stdg_cd', 'varchar(10)', '', 'NOT NULL'),
              ('zip', 'varchar(5)', '', '기초구역번호'),
              ('aptcpx_se', 'varchar(1)', '', ''),
              ('efctn_ymd', 'date', '', '')]),
 'address_lot': ('address_lot · 관련지번',
                 [('stdg_cd', 'varchar(10)', 'PK', ''),
                  ('mtn_yn', 'varchar(1)', 'PK', ''),
                  ('mno', 'smallint', 'PK', ''),
                  ('sno', 'smallint', 'PK', ''),
                  ('road_nm_addr_mng_no', 'varchar(26)', 'PK', '')]),
 'building': ('building · 건물',
              [('bldg_mng_no', 'varchar(25)', 'PK', ''),
               ('road_nm_addr_mng_no', 'varchar(26)', '', 'NULL 허용 · 서울 230채'),
               ('rprs_stdg_cd', 'varchar(10)', '', '대표지번'),
               ('rprs_mtn_yn', 'varchar(1)', '', ''),
               ('rprs_mno', 'smallint', '', ''),
               ('rprs_sno', 'smallint', '', ''),
               ('bdrg_bldg_nm', 'varchar(40)', '', '건축물대장건물명'),
               ('dtl_bldg_nm', 'varchar(100)', '', '상세건물명'),
               ('sgg_bldg_nm', 'varchar(40)', '', '시군구용건물명'),
               ('aptcpx_yn', 'varchar(1)', '', ''),
               ('dong_nm', 'varchar(40)', '', '행정동명 · 참고용'),
               ('stts', 'varchar(1)', '', '0 유효 1 폐지')]),
 'unit': ('unit · 상세위치',
          [('src', 'varchar(1)', 'PK', 'S 시군구용 L 대장'),
           ('sgg_cd', 'varchar(5)', 'PK', ''),
           ('blk_sn', 'bigint', 'PK', '동일련번호'),
           ('flr_sn', 'bigint', 'PK', '층일련번호'),
           ('ho_sn', 'bigint', 'PK', '호일련번호'),
           ('ho_sfx_sn', 'bigint', 'PK', '호접미사일련번호'),
           ('blk_nm', 'varchar(50)', '', '동명칭'),
           ('flr_nm', 'varchar(50)', '', '층명칭'),
           ('ho_nm', 'varchar(50)', '', '호명칭'),
           ('udgd_se', 'varchar(1)', '', ''),
           ('bldg_mng_no', 'varchar(25)', '', '건물 연계키')]),
 'unit_lookup': ('unit_lookup · 상세주소찾기 (파생)',
                 [('road_nm_addr_mng_no', 'varchar(26)', 'PK', ''),
                  ('blk_nm', 'varchar(50)', 'PK', '빈 문자열 허용'),
                  ('flr_nm', 'varchar(50)', 'PK', '빈 문자열 허용'),
                  ('ho_nm', 'varchar(50)', 'PK', '빈 문자열 허용'),
                  ('udgd_se', 'varchar(1)', 'PK', ''),
                  ('bldg_mng_no', 'varchar(25)', '', 'NOT NULL'),
                  ('src', 'varchar(1)', '', 'S 또는 L')]),
 'config': ('config · 설정',
            [('stng_idntfr', 'bigint', 'PK', 'IDENTITY'),
             ('prm_typo_nmtm', 'smallint', '', '[물리명 확인 필요]'),
             ('cand_uplmt', 'smallint', '', '[물리명 확인 필요]'),
             ('page_sz', 'smallint', '', '[물리명 확인 필요]'),
             ('aply_dt', 'timestamptz', '', 'DEFAULT now()')]),
 'request': ('request · 정제요청',
             [('dmnd_idntfr', 'bigint', 'PK', 'IDENTITY'),
              ('addr_vl', 'text', '', 'NOT NULL'),
              ('orgnl_dmnd', 'jsonb', '', '원본 요청'),
              ('strtg_se', 'varchar(1)', '', 'C 교정 D 검출'),
              ('stng_idntfr', 'bigint', 'FK', ''),
              ('rcpt_dt', 'timestamptz', '', 'DEFAULT now()')]),
 'result': ('result · 정제결과',
            [('dmnd_idntfr', 'bigint', 'PK FK', ''),
             ('bldg_mng_no', 'varchar(25)', '', '제약 없음'),
             ('cfmtn_blk', 'varchar(50)', '', '확정 동 · 값 복사'),
             ('cfmtn_flr', 'varchar(50)', '', '확정 층'),
             ('cfmtn_ho', 'varchar(50)', '', '확정 호'),
             ('bldg_jgmt', 'varchar(1)', '', '건물판정'),
             ('daddr_jgmt', 'varchar(1)', '', '상세판정'),
             ('rsn_cd', 'varchar(30)', '', '사유코드')]),
 'result_dropped': ('result_dropped · 버린조각',
                    [('dmnd_idntfr', 'bigint', 'PK FK', ''),
                     ('unsd_tkn_sn', 'smallint', 'PK', '조각순번'),
                     ('unsd_tkn', 'text', '', 'NOT NULL')]),
 'name_map': ('name_map · 이름대응',
              [('stp', 'smallint', 'PK', '1~4 행정구역 5 도로명'),
               ('bfr_nm', 'varchar(80)', 'PK', '옛 이름'),
               ('crsp_cd', 'varchar(12)', 'PK', '법정동코드 또는 도로명코드'),
               ('now_nm', 'varchar(80)', '', 'NOT NULL · 현재 이름'),
               ('obsrvn_ymd', 'date', '', 'NOT NULL · 처음 견준 날'),
               ('crt_src', 'varchar(1)', '', 'B 배치비교 P 과거연동')]),
 'addr_map': ('addr_map · 주소대응',
              [('bfr_road_nm_addr_mng_no', 'varchar(26)', 'PK', '옛 등록주소'),
               ('now_road_nm_addr_mng_no', 'varchar(26)', '', 'NOT NULL · 현재 등록주소'),
               ('bldg_mng_no', 'varchar(25)', '', 'NOT NULL · 이어 준 키'),
               ('obsrvn_ymd', 'date', '', 'NOT NULL'),
               ('crt_src', 'varchar(1)', '', 'B 배치비교 P 과거연동')])}

SCHEMA = {'region': 'ref',
 'road': 'ref',
 'token': 'ref',
 'road_emd': 'ref',
 'lot': 'ref',
 'address': 'ref',
 'address_lot': 'ref',
 'building': 'ref',
 'unit': 'ref',
 'unit_lookup': 'ref',
 'config': 'svc',
 'request': 'svc',
 'result': 'svc',
 'result_dropped': 'svc',
 'name_map': 'ref',
 'addr_map': 'ref'}

LOGICAL_TBL = {'region': '행정구역',
 'road': '도로명',
 'road_emd': '도로명읍면동',
 'lot': '지번',
 'address': '등록주소',
 'address_lot': '관련지번',
 'building': '건물',
 'unit': '상세위치',
 'unit_lookup': '상세주소찾기',
 'token': '주소표기',
 'config': '설정',
 'request': '정제요청',
 'result': '정제결과',
 'result_dropped': '버린조각',
 'name_map': '이름대응',
 'addr_map': '주소대응'}

LOGICAL = {'region': {'stdg_cd': '법정동코드', 'up_stdg_cd': '상위법정동코드', 'stp': '단계', 'admdst_nm': '행정구역명'},
 'road': {'road_nm_cd': '도로명코드', 'road_nm': '도로명', 'up_road_nm_no': '상위도로명번호', 'use_yn': '사용여부'},
 'road_emd': {'road_nm_cd': '도로명코드',
              'emd_sn': '읍면동일련번호',
              'emd_cd': '읍면동코드',
              'emd_se': '읍면동구분',
              'ancmnt_ymd': '고시일자'},
 'lot': {'stdg_cd': '법정동코드', 'mtn_yn': '산여부', 'mno': '지번본번', 'sno': '지번부번'},
 'address': {'road_nm_addr_mng_no': '도로명주소관리번호',
             'road_nm_cd': '도로명코드',
             'udgd_yn': '지하여부',
             'bmno': '건물본번',
             'bsno': '건물부번',
             'stdg_cd': '법정동코드',
             'zip': '기초구역번호',
             'aptcpx_se': '공동주택구분',
             'efctn_ymd': '효력발생일'},
 'address_lot': {'stdg_cd': '법정동코드',
                 'mtn_yn': '산여부',
                 'mno': '지번본번',
                 'sno': '지번부번',
                 'road_nm_addr_mng_no': '도로명주소관리번호'},
 'building': {'bldg_mng_no': '건물관리번호',
              'road_nm_addr_mng_no': '도로명주소관리번호',
              'rprs_stdg_cd': '대표지번법정동코드',
              'rprs_mtn_yn': '대표지번산여부',
              'rprs_mno': '대표지번본번',
              'rprs_sno': '대표지번부번',
              'bdrg_bldg_nm': '건축물대장건물명',
              'dtl_bldg_nm': '상세건물명',
              'sgg_bldg_nm': '시군구용건물명',
              'aptcpx_yn': '공동주택여부',
              'dong_nm': '행정동명',
              'stts': '상태'},
 'unit': {'src': '출처',
          'sgg_cd': '시군구코드',
          'blk_sn': '동일련번호',
          'flr_sn': '층일련번호',
          'ho_sn': '호일련번호',
          'ho_sfx_sn': '호접미사일련번호',
          'blk_nm': '동명칭',
          'flr_nm': '층명칭',
          'ho_nm': '호명칭',
          'udgd_se': '지하구분',
          'bldg_mng_no': '건물관리번호'},
 'unit_lookup': {'road_nm_addr_mng_no': '도로명주소관리번호',
                 'blk_nm': '동명칭',
                 'flr_nm': '층명칭',
                 'ho_nm': '호명칭',
                 'udgd_se': '지하구분',
                 'bldg_mng_no': '건물관리번호',
                 'src': '출처'},
 'token': {'tkn': '토큰', 'tkn_se': '토큰구분'},
 'config': {'stng_idntfr': '설정식별자', 'prm_typo_nmtm': '허용오타횟수', 'cand_uplmt': '후보상한', 'page_sz': '페이지크기',
            '허용오타횟수': '허용오타횟수',
            '후보상한': '후보상한',
            '페이지크기': '페이지크기',
            'aply_dt': '적용일시'},
 'request': {'dmnd_idntfr': '요청식별자',
             'addr_vl': '주소값',
             'orgnl_dmnd': '원본요청',
             'strtg_se': '전략구분',
             'stng_idntfr': '설정식별자',
             'rcpt_dt': '접수일시'},
 'result': {'dmnd_idntfr': '요청식별자',
            'bldg_mng_no': '건물관리번호',
            'cfmtn_blk': '확정동',
            'cfmtn_flr': '확정층',
            'cfmtn_ho': '확정호',
            'bldg_jgmt': '건물판정',
            'daddr_jgmt': '상세판정',
            'rsn_cd': '사유코드'},
 'result_dropped': {'dmnd_idntfr': '요청식별자', 'unsd_tkn_sn': '버린조각순번', 'unsd_tkn': '버린조각값'},
 'name_map': {'stp': '단계', 'bfr_nm': '전명', 'crsp_cd': '대응코드',
              'now_nm': '현재명', 'obsrvn_ymd': '관측일자', 'crt_src': '생성출처'},
 'addr_map': {'bfr_road_nm_addr_mng_no': '전도로명주소관리번호',
              'now_road_nm_addr_mng_no': '현재도로명주소관리번호',
              'bldg_mng_no': '건물관리번호', 'obsrvn_ymd': '관측일자',
              'crt_src': '생성출처'}}

HDR_H, ROW_H, W = 32, 26, 400
COL_W = (30, 132, 148, 90)
HDR = {"ref": "#1B2A4A", "svc": "#8A6A2B"}

POS = {
    "region": (40, 40), "lot": (600, 40), "address_lot": (1160, 40),
    "address": (600, 250), "unit_lookup": (1720, 250), "building": (1160, 350),
    "unit": (1720, 520), "road": (40, 560), "road_emd": (600, 560),
    "token": (40, 760),
    "config": (40, 1000), "request": (600, 1000), "result": (1160, 1000),
    "result_dropped": (1720, 1000),
    "name_map": (40, 1400), "addr_map": (1720, 1250),
}

# 관계 — (부모, 부모칼럼, 자식, 자식칼럼, 종류, 부모개수, 나감, 들어옴, 배선기둥)
#   종류 id 식별 · nonid 비식별 · loose 제약 없음
#   부모개수 one 필수 하나 · zero 선택 하나 · only 하나 대 하나
#   배선기둥 None이면 곧은 직선이다
EDGES = [
    ("region", "stdg_cd", "lot", "stdg_cd", "id", "one", "E", "W", None),
    ("lot", "stdg_cd", "address_lot", "stdg_cd", "id", "one", "E", "W", None),
    ("road", "road_nm_cd", "road_emd", "road_nm_cd", "id", "one", "E", "W", None),
    ("address", "road_nm_addr_mng_no", "unit_lookup", "road_nm_addr_mng_no",
     "id", "one", "E", "W", None),
    ("request", "dmnd_idntfr", "result", "dmnd_idntfr", "id", "only", "E", "W", None),
    ("result", "dmnd_idntfr", "result_dropped", "dmnd_idntfr", "id", "one", "E", "W", None),

    ("region", "stdg_cd", "region", "up_stdg_cd", "nonid", "zero", "W", "W", 0),
    ("region", "stdg_cd", "address", "stdg_cd", "nonid", "one", "E", "W", 500),
    ("road", "road_nm_cd", "address", "road_nm_cd", "nonid", "one", "E", "W", 540),
    ("lot", "stdg_cd", "building", "rprs_stdg_cd", "nonid", "zero", "E", "W", 1060),
    ("address", "road_nm_addr_mng_no", "address_lot", "road_nm_addr_mng_no",
     "id", "one", "E", "W", 1100),
    ("address", "road_nm_addr_mng_no", "building", "road_nm_addr_mng_no",
     "nonid", "zero", "E", "W", 1020),
    ("building", "bldg_mng_no", "unit", "bldg_mng_no", "nonid", "one", "E", "W", 1620),
    ("building", "bldg_mng_no", "unit_lookup", "bldg_mng_no", "nonid", "one",
     "E", "W", 1660),
    ("config", "stng_idntfr", "request", "stng_idntfr", "nonid", "one", "E", "W", 500),
    ("result", "bldg_mng_no", "building", "bldg_mng_no", "loose", "zero", "W", "W", 1100),

    ("region", "stdg_cd", "name_map", "crsp_cd", "loose", "zero", "W", "W", -60),
    ("road", "road_nm_cd", "name_map", "crsp_cd", "loose", "zero", "W", "W", -110),
    ("address", "road_nm_addr_mng_no", "addr_map", "now_road_nm_addr_mng_no",
     "loose", "zero", "E", "W", 1120),
    ("building", "bldg_mng_no", "addr_map", "bldg_mng_no", "loose", "zero", "E", "W", 1660),
]

SIDE = {"W": 0, "E": 1}
START = {"one": "ERone", "zero": "ERzeroToOne", "only": "ERone"}
END = {"one": "ERmany", "zero": "ERmany", "only": "ERone"}
LINE = {
    "id": ("#2B4C8C", 2, ""),
    "nonid": ("#2B4C8C", 1, "dashed=1;dashPattern=8 4;"),
    "loose": ("#8A8A8A", 1, "dashed=1;dashPattern=2 4;"),
}

TBL = ("shape=table;startSize={h};container=1;collapsible=0;childLayout=tableLayout;"
       "fixedRows=1;rowLines=0;columnLines=1;html=1;whiteSpace=wrap;align=center;"
       "fontStyle=1;fontSize=13;resizeLast=1;fillColor={f};fontColor=#FFFFFF;"
       "strokeColor={f};")
ROW = ("shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;"
       "fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];"
       "portConstraint=eastwest;top=0;left=0;right=0;bottom=0;")
CELL = ("shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;"
        "right=0;overflow=hidden;whiteSpace=wrap;html=1;align={al};spacingLeft={sl};"
        "spacingRight=4;fontSize=11;{extra}")
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jumpStyle=arc;jumpSize=8;"
        "exitX={ex};exitY=0.5;exitDx=0;exitDy=0;entryX={nx};entryY=0.5;entryDx=0;"
        "entryDy=0;startArrow={sa};startFill=0;endArrow={ea};endFill=0;"
        "strokeColor={sc};strokeWidth={sw};{dash}")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def cols_of(key):
    return TABLES[key][1]


def row_index(key, col):
    for i, (c, _t, _k, _n) in enumerate(cols_of(key), 1):
        if c == col:
            return i
    raise KeyError(f"{key}.{col}")


def row_center_y(key, col):
    x, y = POS[key]
    return y + HDR_H + ROW_H * (row_index(key, col) - 1) + ROW_H // 2


def box_edge_x(key, side):
    x, _y = POS[key]
    return x + (W if side == "E" else 0)


def build():
    o = ['<mxfile host="app.diagrams.net">',
         '  <diagram name="물리 ERD">',
         '    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" '
         'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
         'pageWidth="2400" pageHeight="1500" math="0" shadow="0">',
         '      <root>',
         '        <mxCell id="0" />',
         '        <mxCell id="1" parent="0" />']

    o.append('        <mxCell id="title" value="주소정제 솔루션 — 물리 ERD    '
             'PostgreSQL · 테이블 열일곱 · 관계 스물하나" '
             'style="text;html=1;align=left;verticalAlign=middle;fontSize=22;'
             'fontStyle=1;fontColor=#1B2A4A;" vertex="1" parent="1">')
    o.append('          <mxGeometry x="40" y="-40" width="900" height="40" as="geometry" />')
    o.append('        </mxCell>')

    legend = ("읽는 법 &#10;"
              "굵은 실선 = 식별 관계 &#160;·&#160; 점선 = 비식별 관계 &#160;·&#160; "
              "회색 잔점선 = 제약 없는 참조&#10;"
              "선은 외래키 제약을 뜻하지 않는다. svc 안쪽 셋만 실제 제약이다&#10;"
              "한 줄은 PK · 논리명 · 물리명 · 자료형 넷이다")
    o.append(f'        <mxCell id="legend" value="{legend}" '
             'style="text;html=1;align=left;verticalAlign=top;fontSize=12;'
             'fontColor=#444444;whiteSpace=wrap;" vertex="1" parent="1">')
    o.append('          <mxGeometry x="600" y="760" width="700" height="90" as="geometry" />')
    o.append('        </mxCell>')

    for key, (x, y) in POS.items():
        cols = cols_of(key)
        sch = SCHEMA[key]
        title = f"{sch}.{key} · {LOGICAL_TBL[key]}"
        h = HDR_H + ROW_H * len(cols)
        o.append(f'        <mxCell id="{key}" value="{esc(title)}" '
                 f'style="{TBL.format(h=HDR_H, f=HDR[sch])}" vertex="1" parent="1">')
        o.append(f'          <mxGeometry x="{x}" y="{y}" width="{W}" height="{h}" '
                 f'as="geometry" />')
        o.append('        </mxCell>')
        for i, (c, t, k, _n) in enumerate(cols, 1):
            rid = f"{key}_r{i}"
            o.append(f'        <mxCell id="{rid}" value="" style="{ROW}" vertex="1" '
                     f'parent="{key}">')
            o.append(f'          <mxGeometry y="{HDR_H + ROW_H * (i - 1)}" width="{W}" '
                     f'height="{ROW_H}" as="geometry" />')
            o.append('        </mxCell>')
            key_mark = "PK" if "PK" in k else ("FK" if "FK" in k else "")
            parts = [(key_mark, "center", 4, "fontColor=#2B4C8C;fontStyle=1;"),
                     (LOGICAL[key].get(c, c), "left", 6,
                      "fontStyle=1;" if key_mark else ""),
                     (c, "left", 6, "fontColor=#333333;"),
                     (t, "left", 6, "fontColor=#888888;")]
            cx = 0
            for j, ((val, al, sl, extra), cw) in enumerate(zip(parts, COL_W), 1):
                o.append(f'        <mxCell id="{rid}c{j}" value="{esc(val)}" '
                         f'style="{CELL.format(al=al, sl=sl, extra=extra)}" '
                         f'vertex="1" parent="{rid}">')
                o.append(f'          <mxGeometry x="{cx}" width="{cw}" height="{ROW_H}" '
                         f'as="geometry"><mxRectangle width="{cw}" height="{ROW_H}" '
                         f'as="alternateBounds" /></mxGeometry>')
                o.append('        </mxCell>')
                cx += cw

    straight = 0
    for n, (p, pc, c, cc, kind, card, es, ns, lane) in enumerate(EDGES, 1):
        sc, sw, dash = LINE[kind]
        st = EDGE.format(ex=SIDE[es], nx=SIDE[ns], sa=START[card], ea=END[card],
                         sc=sc, sw=sw, dash=dash)
        o.append(f'        <mxCell id="e{n}" style="{st}" edge="1" parent="1" '
                 f'source="{p}_r{row_index(p, pc)}" target="{c}_r{row_index(c, cc)}">')
        y1, y2 = row_center_y(p, pc), row_center_y(c, cc)
        if lane is None:
            straight += 1
            o.append('          <mxGeometry relative="1" as="geometry" />')
        else:
            o.append('          <mxGeometry relative="1" as="geometry">')
            o.append('            <Array as="points">')
            o.append(f'              <mxPoint x="{lane}" y="{y1}" />')
            o.append(f'              <mxPoint x="{lane}" y="{y2}" />')
            o.append('            </Array>')
            o.append('          </mxGeometry>')
        o.append('        </mxCell>')

    o += ['      </root>', '    </mxGraphModel>', '  </diagram>', '</mxfile>']
    print(f"곧은 직선 {straight} · 꺾은 선 {len(EDGES) - straight}")
    return "\n".join(o)


if __name__ == "__main__":
    open("erd-physical.drawio", "w", encoding="utf-8").write(build() + "\n")
    print("erd-physical.drawio")
