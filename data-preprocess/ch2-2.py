# ch2-2.py
import pandas as pd
import numpy as np
import cx_Oracle      # Oracle DB 연동을 위한 cx_Oracle 패키지 임포트

# 데이터로드 (ch2-2.csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap2/ch2-2(선박입출항).csv', encoding='CP949', engine='python')

# Oracle DB 연결
# 접속정보(connection string) : ID/PASS@CONNECTION_ALIAS
# CONNECTION_ALIAS : Oracle TNSNAMES.ORA 파일에 있는 접속정보 별칭(ALIAS)
conn_ora = cx_Oracle.connect("prep1/prep1@XE")

# DB 커서(Cursor) 선언
cur = conn_ora.cursor()

# 사용할 Oracle 소스 테이블명 지정
src_table = "d_base2_2"

# 데이터프레임(rawData)에 저장된 데이터를 Oracle 테이블(d_base2_2)에 입력하기 위한 로직
# d_base2_2 테이블 존재하는지 체크하는 함수
def table_exists(name=None, con=None):
    sql = "select table_name from user_tables where table_name='MYTABLE'".replace('MYTABLE', name.upper())
    df = pd.read_sql(sql, con)

    # 테이블이 존재하면 True, 그렇지 않으면 False 반환
    exists = True if len(df) > 0 else False
    return exists

# 테이블(d_base2_2) 생성 (테이블이 이미 존재한다면 TRUNCATE TABLE)
if table_exists(src_table, conn_ora):
    cur.execute("TRUNCATE TABLE " + src_table)
else:
    cur.execute("create table " + src_table + " ( \
               항만 varchar2(20) primary key, \
               입항선박수 number(5), \
               입항선박톤수 number(10), \
               출항선박수 number(5), \
               출항선박톤수 number(10))")

# Sequence 구조를 Dictionary 구조((element, value))로 변환하는 함수
# 예: ("Matt", 1) -> {'1':'Matt', '2':1}
# INSERT INTO ... VALUES (:1, :2, ...) 에서 바인드 변수값을 주기위해 Dictionary item 구조 사용
def convertSequenceToDict(list):
    dict = {}
    argList = range(1, len(list) + 1)
    for k, v in zip(argList, list):
        dict[str(k)] = v
    return dict

# 데이터프레임에 저장된 데이터를 Oracle 테이블로 입력(insert)
cols = [k for k in rawData.dtypes.index]
colnames = ','.join(cols)
colpos = ', '.join([':' + str(i + 1) for i, f in enumerate(cols)])
insert_sql = 'INSERT INTO %s (%s) VALUES (%s)' % (src_table, colnames, colpos)

# INSERT INTO ... VALUES (:1, :2, ...)의 바인드 변수 값을 저장하는 Dictionary 구조 생성
data = [convertSequenceToDict(rec) for rec in rawData.values]

# 바인드 변수와 Dictionary 데이터구조를 활용하여 Bulk Insertion 구현
cur.executemany(insert_sql, data)
conn_ora.commit()

# 평균값 평활화 (동일 너비 방식, 구간너비 : 500)
result_df = pd.read_sql("select 항만 \
                          , 입항선박수 \
                          , round(avg(입항선박수) over (partition by floor(입항선박수/500)), 0) 입항선박수_평활 \
                          , 출항선박수 \
                          , round(avg(출항선박수) over (partition by floor(출항선박수/500)), 0) 출항선박수_평활 \
                      from " + src_table, con=conn_ora)

# 결과보기(첫 10개행만 출력)
print(result_df.head(10))

# 중앙값 평활화 (동일 너비 방식, 구간너비 : 500)
# 입항선박수 중앙값을 구하는 뷰(view)
cur.execute("create or replace view 입항_median_view \
           as \
           select 항만 \
                , 입항선박수 \
                , bin_id /* 구간 id */ \
                , rnum /* 구간 내의 위치 */ \
                , floor((cnt + 1) / 2) med1 /* 구간의 중앙 위치(왼쪽) */ \
                , ceil((cnt + 1) / 2) med2 /* 구간의 중앙 위치(오른쪽) */ \
           from ( select 항만 \
                       , 입항선박수 \
                       , floor(입항선박수 / 500) bin_id \
                       , row_number() over (partition by floor(입항선박수 / 500) order by 입항선박수) rnum \
                       , count(*) over (partition by floor(입항선박수 / 500)) cnt \
                  from " + src_table + " )")

