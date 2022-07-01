# Project_PL
## http://ggmc.shop
## 프리미어리그 팀 소식공유 커뮤니티 미니 프로젝트입니다.
- 김승수
- 송하준
- 이창호
- 정성욱


## 미니 프로젝트 SA

## 프로젝트명: 금쪽같은 내 시티
>    - 프리미어리그 팀 소식 공유 서비스
>    - `항해99` 1주차 첫 미니 프로젝트
>    - 6.20.~6.23. 4일간의 노오오력

---

### 프로젝트 개요
> #### 💡 필수 포함 사항
>  - `Jinja2` 템플릿 엔진을 이용한 서버사이드 렌더링
>  - `JWT` 인증 방식으로 `로그인 구현`하기

#### 개발기한
- 22.6.20.(월) ~ 6.23.(목)
#### 일정 프로세스
- 1일차
  - 프로젝트 준비(서비스 구상, API 설계, 와이어프레임 작성(Figma), 기능 선정, 역할분담)
- 2일차
  - 개인 공부, 서비스 구현
- 3일차
  - Git 병합, 이슈 해결
- 4일차
  - AWS 연동, 도메인 연결, 서비스 테스트
  
  
### 서비스 기능
#### 1. 로그인 Dropdown Bar
#### 2. 회원가입 (Modal Page)
#### 3. 메인 페이지
#### 4. 팀 페이지(팀 뉴스/ 팀 게시판)

### 구현기능
- 로그인 기능
- 회원가입 기능
- 팀별 뉴스(BBC) 모아보기
- 팀별 게시글 모아보기 (인기순 정렬)
- 게시판 글쓰기
- 좋아요 / 싫어요 기능

### 사용도구
- HTML & CSS
- JavaScript - Ajax
- Python - pymongo, flask, bs4, ...

---
### 팀빌딩 및 역할

> - `항해99` 1주차 인원 4명으로 8조 구성
> - `FE/BE` 구분 없이 다양한 경험을 위한 역할 배정
> - `A팀/B팀`으로 나누어 역할별 유기적 협동

### 개발자 (가나다순)

#### 김승수 [@kimseungsuu](https://github.com/kimseungsuu) / (B팀)
- 팀별 뉴스 페이지 담당
- 팀별 뉴스(BBC 크롤링)

#### 송하준 [@FoocoJun](https://github.com/FoocoJun) / 조장 (B팀)
- 팀별 게시판 페이지 담당
- 게시글 등록 구현
- 게시글 좋아요 싫어요 정렬 구현

#### 이창호 [@chlee1234](https://github.com/chlee1234) / (A팀)
- 로그인 페이지 담당
- 로그인 Dropdown Bar 구현
- JWT 인증방식 로그인 구현

#### 정성욱 [@jm03100](https://github.com/jm03100) / (A팀)
- 메인 페이지 담당
- 더보기(or Slide) 버튼 구현
- 회원가입 페이지 담당

>
#### 🤿 버려진 기능들
- ~~`팀별 뉴스 및 팀별 게시글 무한스크롤 구현`~~
- ~~`회원가입 모달 창 구현`~~

---
### API 설계하기




| 기능 | Method | URL | request | response |
|:------|:----------|:----------|:----------|:----------|
|메인페이지|`GET`|/|
|로그인|POST|/login| {"_id":"id string",<br>"_password":"password"<br>}|
|회원가입 페이지로 이동||/sign_up|
|회원가입|POST|/sign_up/new|{"username":"username_string",<br>"nickname":"nickname_string",<br>"password":"password_string"<br>}
|게시글 목록|GET|/team/read
|게시글 기록작성|POST|/team/write<br>DB이름 - sparta<br>글 저장 컬렉션 - articles|{"comment":"comment_string",<br>"date":"time-date_string"<br>}
|게시글 좋아요|POST|/team/write/likes|
|게시글 싫어요|POST|/team/write/dislikes|

---
### 와이어프레임

#### <전체 와이어프레임>
![](https://velog.velcdn.com/images/fxoco/post/b57df892-c2ee-403c-90d5-3633c2feeee6/image.png)



#### <메인 페이지>
> - Sign In 클릭 시 드롭다운 메뉴로 로그인 (회원가입)
- 로고 클릭시 팀별 페이지로 이동

![](https://velog.velcdn.com/images/fxoco/post/e279c187-5364-4c29-bd57-632e9f71c033/image.png)


#### <회원가입 페이지>
> - 이름, 닉네임, 비밀번호 입력 후 회원가입

![](https://velog.velcdn.com/images/fxoco/post/e3456c13-f8c5-4cc1-b9fe-fc8162d59e6c/image.png)

#### <팀별 페이지>
> 💡 팀 뉴스 페이지(좌) / 팀 게시판(우)
- 팀 뉴스 페이지
  - 팀 인스타그램, 페이스북, 트위터, 공식 홈페이지 링크 제공
  - 팀 설명을 위한 킹무위키 링크
  - 최근 경기 결과 / 예정 경기 제공
  - 팀별 뉴스 제공
- 팀 게시판
  - 팀을 주제로 게시글 작성 기능 (닉네임, 작성일시)
  - 좋아요 싫어요 버튼을 통한 인기순 정렬
  
![](https://velog.velcdn.com/images/fxoco/post/05f83ba1-9a5c-4b99-9138-ab0a5567f2ad/image.png)




