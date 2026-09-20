# -*- coding: utf-8 -*-
"""ref·svc 테이블 정의서와 인덱스 정의서를 찍는다. gen_std_dict.py의 재료를 그대로 쓴다."""
import csv, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)   # 저장소 뿌리
OUT  = os.path.join(BASE, "design", "standard-dict")
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "gen_std_dict.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

# 필수 여부가 기본키로 안 정해지는 자리만 적는다
NOTE = {
 ('ref.building','road_nm_addr_mng_no'): 'NOT NULL을 걸지 않는다. 동 표시에 없는 건물이 서울 230채다',
 ('ref.unit_lookup','flr_nm'): '빈 값은 빈 문자열이다. NULL이 아니다. 기본키 칼럼이라 NULL을 못 받는다',
 ('ref.unit_lookup','ho_nm'): '빈 값은 빈 문자열이다',
 ('svc.result_dropped','unsd_tkn'): 'NOT NULL',
 ('svc.result','cfmtn_blk'): '값 복사. 상세위치를 참조하지 않는다',
 ('svc.result','cfmtn_flr'): '값 복사',
 ('svc.result','cfmtn_ho'): '값 복사',
 ('svc.request','orgnl_dmnd'): '감사 기록. 조회하지 않는다',
 ('svc.load_run','excn_rslt'): '시작할 때 「도는중」으로 넣고 끝날 때 갱신한다',
 ('svc.load_file','ctpv_nm'): '전국 파일 한 세트면 빈다',
 ('svc.load_file','excl_rsn_cd'): '처리결과가 「제외」일 때만 찬다',
}
FK = {
 ('svc.request','stng_idntfr'): 'svc.config',
 ('svc.result','dmnd_idntfr'): 'svc.request',
 ('svc.result_dropped','dmnd_idntfr'): 'svc.result',
 ('svc.load_file','load_excn_idntfr'): 'svc.load_run',
}

INDEX = [
 ('ix_address_road4','ref.address','road_nm_cd, udgd_yn, bmno, bsno','stdg_cd','4칸 묶음 조회 · 역조회','유일 인덱스로 걸지 않는다. 전국 10건이 겹친다'),
 ('ix_address_stdg','ref.address','stdg_cd','','시군구로 좁히기',''),
 ('ix_building_addr','ref.building','road_nm_addr_mng_no','','등록주소 → 건물 목록',''),
 ('ix_building_replot','ref.building','rprs_stdg_cd, rprs_mtn_yn, rprs_mno, rprs_sno','','대표지번 갈래',''),
 ('pk_address_lot','ref.address_lot','기본키','','관련지번 갈래','별도 인덱스가 필요 없다'),
 ('pk_unit_lookup','ref.unit_lookup','기본키','','동·층·호 조회 · 자리 단위 삭제',''),
 ('ix_unit_bldg','ref.unit','bldg_mng_no','','건물 → 상세위치',''),
 ('ix_token_se','ref.token','tkn_se, tkn','','사전 적재',''),
 ('pk_addr_map','ref.addr_map','기본키','','옛 자리 → 새 자리','실재 확인이 후보를 다 지운 뒤에만 친다'),
 ('ix_name_map_cd','ref.name_map','crsp_cd','','대응 비교가 코드로 기존 줄을 찾는다','옛 이름 조회는 메모리 사전이 받는다'),
 ('ix_token_prefix','ref.token','tkn varchar_pattern_ops','','접두사 비교',"기본 인덱스는 LIKE '강남%'를 안 탄다. 콜레이션 때문이다"),
 ('(인덱스)','svc.load_run','기본키','','실행 조회','더 만들지 않는다. 하루 한 줄이라 스캔이 싸다'),
 ('(부분 인덱스)','ref.building',"WHERE stts = '0'",'','유효 건물만','만들지 않는다. 폐지 비율을 재기 전까지는 값이 안 나온다'),
]

CONSTRAINT = [
 ('ref 안쪽','외래키','걸지 않는다','자료마다 담는 범위와 배포 단위가 다르다. 적재 배치가 대사하고 지표로 남긴다'),
 ('svc 안쪽','외래키','건다','우리가 만드는 자료라 무결성을 우리가 책임진다'),
 ('svc → ref','외래키','걸지 않는다','참조 마스터가 배치로 통째로 갈린다'),
 ('전체','CHECK','건다','길이와 코드값 집합은 원천이 무엇을 주든 우리가 아는 사실이다'),
 ('ref.unit_lookup · ref.address_lot · ref.unit','autovacuum','고정 건수 5만','기본 비율 20%는 432만 줄에서 스물두 달치가 쌓여야 돈다'),
 ('전체','분할','하지 않는다','서울 규모에서 값을 안 한다. 전국 확장 때 다시 연다'),
]

def main():
    rows = g.fix(g.read_columns())
    by_abbr, term = g.load()
    for sch in ('ref', 'svc'):
        out = []
        seq = {}
        for r in rows:
            if r['schema'] != sch: continue
            seq[r['tbl']] = seq.get(r['tbl'], 0) + 1
            k = r['key'] or ''
            if (r['tbl'], r['en']) in FK and 'FK' not in k:
                k = (k + ' · FK' if k else 'FK')
            out.append([r['tbl'], r['tbl_ko'], seq[r['tbl']], r['ko'], r['en'],
                        r['typ'], k, FK.get((r['tbl'], r['en']), ''),
                        '필수' if 'PK' in (r['key'] or '') else '',
                        NOTE.get((r['tbl'], r['en']), '')])
        g.write(f'{sch}테이블정의서.csv',
                ['테이블 물리명','테이블 논리명','순서','칼럼 논리명','칼럼 물리명',
                 '저장형식','키','참조 대상','필수','비고'], out)
        print(f'{sch}: 테이블 {len(set(x[0] for x in out))} · 칼럼 {len(out)}')
    g.write('인덱스정의서.csv',
            ['인덱스명','테이블','칼럼','INCLUDE','무엇을 받나','비고'],
            [list(x) for x in INDEX])
    g.write('제약정의서.csv',
            ['대상','종류','건다/안 건다','근거'], [list(x) for x in CONSTRAINT])
    print(f'인덱스 {len(INDEX)} · 제약 {len(CONSTRAINT)}')

if __name__ == '__main__':
    main()
