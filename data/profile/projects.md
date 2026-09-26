# Projects

## Confident project

가장 자신 있는 프로젝트는 qa-for-me다. 나에 대한 Q&A를 위해 프로필 로더, 청크, Chroma 적재, LangGraph의 prepare → retrieve(bio|projects) → generate, 대화 history, 1인칭 답변까지 직접 이어 붙인 개인 프로젝트이기 때문이다. Cursor를 쓰되 코드를 이해하고 의도대로 고칠 수 있을 때만 다음 단계로 진행하는 방식으로 만들고 있다.

## Project

기간순 목록이다. delivery-service(2024.03~2024.05, 음식 주문 백엔드), movie-recommendation(2025.12~2026.01, 영화 추천 대회), why-song-serious(2026.01~2026.02, 음악 추천 서빙), qa-for-me(2026.09~진행 중, 개인 Q&A)다. 상세는 아래 각 절이다.

### Delivery Service

- 기간: 2024.03.13~2024.05.27
- 형태: 2인 프로젝트 (친한 친구와)
- 역할: 백엔드 API, DB 구조 설계 및 구현
- 한 줄: 음식 주문 서비스
- 저장소: https://github.com/DaGoMi1/delivery-service
- 스택: Java, Spring Boot, JPA, MySQL, Redis, JWT

#### 풀려던 문제

손님은 회원가입 뒤 한 가게 메뉴만 장바구니에 담고, 대표 주소로 주문을 만든다. 점주는 그 주문을 상태 머신대로만 넘긴다. 가게 목록의 평점과 찜 수는 조회마다 리뷰 테이블을 합산하지 않고 Redis에 올려 둔 값을 쓴다. 이러한 과정들을 통해 가게의 원하는 음식 메뉴를 찾고 주문하는 과정까지의 음식 주문 서비스를 만들려고 했다.

#### 데이터

공개 학습 데이터가 아니다. 스키마는 직접 짠 MySQL이고, ERD는 드라이브에 1차부터 7차까지 남아 있다. API 요청과 응답은 Postman 컬렉션 delivery_service_api.json이다.

역할은 CUSTOMER, OWNER, ADMIN이다. 가입 직후 역할은 CUSTOMER이고, 빈 장바구니가 같이 생긴다. 아이디, 이메일, 휴대폰은 각각 unique다. 닉네임도 unique이고 길이는 10이다.

가게 상태는 OPEN, CLOSED, TEMPORARILY_CLOSED다. 생성 직후는 CLOSED다. 메뉴는 is_available이 있고, 생성 직후는 false다. 주문 상태는 PENDING, CONFIRMED, PREPARING, OUT_FOR_DELIVERY, COMPLETED, CANCELLED다. 리뷰 별점은 1에서 5다. 평점 응답은 합계를 개수로 나눈 뒤 소수 한 자리로 반올림한다. 리뷰가 없으면 0.0이다.

#### 만든 시스템

스택은 Spring Boot 3.4.3, Java 23, Spring Security, JPA, MySQL, Gradle이다. 인증은 jjwt 0.12.3이다. 캐시는 Redis이고 Lettuce로 localhost:6379에 붙는다. 메일은 JavaMailSender다. 결제 호출만 WebFlux WebClient다.

Auth: POST /auth/login은 아이디와 BCrypt 비밀번호가 맞으면 access, refresh를 같이 준다. 주석상 access는 설정값 초 단위, refresh도 같다. POST /auth/refresh-token은 Authorization의 Bearer refresh로 access만 다시 만든다. refresh는 서버에 저장하지 않는다. 로그아웃과 폐기 목록은 없다. 세션은 STATELESS다. 비밀번호는 BCrypt다.

