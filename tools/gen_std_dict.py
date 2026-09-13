# -*- coding: utf-8 -*-
"""표준 사전 넷을 찍는다. erd-physical.drawio와 행정안전부 표준 사전 둘을 읽는다."""
import csv, os, re, html, glob, collections
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 저장소 뿌리
OUT  = os.path.join(BASE, "design", "standard-dict")
os.makedirs(OUT, exist_ok=True)
WORD = glob.glob(os.path.join(BASE, "reference", "*공통표준단어*.csv"))[0]
TERM = glob.glob(os.path.join(BASE, "reference", "*공통표준용어*.csv"))[0]
DRAW = os.path.join(BASE, "design", "erd-physical.drawio")

def read_columns():
    t = ET.parse(DRAW); cells = {}; order = []
    for c in t.getroot().iter('mxCell'):
        cells[c.get('id')] = c; order.append(c.get('id'))
    def txt(v):
        return html.unescape(re.sub(r'<[^>]+>', '', v)).strip() if v else ''
    def y(i):
        g = cells[i].find('mxGeometry'); return float(g.get('y') or 0) if g is not None else 0
    def x(i):
        g = cells[i].find('mxGeometry'); return float(g.get('x') or 0) if g is not None else 0
    rows = []
    for ti in [i for i in order if 'shape=table' in (cells[i].get('style') or '')]:
        tname = txt(cells[ti].get('value'))
        phys, logi = [s.strip() for s in tname.split('.', 0)] if False else (
            tname.split('·')[0].strip(), tname.split('·')[1].strip() if '·' in tname else '')
        rs = [i for i in order if cells[i].get('parent') == ti and 'tableRow' in (cells[i].get('style') or '')]
        for ri in sorted(rs, key=y):
            cs = sorted([i for i in order if cells[i].get('parent') == ri], key=x)
            v = [txt(cells[i].get('value')) for i in cs]
            rows.append(dict(schema=phys.split('.')[0], tbl=phys, tbl_ko=logi,
                             key=v[0], ko=v[1], en=v[2], typ=v[3]))
    return rows

RENAME = {'rep': 'rprs', 'cfg': 'stng'}
FILL = {'허용오타횟수': 'prm_typo_nmtm', '후보상한': 'cand_uplmt', '페이지크기': 'page_sz'}

def fix(rows):
    for r in rows:
        if r['ko'] in FILL:
            r['en'] = FILL[r['ko']]
        r['en'] = '_'.join(RENAME.get(p, p) for p in r['en'].split('_'))
    return rows

NEW_WORDS = [
    ('동(棟)', 'Block',               'BLK',  '표준에 「아파트 동」 뜻의 홑글자가 없다. DONG은 표준용어 행정동명·행정동코드가 이미 쓴다'),
    ('호',     'Ho',                  'HO',   '등재 없음'),
    ('접미사', 'Suffix',              'SFX',  '등재 없음. 영어 관용 축약을 쓴다'),
    ('전',     'Before',              'BFR',  '등재 없음. 표준단어 「이전 = BFR」의 축약을 빌린다'),
    ('오타',   'Typographical Error', 'TYPO', '등재 없음. 표준 3,284개에서 TYPO는 비어 있다'),
    ('후보',   'Candidate',           'CAND', '등재 없음. 「후보자 = CNDD」·「조건 = CND」와 겹치지 않는다'),
]
NEW_ABBR = {w[2]: w for w in NEW_WORDS}

SUFFIX_RULE = [
    ('일련번호', '일련번호'), ('식별자', '식별자'), ('관리번호', '번호'),
    ('코드', '코드'), ('명칭', '명'), ('이름', '명'), ('명', '명'),
    ('여부', '여부'), ('구분', '구분'), ('번호', '번호'),
    ('일자', '일자'), ('일시', '일시'), ('순번', '순번'),
    ('횟수', '수'), ('상한', '수'), ('크기', '수'),
    ('본번', '수'), ('부번', '수'), ('단계', '수'),
    ('값', '값'), ('표기', '명'), ('토큰', '명'),
    ('출처', '구분'), ('상태', '구분'), ('판정', '구분'),
    ('연월', '연월'), ('결과', '구분'),
]

def domain_of(ko, typ):
    cls = None
    for suf, c in SUFFIX_RULE:
        if ko.endswith(suf):
            cls = c; break
    if cls is None:
        cls = {'text': '내용', 'jsonb': '문서', 'date': '일자', 'timestamptz': '일시',
               'bigint': '수', 'integer': '수', 'smallint': '수'}.get(typ, '명')
    m = re.match(r'varchar\((\d+)\)', typ)
    if m: return f"{cls}V{m.group(1)}"
    if typ in ('smallint', 'integer', 'bigint'): return f"{cls}N"
    if typ == 'date': return "일자D8"
    if typ == 'timestamptz': return "일시D"
    if typ == 'text': return "내용T"
    if typ == 'jsonb': return "문서J"
    return cls