# 출항선박수 중앙값을 구하는 뷰(view)
cur.execute("create or replace view 출항_median_view \
           as \
           select 항만 \
                , 출항선박수 \
                , bin_id /* 구간 id */ \
                , rnum /* 구간 내의 위치 */ \
                , floor((cnt + 1) / 2) med1 /* 구간의 중앙 위치(왼쪽) */ \
                , ceil((cnt + 1) / 2) med2  /* 구간의 중앙 위치(오른쪽) */ \
           from ( select 항만 \
                       , 출항선박수 \
                       , floor(출항선박수 / 500) bin_id \
                       , row_number() over(partition by floor(출항선박수 / 500) order by 출항선박수) rnum \
                       , count(*) over(partition by floor(출항선박수 / 500)) cnt \
                  from " + src_table + " )")

# 입항선박수와 출항선박수 평활(중앙)값 결합
result_df = pd.read_sql(" \
          select 항만 \
               , min(decode(gubun, 1, col1)) 입항선박수 \
               , min(decode(gubun, 1, col2)) 입항선박수_평활 \
               , min(decode(gubun, 2, col1)) 출항선박수 \
               , min(decode(gubun, 2, col2)) 출항선박수_평활 \
          from ( select 1 gubun /* 입항선박수 중앙값 구하기 */ \
                      , a.항만 \
                      , a.입항선박수 col1 \
                        /* b.입항선박수 : 구간 내 중앙(왼쪽)값, c.입항선박수 : 구간 내 중앙(오른쪽)값 */ \
                      , round((b.입항선박수+c.입항선박수) / 2, 0) col2 \
                 from 입항_median_view a, 입항_median_view b, 입항_median_view c \
                 where a.bin_id = b.bin_id and a.med1 = b.rnum \
                   and a.bin_id = c.bin_id and a.med2 = c.rnum \
                 union all \
                 select 2 gubun /* 출항선박수 중앙값 구하기 */ \
                      , a.항만 \
                      , a.출항선박수 col1 \
                        /* b.출항선박수 : 구간 내 중앙(왼쪽)값, c.출항선박수 : 구간 내 중앙(오른쪽)값 */ \
                      , round((b.출항선박수 + c.출항선박수) / 2, 0) col2 \
                 from 출항_median_view a, 출항_median_view b, 출항_median_view c \
                 where a.bin_id = b.bin_id and a.med1 = b.rnum \
                   and a.bin_id = c.bin_id and a.med2 = c.rnum ) \
          group by 항만", con=conn_ora)

# 결과보기(첫 10개행만 출력)
print(result_df.head(10))

# 경계값 평활화 (동일 너비 방식, 구간너비 : 500)
result_df = pd.read_sql("select 항만 \
                          , 입항선박수 \
                          , case when (입항선박수 - 입항_경계_최소) < (입항_경계_최대 - 입항선박수) then 입항_경계_최소 \
                            else 입항_경계_최대 end 입항선박수_평활 \
                          , 출항선박수 \
                          , case when (출항선박수 - 출항_경계_최소) < (출항_경계_최대 - 출항선박수) then 출항_경계_최소 \
                            else 출항_경계_최대 end 출항선박수_평활 \
                      from ( \
                             select 항만 \
                                  , 입항선박수 \
                                  , floor(입항선박수/500)*500 입항_경계_최소 \
                                  , floor(입항선박수/500)*500 + 500 입항_경계_최대 \
                                  , 출항선박수 \
                                  , floor(출항선박수/500)*500 출항_경계_최소 \
                                  , floor(출항선박수/500)*500 + 500 출항_경계_최대 \
                             from " + src_table + " )", con=conn_ora)

# 결과보기(첫 10개행만 출력)
print(result_df.head(10))

# 회귀분석에 의한 평활화 (입출항선박수와 입출항선박톤수 간 회귀분석)
# 회귀분석 시, 결측치 등으로 인한 경고메시지 출력 방지
np.seterr(invalid='ignore')

# 선형회귀분석을 위한 scipy 패키지 중 stats 모듈 임포트
from scipy import stats

# stats.linregress(x, y) : y = slope * x + intercept 형식의 선형함수를 찾아주는 stats 모듈 함수로 다섯 개의 값을 반환
slope, intercept, r_value, p_value, std_err = stats.linregress(rawData['입항선박수'], rawData['입항선박톤수'])

# 입항선박수에 의한 입항선박톤수 산출
rawData.loc['입항선박톤수'] = rawData['입항선박수']*slope + intercept

slope, intercept, r_value, p_value, std_err = stats.linregress(rawData['출항선박수'], rawData['출항선박톤수'])

# 출항선박수에 의한 출항선박톤수 산출
rawData.loc['출항선박톤수'] = rawData['출항선박수']*slope + intercept

# 결과보기(첫 10개행만 출력)
print(rawData.head(10))

# 커서(cursor) 종료
cur.close()

# Oracle connection 종료
conn_ora.close()