권한: 가입, 아이디 찾기, 비밀번호 찾기, /auth/**, /category/**만 비로그인이다. /role/**, /address/**, /cart/**, /cart-item/**, /favorite/**, /review/**는 세 역할 모두다. /store/**, /menu/**, /option-group/**, /option/**는 OWNER와 ADMIN만이다. /admin/**는 ADMIN만이고, 그 경로는 컨트롤러가 없다. 나머지는 로그인만 되면 된다. CORS는 http://localhost:5174이고 메서드는 GET, POST, DELETE, PATCH다.

Member: 가입, 내 정보, 탈퇴, 비밀번호 변경이 있다. 변경은 직전 비밀번호 재사용을 막는다. 아이디 찾기는 휴대폰으로 회원을 찾아 가입 아이디를 메일로 보낸다. 비밀번호 찾기는 아이디와 휴대폰이 맞으면 8자 임시 비밀번호를 저장한 뒤 메일로 보낸다. 메일 실패는 503이다.

Role: PATCH /role/upgrade-to-owner는 CUSTOMER만 받는다. 코드 문자열이 사업자 등록증 032와 같으면 OWNER로 바꾼다. 사업자 등록증 조회는 없다.

Address: 추가, 조회, 수정, 삭제, 대표 주소 설정이 있다. 주문은 대표 주소만 스냅샷으로 복사한다. 대표 주소가 없으면 주문이 거절된다.

Store: 점주가 생성, 수정, 삭제한다. 수정과 삭제는 그 가게의 member이거나 ADMIN만 된다. 조회는 카테고리 id 또는 이름 LIKE %name%다. 정렬 쿼리 type은 FAVORITE, CREATED_AT, RATING이다. 이름 조회 기본값은 favorite다. 페이지는 없다. 거리, 배달비, 영업 중 필터는 없다.

Menu와 옵션: 메뉴 생성, 가게 기준 조회, 수정, 삭제, 메뉴-카테고리 연결이 있다. 옵션 그룹과 옵션은 메뉴 아래에 둔다. 장바구니에 넣는 옵션은 그 메뉴의 옵션이 아니면 거절된다.

Cart: 회원당 장바구니 하나다. 품절 메뉴는 담을 수 없다. 이미 담긴 메뉴와 가게가 다르면 거절된다. 주문 생성 뒤 장바구니를 비운다.

Order: POST /order는 장바구니가 비어 있으면 거절한다. 총액은 (메뉴 가격 + 옵션 가격 합) * 수량이다. 상태는 PENDING으로 시작한다. 결제 방법과 요청사항만 바디로 받는다. 픽업 타입 필드는 없다. GET /order는 내 주문이다. GET /order/{id}의 id는 주문 id가 아니라 가게 id이고, 그 가게 점주만 목록을 본다. PATCH /order/{id}는 그 가게 점주만 상태를 바꾼다. 전이는 PENDING에서 CONFIRMED, CONFIRMED에서 PREPARING, PREPARING에서 OUT_FOR_DELIVERY, OUT_FOR_DELIVERY에서 COMPLETED다. CANCELLED는 PENDING과 CONFIRMED에서만 되고, 취소 사유가 비면 거절된다. 점포 OPEN 여부는 주문 때 보지 않는다.

Review: 주문 소유자만 작성한다. 별점 1에서 5, 코멘트 길이 500이다. 주문이 COMPLETED인지는 보지 않는다. 주문당 리뷰 1개 제약도 없다. 작성하면 그 가게 Redis 평점 합과 리뷰 수를 더하고, 삭제하면 뺀다.

Redis: 서버 기동 시 가게마다 store:rating_sum:{id}, store:review_count:{id}, store:favorite_count:{id}를 DB 집계로 set한다. 가게 목록 DTO의 평점과 찜 수는 이 키를 읽는다. 찜 추가와 삭제 때 favorite_count를 1씩 올리고 내린다. 조회 지연 시간 측정은 없다.

Payment: POST /toss-payment가 토스 POST /v1/payments/confirm을 호출한다. 시크릿은 코드에 박힌 토스 문서용 테스트 키다. 응답 orderId는 무언가_숫자로 split하고, 뒤 숫자를 주문 id로 쓴다. 토스 금액과 주문 총액이 다르면 저장하지 않는다. 맞으면 toss_payment에 paymentKey, 상태, 수단, 금액을 저장한다. 주문 상태를 결제 완료로 바꾸지 않는다. README 기능 표의 결제는 여전히 예정이다.

예외는 @ControllerAdvice다. 권한 없음 401, 사업자 코드 불일치와 정보 불일치 400, 메일 실패와 메뉴 불가 503, 중복 가입 409, 없음 404, 금지 403, 검증 실패 400, 그 밖은 500이다.

테스트는 BeApplicationTests.contextLoads 하나다. GitHub Actions, Docker Compose 파일, 공개 배포는 저장소에 없다. README는 Redis를 Docker로 띄워 학습했다고 적는다. Compose 정의는 커밋되어 있지 않고, 접속 주소는 localhost 6379로 고정이다.

#### 말하면 안 되는 것

프론트를 만들었다고 말하면 안 된다. 정X인 담당이다. 픽업 주문이 있다고 말하면 안 된다. 주문은 대표 주소 스냅샷이고 상태는 배달 출발이 들어 있다. 추천이나 검색 랭킹을 했다고 말하면 안 된다. 정렬은 찜, 생성일, 평점 세 가지다. Redis로 조회가 몇 ms 줄었다고 말하면 안 된다. 지연 측정이 없다. 손님이 가게와 메뉴 API를 연다고 말하면 안 된다. SecurityConfig에서 /store/**와 /menu/**는 OWNER와 ADMIN만 허용한다. 사업자 인증을 연동했다고 말하면 안 된다. 고정 문자열 비교다. 토스 실결제가 된다고 말하면 안 된다. 문서용 테스트 키이고, 승인 뒤 주문 상태를 바꾸지 않는다. README도 결제를 예정으로 둔다. refresh를 서버에서 폐기할 수 있다고 말하면 안 된다. 서명 검증 후 access만 다시 발급한다. Docker Compose로 배포했다고 말하면 안 된다. Compose 파일과 CI와 공개 데모는 없다. 리뷰가 배달 완료 주문에만 달린다고 말하면 안 된다. 주문 소유자 확인만 있다.

### Movie Recommendation

- 기간: 2025.12.15~2026.01.07
- 형태: 팀 프로젝트 (6명)
- 역할: VAE 계열 모델 설계 및 구현, EDA를 통한 앙상블 전략 수립
- 한 줄: 네이버 부스트캠프 AI Tech 영화 추천 대회용 오프라인 프로젝트
- 저장소: https://github.com/DaGoMi1/movie-recommendation
- 스택: Python, PyTorch, Pandas, Scikit-learn

#### 풀려던 문제

각 유저에게 아직 안 본 영화 10편을 고른다. 정답은 별점이 아니다. train_ratings.csv에는 user, item, time만 있고, 행 하나가 시청이다. 제출은 유저 31,360명, 유저당 10행, 총 313,600행이다. 제출 후에 실제로 추천된 영화 10편이 이후에 유저가 본 영화인지 아닌지에 따라 Recall@10을 계산하고 이 값을 가장 높게 만드는 것이 풀려던 문제이다.

#### 데이터

상호작용은 5,154,471건이다. 유저 31,360명, 영화 6,807편이다. 같은 유저-영화 쌍의 중복은 0건이다. 유저당 시청 수는 최소 16, 중앙값 114, 평균 164.36이다. 영화당 시청 수는 최소 27, 중앙값 197이다. 가장 적게 본 유저도 16편이라 유저당 중앙값 1인 콜드 유저 문제는 아니다.

밀도는 5,154,471 / (31,360 × 6,807) = 약 2.415%다. 빈 칸은 약 97.585%다. 희소하다고 말할 수는 있지만 99.9%를 넘었다고 말하면 이 데이터와 맞지 않다.

사이드 정보는 제목, 장르 18개, 감독, 작가, 연도다. 감독이 없는 영화는 19.16%, 작가가 없는 영화는 17.03%, 연도가 없는 영화는 8편이다.

#### 만든 시스템

직접 구현한 쪽은 VAE 계열이다. MultiVAE, RecVAE, M2VAE가 유저-영화 행렬을 복원하고, 추론에서는 이미 본 영화를 뺀다. MultiVAE는 암묵적 피드백(Implicit Feedback) 협업 필터링을 위한 비선형 확률적 생성 모델로, 다항 분포 우도(Multinomial Likelihood), 비선형 모델링, 정규화 가중치 조절(Annealed Regularization) 등을 구현했다. M2VAE는 MultiVAE에서 콜드스타트를 완화하기 위해 메타데이터를 쓰는 모델로 구현했다. RecVAE는 복합 사전 분포와 교대 업데이트로 MultiVAE보다 고도화된 학습을 노린 모델로 구현했다. EDA에서는 데이터 분포 분석으로 sparsity 약 0.97·long-tail이라 희소성 극복이 핵심임을 보았고, timestamp 분석으로 유저당 평균 시청 164편이라 sequential 패턴 학습에 충분하다고 보았다. 장르·감독·작가 side-info가 있어 하이브리드 확장 여지가 있다는 인사이트도 얻었다. Static 특징과 Sequential 특징을 같이 잡아야 성능이 높을 것이라 보고 앙상블 전략을 세웠다. EASE, M2VAE, RecVAE, BERT4Rec, gSASRec 다섯 개를 가중치 0.2로 동일 앙상블했다. EASE는 아이템 공행성, VAE는 취향 분포, sequential은 시청 순서를 맡는 구성이었고, 대회에서 1등을 했다.

#### 말하면 안 되는 것

BERT4Rec, gSASRec, EASE를 본인이 구현했다고 말하면 안 된다. 서빙 프로젝트가 아니다. 대회에서 높은 성능을 내는 모델을 만드는 것이 주 목적이다. Public/Private 점수 숫자를 저장소에 없는 값으로 지어 말하면 안 된다.

### Why Song Serious

- 기간: 2026.01.16~2026.02.06
- 형태: 팀 프로젝트 (6명)
- 역할: 모델 설계 및 구현, 서빙
- 한 줄: 음악 추천 프로젝트, 취향 클러스터 시각화
- 저장소: https://github.com/DaGoMi1/why-song-serious
- 스택: Python, PyTorch, Pandas, Scikit-learn, FastAPI

#### 풀려던 문제

유저에게 오디오 피처 성향을 입력하게 한다(템포, 긍정도, 사운드 크기 등). 그 성향을 기준으로 몇 곡을 벡터 검색으로 빠르게 추천하고, 그중 마음에 드는 곡을 고르게 한다. 최종 선택한 곡을 바탕으로 들어보지 못했을 법하지만 마음에 들 새 음악을 추천하고, 추천된 음악이 취향 클러스터에 어떻게 분포하는지 시각화해 보여주는 것이 풀려던 문제이자 서비스 목적이다.

#### 데이터

Kaggle Spotify_1Million_Tracks다. 라이선스는 Open Data Commons Attribution License (ODC-By) v1.0이다. 출처는 https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks 이다.

#### 만든 시스템

DeepFM으로 저차원·고차원 상호작용을 같이 학습하고, 임베딩을 공유한 뒤 합산과 sigmoid로 클릭 확률을 예측하는 모델을 구현했다. 서빙 추론이 3초 이상 걸려 이탈을 줄이려면 단축이 필요하다고 보고, FAISS로 후보를 빠르게 고른 뒤 그 안에서 DeepFM이 랭킹하는 two-stage로 바꿨다. 로컬에서 본 추론 시간은 3초대에서 0.5초대로 줄었다. 인기곡이 랭킹을 독식하는 경향에 Focal Loss를 적용해 소수·어려운 샘플 가중을 키웠고 다양성이 나아진 것을 확인했다. popularity_bin 등 피처 구간화로 노이즈를 줄였고, negative sampling으로 정답·오답을 분명히 학습하게 했다. 학습된 모델은 서버 로드 시 최초 1회 메모리에 올려 추론에 썼다. FAISS는 처음에 입력 곡 평균 벡터만 썼다가 취향이 뭉개지는 문제가 있어, 개별 벡터와 평균 벡터를 함께 쓰는 검색으로 바꿨다.

#### 말하면 안 되는 것

프론트를 맡았다고 말하면 안 된다. 일반적인 회원 가입·로그인 백엔드를 맡았다고 말하면 안 된다. 모델 구현과 추론 서빙만 했다. 취향 클러스터 시각화를 본인이 했다고 말하면 안 된다. DeepFM이 오프라인 Recall에서 EASE나 LightGCN을 이겼다고 말하면 안 된다.

### qa-for-me

- 기간: 2026.09~진행 중
- 형태: 솔로
- 역할: 전체 (프로필 RAG, LangGraph, FastAPI, Streamlit)
- 한 줄: 나에 대한 질문에 프로필 근거만으로 답하는 개인 Q&A
- 저장소: https://github.com/DaGoMi1/qa-for-me
- 스택: Python, FastAPI, Streamlit, LangChain, LangGraph, Chroma, OpenAI

#### 풀려던 문제

사용자는 자연어로 이다검에 대해 묻는다. 답은 프로필 마크다운에 있는 사실 안에서만 나와야 하고, 1인칭으로 들려야 한다. 소개(bio)와 프로젝트(projects)를 가르고, 이어 묻기도 이전 대화를 반영한 검색어로 다시 찾아야 한다. Cursor를 쓰되 수정 코드를 이해하고 의도대로 고칠 수 있을 때만 다음 단계로 진행하는 방식으로 만들고 있다.

#### 데이터

답변 근거는 data/profile/bio.md와 projects.md다. 청크로 나눈 뒤 Chroma 컬렉션 profile에 넣고, 경로 data/chroma에 둔다. 공개 학습 데이터가 아니다.

#### 만든 시스템

스택은 Python, FastAPI, Streamlit, LangChain, LangGraph, Chroma, OpenAI embeddings(text-embedding-3-small), 채팅 모델 gpt-4o-mini다. 그래프는 prepare → retrieve(bio|projects) → generate다. prepare가 intent(bio|projects)와 검색용 한국어 한 문장(search_query)을 한 번에 만들고, retrieve는 source 필터로 해당 파일 청크만 고른다. generate는 고른 내용만 근거로 1인칭 한국어 답을 쓴다. Streamlit은 최근 대화를 history로 POST /chat에 보낸다. 서버 기동 시 컬렉션이 비어 있을 때만 적재하고, 프로필을 고친 뒤에는 scripts/ingest.py로 강제 재적재한다. 단위 테스트는 가짜 모델·임베딩으로 pytest한다.

#### 말하면 안 되는 것

클라우드 공개 배포나 CI가 있다고 말하면 안 된다. 로컬 FastAPI와 Streamlit이다. 벤치마크·리더보드 점수가 있다고 말하면 안 된다. 팀 프로젝트라고 말하면 안 된다. 혼자 만든다. 프로필에 없는 학력·연락처·다른 사람 풀네임을 지어 말하면 안 된다. rewrite와 classify가 따로 있다고 말하면 안 된다. prepare 한 노드다.