def load():
    w = list(csv.reader(open(WORD, encoding='utf-8-sig')))[1:]
    t = list(csv.reader(open(TERM, encoding='utf-8-sig')))[1:]
    by_abbr = {}
    for r in w:
        by_abbr.setdefault(r[1].upper(), r)
    return by_abbr, {r[0] for r in t}

def write(path, header, rows):
    with open(os.path.join(OUT, path), 'w', newline='', encoding='utf-8-sig') as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)
    return rows

RSN_ROWS = [
 ('NOT_AN_ADDRESS','관문','입력 오류','실패','사전에서 찾은 조각이 하나도 없다','03-pipeline 0-1절 관문 · 4절'),
 ('SIDO_NOT_FOUND','파서 · 계층 조회','입력 오류','실패','시·도 자리를 못 맞췄다','03-pipeline 2절 상태 전이표'),
 ('SGG_NOT_FOUND','계층 조회','입력 오류','실패','시·군·구 자리를 못 맞췄다','03-pipeline 2절 상태 전이표'),
 ('ROAD_TOKEN_NOT_FOUND','파서','입력 오류','실패','시군구·행정구·읍면 뒤 조각이 어느 사전에도 안 걸렸다','03-pipeline 2절 상태 전이표'),
 ('ROAD_NAME_NOT_FOUND','역조회','입력 오류','실패','그 이름의 도로명이 전국에 없다','03-pipeline 4-2-1절'),
 ('BLDG_NO_NOT_FOUND','도로명 갈래','입력 오류','실패','도로명은 있으나 그 건물번호가 없다','03-pipeline 2절 · 4-2-1절'),
 ('BLDG_NO_NOT_FOUND_NATIONWIDE','역조회','입력 오류','실패','도로명은 있으나 그 번지가 어디에도 없다','03-pipeline 4-2-1절'),
 ('JIBUN_NOT_FOUND','지번 갈래','입력 오류','실패','법정동 뒤 지번을 못 맞췄다','03-pipeline 2절 상태 전이표'),
 ('ADMIN_DONG_USED','행정동 판정','참조 데이터 없음','실패','행정동으로 쓰였고 법정동 대응표가 없다. A3의 응답 코드다','03-pipeline 0-1절 행정동'),
 ('SGG_AMBIGUOUS','역조회','정보 부족','후보 여럿','시군구 후보가 2~10이다. 검출 전략이 목록을 다 적는다','03-pipeline 4-2-1절'),
 ('SGG_TOO_MANY','역조회','정보 부족','후보 여럿','시군구 후보가 11 이상이다. 목록을 비우고 개수만 낸다','03-pipeline 4-2-1절'),
 ('BLDG_NAME_TOO_MANY','건물이름 갈래','정보 부족','후보 여럿','건물 이름 후보가 상한 열을 넘었다. 목록을 비우고 개수만 낸다','03-pipeline 2절 ② 조회'),
 ('SGG_INFERRED','역조회','정보 부족','확인 권장','도로명과 건물번호로 시·군·구를 채웠다','03-pipeline 4절 · 4-2-1절'),
 ('UNIT_TOKEN_RESTORED','인덱스 기반 끊기','입력 오류','확인 권장','단위 표기가 빠진 조각을 인덱스가 복원했다. A1의 응답 코드다','03-pipeline 4절 · 2절 ①-2'),
 ('LEGACY_NAME_MAPPED','이름 대응 사전','입력 오류','확인 권장','옛 표기를 지금 표기로 갈아 끼웠다. A4·A5의 응답 코드다','03-pipeline 4절 · 8-7절'),
 ('TYPO_CORRECTED','파서','입력 오류','확인 권장','자모 거리 안의 닮은 이름으로 고쳐 읽었다. A2의 응답 코드다','03-pipeline 2절 ① 파싱'),
 ('PART_DISCARDED','합치기','입력 오류','확인 권장','자리를 정하는 데 안 쓴 조각이 있다. 무엇을 버렸는지는 값으로 적는다','03-pipeline 4절'),
]

