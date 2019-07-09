# SQL 연습 문제

## 1. 연봉이 12000 이상되는 직원들의 LAST_NAME 및 연봉을 조회한다.

(결과 예제)
```
LAST_NAME SALARY
-------------------------
Hartstein 13000
King 24000
Kochhar 17000
De Haan 17000
Russell 14000
Partners 13500
```

(해답)
```SQL
SELECT LAST_NAME, SALARY  
FROM EMPLOYEES  
WHERE SALARY >= 12000;
```
---

## 2. 사원번호가 176 인 사람의 LAST_NAME 과 부서 번호를 조회한다.

(결과 예제)
```
LAST_NAME DEPARTMENT_ID
------------------------- -------------
Taylor 80
```

(해답)
```SQL

```

---

## 3. 연봉이 5000 에서 12000 의 범위 이외인 사람들의 LAST_NAME 및 연봉을 조회힌다.

(결과 예제)
```
LAST_NAME SALARY
------------------------- ---------- OConnell 2600
Grant 2600
Whalen 4400
Hartstein 13000
King 24000
...
```

(해답)
```SQL
SELECT LAST_NAME, SALARY
FROM EMPLOYEES
WHERE SALARY < 5000 OR SALARY > 12000;
```

---

## 4. 20 번 및 50 번 부서에서 근무하는 모든 사원들의 LAST_NAME 및 부서 번호를 알파벳순으로 조회한다.

(결과 예제)
```
LAST_NAME DEPARTMENT_ID
------------------------- -------------
Atkinson 50
Bell 50
Bissot 50
Bull 50
Cabrio 50
Chung 50
...
```

(해답)
```SQL
SELECT LAST_NAME, DEPARTMENT_ID
FROM EMPLOYEES
WHERE DEPARTMENT_ID IN ( 20, 50 )
ORDER BY LAST_NAME ASC;
```
---

## 5. 20 번 및 50 번 부서에 근무하며, 연봉이 5000 ~ 12,000 사이인 사원들의 LAST_NAME 및 연봉을 조회한다.

(결과 예제)
```
EMPLOYEES SALARY
-------------------------
Fay 6000
Weiss 8000
Fripp 8200
Kaufling 7900
Vollman 6500
Mourgos 5800
```

(해답)
```SQL
SELECT LAST_NAME, SALARY
FROM EMPLOYEES
WHERE DEPARTMENT_ID IN ( 20, 50 )
      AND SALARY >= 5000
      AND SALARY <= 12000;
```
---

## 6. 매니저가 없는 사람들의 LAST_NAME 및 JOB_ID 를 조회한다.

(결과 예제)
```
LAST_NAME JOB_ID
-------------------------
King AD_PRES
```

(해답)
```SQL
SELECT LAST_NAME, JOB_ID, MANAGER_ID
FROM EMPLOYEES
WHERE MANAGER_ID is null OR MANAGER_ID = '';
```

---

## 7. LAST_NAME 의 네번째 글자가 a 인 사원들의 LAST_NAME을 조회한다.

(결과 예제)
```
LAST_NAME
------------------------- 
oran
Errazuriz
Fleaur
Kumar
McCain
Pataballa
Sciarra
Sewall
Tuvault
Urman
```

(해답)
```SQL
SELECT LAST_NAME
FROM EMPLOYEES
WHERE LAST_NAME LIKE '___a%';
```

---

## 8. LAST_NAME 에 a 또는 e 글자가 있는 사원들의 LAST_NAME을 조회힌다.

(결과 예제)
```
LAST_NAME
-----------------------
Baer
Bates
Colmenares
Davies
De Haan
Faviet
Fleaur
Gates
Hartstein
Markle
Nayer
Partners
Patel
Philtanker
Raphaely
Sewall
Whalen
```

(해답)
```SQL
SELECT LAST_NAME
FROM EMPLOYEES
WHERE LAST_NAME LIKE '%a%' OR LAST_NAME LIKE '%e%';
```
---

## 9. 연봉이 2,500, 3,500, 7000 이 아니며 직업이 SA_REP 이나 ST_CLERK 인 사람들을 조회한다.

(결과 예제)
```
LAST_NAME JOB_ID SALARY
-------------------------
Nayer ST_CLERK 3200
Mikkilineni ST_CLERK 2700
Landry ST_CLERK 2400
Markle ST_CLERK 2200
...
```

(해답)
```SQL
SELECT LAST_NAME, JOB_ID, SALARY
FROM EMPLOYEES
WHERE SALARY NOT IN ( 2500, 3500, 7000 )
      AND JOB_ID IN ( 'SA_REP', 'ST_CLERK' );
```

---

## 10. 모든 사원들의 LAST_NAME, 부서 번호 및 부서 이름을 조회한다.

(결과 예제)
```
LAST_NAME DEPARTMENT_ID DEPARTMENT_NAME
------------------------- -------------OConnell 50 Shipping
Grant 50 Shipping
Whalen 10 Administration
Hartstein 20 Marketing
Fay 20 Marketing
...
```

(해답)
```SQL
SELECT EMPLOYEE_ID, LAST_NAME, DEPARTMENT_NAME, D.DEPARTMENT_ID
FROM EMPLOYEES E, DEPARTMENTS D
WHERE E.DEPARTMENT_ID = D.DEPARTMENT_ID;
```
---

## 11. 부서번호 30 내의 모든 직업들을 중복없이 조회한다. 90 부서 또한 포함한다.

(결과 예제)
```
JOB_ID LOCATION_ID
---------- ----------- AD_PRES 1400
AD_VP 1500
PU_CLERK 1700
AD_PRES 1700
AD_VP 2500
AD_VP 2400
AD_PRES 1500
AD_VP 1400
PU_MAN 1700
AD_PRES 1800
AD_PRES 2400
AD_PRES 2500
AD_VP 1700
AD_VP 1800
AD_PRES 2700
AD_VP 2700
```

(해답)
```SQL
SELECT DISTINCT JOB_ID, D.DEPARTMENT_ID
FROM EMPLOYEES E, DEPARTMENTS D
WHERE E.DEPARTMENT_ID = D.DEPARTMENT_ID AND D.DEPARTMENT_ID IN ( 30, 90 )
ORDER BY JOB_ID;
```

---

## 12. 커미션을 버는 모든 사람들의 LAST_NAME, 부서 명, 지역 ID 및 도시 명을 조회한다.

(결과 예제)
```
LAST_NAME DEPARTMENT_NAME LOCATION_ID CITY
------------------------- ------------------------------
Russell Sales 2500 Oxford
Partners Sales 2500 Oxford
Errazuriz Sales 2500 Oxford
Cambrault Sales 2500 Oxford
Zlotkey Sales 2500 Oxford
Tucker Sales 2500 Oxford
...
```

(해답)
```SQL
SELECT LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY
FROM EMPLOYEES E, DEPARTMENTS D, LOCATIONS L
WHERE E.DEPARTMENT_ID = D.DEPARTMENT_ID -- 빨간줄
    AND D.LOCATION_ID = L.LOCATION_ID; -- 보라줄
```

---