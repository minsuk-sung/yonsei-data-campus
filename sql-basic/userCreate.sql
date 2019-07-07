-- KIM, LEE 사용자 생성하기
CREATE USER KIM IDENTIFIED BY kim
DEFAULT TABLESPACE users;

CREATE USER LEE IDENTIFIED BY lee;

-- Grant 명령어로 접속, 사용 권한 주기
grant connect, resource to KIM;
grant connect, resource to LEE;