CODE_ROWS = [
 ('mtn_yn','ref.lot · ref.building','산여부','지번 앞에 홑글자 「산」이 있는가','0 대지 · 1 산','varchar(1)','두 값으로 닫힌다. 원천 문자를 그대로 받는다','도로명주소법 시행령 제56조①'),
 ('udgd_yn','ref.address','지하여부','건물번호 앞에 지하 표시가 있는가','0 지상 · 1 지하 · 2 공중 · 3 수상','varchar(1)','원천 문자를 그대로 받는다','원천'),
 ('udgd_se','ref.unit · ref.unit_lookup','지하구분','상세위치가 지하인가','0 일반 · 1 지하','varchar(1)','두 값으로 닫힌다. 원천 문자를 그대로 받는다','원천'),
 ('aptcpx_se','ref.address','공동주택구분','등록주소가 공동주택 자리인가','원천 코드값을 그대로 받는다','varchar(1)','원천이 값을 더하면 그대로 들어온다','원천'),
 ('aptcpx_yn','ref.building','공동주택여부','건물이 공동주택인가','0 비공동주택 · 1 공동주택','varchar(1)','두 값으로 닫힌다. 어느 법 기준인지는 [확인 필요]','원천'),
 ('emd_se','ref.road_emd','읍면동구분','도로명이 걸친 자리가 어느 단계인가','2 = 미부여. 나머지 값은 [확인 필요]','varchar(1)','원천이 정한다','원천'),
 ('use_yn','ref.road','사용여부','도로명을 지금 쓰는가','전량 0으로 온다. 0이 사용이다','varchar(1)','원천이 정한다','원천'),
 ('stts','ref.building','상태','건물이 살아 있는가 폐지됐는가','0 사용 · 1 폐지','varchar(1)','규약의 예외다. 원천 use_yn과 같은 뜻이라 같은 문자를 쓴다','우리'),
 ('stp','ref.region','단계','법정동코드 10자리에서 어디까지 채워졌는가','1 시도 · 2 시군구 · 3 읍면동 · 4 리','smallint','smallint라 문자가 아니다. ref.name_map은 5 도로명을 더 쓴다','우리'),
 ('src','ref.unit · ref.unit_lookup','출처','상세주소를 어느 배포본에서 읽었는가','S 시군구용 · L 건축물대장','varchar(1)','상세주소DB는 시군구용과 같은 자료라 값이 아니다. 배포본이 늘면 값이 는다','우리'),
 ('tkn_se','ref.token','토큰구분','이 이름이 어느 표기 갈래에 속하는가','R 도로명 · J 지번 · B 건물이름 · H 행정동','varchar(1)','표기 갈래가 늘면 값이 는다','우리'),
 ('crt_src','ref.name_map · ref.addr_map','생성출처','이 대응을 무엇이 만들었는가','B 배치비교 · P 과거연동 · E 외부조회','varchar(1)','만드는 경로가 늘면 값이 는다. svc.legacy_map은 idnty_src를 따로 쓴다','우리'),
 ('strtg_se','svc.request','전략구분','어느 API 진입점으로 들어왔는가','C 교정 · D 검출','varchar(1)','진입점이 늘면 값이 는다. 하나로 합치지 않는다','우리'),
 ('bldg_jgmt','svc.result','건물판정','남은 건물 후보가 몇이고 버린 조각이 있는가','C 확실한 성공 · R 확인 권장 · M 후보 여럿 · F 실패 · S 수정 제안','varchar(1)','등급은 후보 수가 정한다. 조건이 늘어도 사유 쪽에 값을 더하고 등급은 늘리지 않는다','우리'),
 ('daddr_jgmt','svc.result','상세판정','동·층·호를 하나로 좁혔는가','C 확정 · E 미입력 · M 불일치 · R 확인 권장 · N 해당 없음','varchar(1)','미입력은 사용자가 안 쓴 것이고 해당 없음은 건물에 상세주소가 없는 것이라 글자를 갈랐다','우리'),
 ('rsn_cd','svc.result','사유코드','고칠 방향을 무엇으로 주는가','열일곱. 목록은 사유코드정의서가 든다','varchar(30)','더하는 것은 열려 있다. 빼는 것은 과거 줄이 뜻을 잃으므로 설계로 돌아온다','우리'),
 ('btch_se','svc.load_run','배치구분','어느 배치로 부른 실행인가','I 최초적재 · D 일반영 · M 월대사 · P 과거연동','varchar(1)','배치가 늘면 값이 는다','우리'),
 ('data_se','svc.load_run','자료구분','받은 폴더가 전체분인가 변동분인가','F 전체분 · C 변동분','varchar(1)','폴더 이름 full·changes와 같은 글자다. 두 값으로 닫힌다','원천'),
 ('clot_se','svc.load_run','호출구분','사람이 불렀는가 자동으로 돌았는가','A 자동 · M 수동','varchar(1)','두 값으로 닫힌다','우리'),
 ('excn_rslt','svc.load_run','실행결과','실행이 어떻게 끝났는가','R 도는중 · S 성공 · F 실패','varchar(1)','「도는중」이 값이라 같은 폴더를 동시에 두 번 넣는 것을 막는다','우리'),
 ('load_trgt_se','svc.load_file','적재대상구분','적재 대상 일곱 중 어느 자료인가','B 건물정보 · R 도로명코드 · A 도로명주소한글 · J 관련지번 · S 상세주소표시(시군구용) · L 상세주소표시(건축물대장) · D 상세주소동표시','varchar(1)','S와 L은 ref.unit.src와 일부러 맞췄다. 적재 대상이 늘면 값이 늘고 제외한 파일에서는 빈다','우리'),
 ('excl_rsn_cd','svc.load_file','제외사유코드','왜 적재하지 않았는가','NOT_TARGET 적재대상아님 · REFERENCE 근거자료 · UNKNOWN 모르는파일','varchar(10)','문자가 아니라 이름이다. 더하는 것은 열려 있고 처리결과가 「제외」일 때만 찬다','우리'),
 ('prcs_rslt','svc.load_file','처리결과','파일 한 줄이 어떻게 끝났는가','S 성공 · F 실패 · E 제외','varchar(1)','성공·실패는 excn_rslt와 같은 글자다. 제외가 값으로 선다','우리'),
 ('idnty_src','svc.legacy_map','규명출처','옛 표기와 등록주소를 무엇으로 이었는가','E 외부조회 · I 내부판정','varchar(1)','E는 crt_src의 외부조회와 같은 글자다. 규명 수단이 늘면 값이 는다','우리'),
]

def main():
    rows = fix(read_columns())
    by_abbr, term_names = load()

    frag = collections.Counter(p for r in rows for p in r['en'].split('_'))
    wrows = []
    for p, n in sorted(frag.items(), key=lambda x: (-x[1], x[0])):
        A = p.upper()
        if A in NEW_ABBR:
            k, en, ab, memo = NEW_ABBR[A]
            wrows.append([k, en, ab, '프로젝트 신규', '', n, memo])
        elif A in by_abbr:
            r = by_abbr[A]
            wrows.append([r[0], r[2], r[1], '공통표준단어', r[5], n, ''])
        else:
            wrows.append([p, '', A, '[확인 필요]', '', n, '표준 사전에서 못 찾았다'])
    write('표준단어정의서.csv',
          ['표준단어명','영문명','영문약어명','출처','표준도메인분류','쓰인 칼럼 수','비고'], wrows)

    dom = collections.Counter(); dtyp = {}
    for r in rows:
        d = domain_of(r['ko'], r['typ']); dom[d] += 1; dtyp[d] = r['typ']
    drows = []
    for d, n in sorted(dom.items(), key=lambda x: (-x[1], x[0])):
        t = dtyp[d]; m = re.match(r'varchar\((\d+)\)', t)
        drows.append([d, re.sub(r'[A-Z].*$', '', d), t,
                      f"{m.group(1)}자리 이내 문자" if m else
                      {'smallint':'정수 5자리','integer':'정수 10자리','bigint':'정수 19자리',
                       'date':'YYYY-MM-DD','timestamptz':'YYYY-MM-DD HH:MM:SS+TZ',
                       'text':'길이 제한 없는 문자','jsonb':'JSON 문서'}.get(t, t), n])
    write('표준도메인정의서.csv',
          ['표준도메인명','도메인분류','저장형식(PostgreSQL)','표현형식','쓰인 칼럼 수'], drows)

    trows = []
    for r in rows:
        combo = ' + '.join(
            (NEW_ABBR[p.upper()][0] if p.upper() in NEW_ABBR else
             by_abbr[p.upper()][0] if p.upper() in by_abbr else f'[{p}]')
            for p in r['en'].split('_'))
        trows.append([r['schema'], r['tbl'], r['tbl_ko'], r['key'], r['ko'], r['en'],
                      domain_of(r['ko'], r['typ']), r['typ'], combo,
                      '공통표준용어' if r['ko'] in term_names else '표준단어 조합'])
    write('표준용어정의서.csv',
          ['스키마','테이블 물리명','테이블 논리명','키','표준용어명(논리명)',
           '영문약어명(물리명)','표준도메인명','저장형식','단어 조합','출처'], trows)

    write('표준코드정의서.csv',
          ['코드칼럼','소속 테이블','코드명','구분 기준','값의 범위','형식','확장 규칙','값을 정하는 주체'],
          [list(x) for x in CODE_ROWS])

    write('사유코드정의서.csv',
          ['사유코드','내는 자리','사유 종류','등급','뜻','근거'],
          [list(x) for x in RSN_ROWS])
    return rows, wrows, drows, trows

if __name__ == '__main__':
    rows, w, d, t = main()
    print(f"칼럼 {len(rows)} · 단어 {len(w)} · 도메인 {len(d)} · 용어 {len(t)} · 코드 {len(CODE_ROWS)} · 사유코드 {len(RSN_ROWS)}")
    print("확인 필요 단어:", [x[0] for x in w if x[3] == '[확인 필요]'] or "없음")
    print("신규 단어:", [x[0] for x in w if x[3] == '프로젝트 신규'])
