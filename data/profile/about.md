# About

학부 때 백엔드에 관심을 두고 학습했고, 최근에는 AI를 붙인 서비스를 만드는 데 관심이 있습니다. 추천 후보를 검색이 고르고, LLM은 그 후보 안에서만 이유를 쓰도록 서비스를 구성합니다.

## Name

이름은 이다검입니다.

## Location

부산에서 살고 있습니다.

## GitHub

깃허브는 https://github.com/DaGoMi1 입니다.

## Project

기간순 목록이다. delivery-service(2025.02~2025.04, 배달 백엔드), movie-recommendation(2025.12~2026.01, 영화 추천 대회), why-song-serious(2026.01~2026.02, 음악 추천 서빙), why-this-product(2026.09, 쇼핑 어시스턴트)다. 상세는 아래 각 절이다.

### delivery-service

기간은 2025.02.21~2025.04.09다. 저장소는 https://github.com/DaGoMi1/delivery-service 이다. 그 이후 커밋은 README 수정이고, 백엔드 Java 변경은 2025.04.09가 마지막이다.

배달 주문을 받는 웹 앱의 백엔드다. 회원, 가게, 메뉴, 장바구니, 주문 상태, 리뷰, 찜, 토스 결제 승인을 Spring Boot API로 붙였다. 프론트는 정X인이 했고, 이다검은 백엔드만 했다. 서비스 메일 제목의 이름은 배달의 부족이다.

#### 풀려던 문제

손님은 회원가입 뒤 한 가게 메뉴만 장바구니에 담고, 대표 주소로 주문을 만든다. 점주는 그 주문을 상태 머신대로만 넘긴다. 가게 목록의 평점과 찜 수는 조회마다 리뷰 테이블을 합산하지 않고 Redis에 올려 둔 값을 쓴다. 추천 모델은 없다. 정렬은 찜 수, 생성 시각, 평점 내림차순뿐이다.

#### 데이터

공개 학습 데이터가 아니다. 스키마는 직접 짠 MySQL이고, ERD는 드라이브에 1차부터 7차까지 남아 있다. API 요청과 응답은 Postman 컬렉션 delivery_service_api.json이다.

역할은 CUSTOMER, OWNER, ADMIN이다. 가입 직후 역할은 CUSTOMER이고, 빈 장바구니가 같이 생긴다. 아이디, 이메일, 휴대폰은 각각 unique다. 닉네임도 unique이고 길이는 10이다.

가게 상태는 OPEN, CLOSED, TEMPORARILY_CLOSED다. 생성 직후는 CLOSED다. 메뉴는 is_available이 있고, 생성 직후는 false다. 주문 상태는 PENDING, CONFIRMED, PREPARING, OUT_FOR_DELIVERY, COMPLETED, CANCELLED다. 리뷰 별점은 1에서 5다. 평점 응답은 합계를 개수로 나눈 뒤 소수 한 자리로 반올림한다. 리뷰가 없으면 0.0이다.

#### 만든 시스템

스택은 Spring Boot 3.4.3, Java 23, Spring Security, JPA, MySQL, Gradle이다. 인증은 jjwt 0.12.3이다. 캐시는 Redis이고 Lettuce로 localhost:6379에 붙는다. 메일는 JavaMailSender다. 결제 호출만 WebFlux WebClient다.

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

Payment: POST /toss-payment가 토스 POST /v1/payments/confirm을 호출한다. 시크릿은 코드에 박힌 토스 문서용 테스트 키 test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6다. 응답 orderId는 무언가_숫자로 split하고, 뒤 숫자를 주문 id로 쓴다. 토스 금액과 주문 총액이 다르면 저장하지 않는다. 맞으면 toss_payment에 paymentKey, 상태, 수단, 금액을 저장한다. 주문 상태를 결제 완료로 바꾸지는 않는다. README 기능 표의 결제는 여전히 예정이다.

예외는 @ControllerAdvice다. 권한 없음 401, 사업자 코드 불일치와 정보 불일치 400, 메일 실패와 메뉴 불가 503, 중복 가입 409, 없음 404, 금지 403, 검증 실패 400, 그 밖은 500이다.

테스트는 BeApplicationTests.contextLoads 하나다. GitHub Actions, Docker Compose 파일, 공개 배포는 저장소에 없다. README는 Redis를 Docker로 띄워 학습했다고 적는다. Compose 정의는 커밋되어 있지 않고, 접속 주소는 localhost 6379로 고정이다.

#### 말해도 되는 것

2025년 2월 21일부터 4월 9일까지 배달 서비스 백엔드를 혼자 붙였다. 프론트는 팀원 정X인이다. Spring Boot와 JWT로 손님, 점주, 관리자 권한을 나눴고, 장바구니는 한 가게만 담기게 막았다. 주문 총액은 메뉴와 옵션과 수량으로 계산하고, 점주는 PENDING부터 COMPLETED까지 정해진 전이만 시킨다. 취소는 조리 시작 전과 사유가 있을 때만 된다. 가게 정렬용 평점과 찜 수는 기동 시 Redis에 올리고, 리뷰와 찜이 바뀔 때 그 키만 증감한다. 토스 결제 승인은 테스트 키로 confirm을 호출하고, 금액이 주문 총액과 같을 때만 결제 row를 저장한다. 아이디와 임시 비밀번호는 메일로 보낸다.

#### 말하면 안 되는 것

프론트를 만들었다고 말하면 안 된다. 정X인 담당이다. 픽업 주문이 있다고 말하면 안 된다. 주문은 대표 주소 스냅샷이고 상태는 배달 출발이 들어 있다. 추천이나 검색 랭킹을 했다고 말하면 안 된다. 정렬은 찜, 생성일, 평점 세 가지다. Redis로 조회가 몇 ms 줄었다고 말하면 안 된다. 지연 측정이 없다. 손님이 가게와 메뉴 API를 연다고 말하면 안 된다. SecurityConfig에서 /store/**와 /menu/**는 OWNER와 ADMIN만 허용한다. 사업자 인증을 연동했다고 말하면 안 된다. 고정 문자열 비교다. 토스 실결제가 된다고 말하면 안 된다. 문서용 테스트 키이고, 승인 뒤 주문 상태를 바꾸지 않는다. README도 결제를 예정으로 둔다. refresh를 서버에서 폐기할 수 있다고 말하면 안 된다. 서명 검증 후 access만 다시 발급한다. Docker Compose로 배포했다고 말하면 안 된다. Compose 파일과 CI와 공개 데모는 없다. 리뷰가 배달 완료 주문에만 달린다고 말하면 안 된다. 주문 소유자 확인만 있다.

### movie-recommendation

기간은 2025.12.15~2026.01.07이다. 저장소는 https://github.com/DaGoMi1/movie-recommendation 이다.

네이버 부스트캠프 AI Tech 영화 추천 대회용 오프라인 프로젝트다. 서빙 앱이 아니다. 산출물은 유저당 영화 10개의 제출 CSV다. 이다검이 한 일은 VAE 계열 구현과, EDA를 근거로 한 앙상블 전략이다. 대회 결과는 저장소에 없고, 본인이 확인한 성적은 7팀 중 1위다.

#### 풀려던 문제

각 유저에게 아직 안 본 영화 10편을 고른다. 정답은 별점이 아니다. train_ratings.csv에는 user, item, time만 있고, 행 하나가 시청이다. 제출은 유저 31,360명, 유저당 10행, 총 313,600행이다.

EDA에서 시청 기록이 두 종류로 섞여 있었다. 특정 시점 이후는 시간순이고, 그 이전은 랜덤 샘플링된 Static 데이터다. Static 구간은 VAE 계열인 Multi-VAE, RecVAE, M2VAE로 잡고, 시간순 구간은 BERT4Rec과 gSASRec으로 잡기로 했다. 그 근거로 최종 제출은 EASE, RecVAE, M2VAE, BERT4Rec, gSASRec을 가중치 0.2씩 같게 앙상블한 것이다. 이 가중은 저장소 파일에 없고, 제출 구성으로 확인한 값이다.

#### 데이터

상호작용은 5,154,471건이다. 유저 31,360명, 영화 6,807편이다. 같은 유저-영화 쌍의 중복은 0건이다. 유저당 시청 수는 최소 16, 중앙값 114, 평균 164.36이다. 영화당 시청 수는 최소 27, 중앙값 197이다. 가장 적게 본 유저도 16편이라 유저당 중앙값 1인 콜드 유저 문제는 아니다.

밀도는 5,154,471 / (31,360 × 6,807) = 약 2.415%다. 빈 칸은 약 97.585%다. 희소하다고 말할 수는 있지만 99.9%를 넘었다고 말하면 이 데이터와 맞지 않다.

사이드 정보는 제목, 장르 18개, 감독, 작가, 연도다. 감독이 없는 영화는 19.16%, 작가가 없는 영화는 17.03%, 연도가 없는 영화는 8편이다.

#### 만든 시스템

README 베이스라인은 CIKM 2020 S3Rec을 대회 데이터에 맞춘 것이다. 최종 제출 모델은 아니다.

직접 구현한 쪽은 VAE 계열이다. MultiVAE, RecVAE, M2VAE가 유저-영화 행렬을 복원하고, 추론에서는 이미 본 영화를 뺀다. 같은 대회 데이터 위에 EASE, BERT4Rec, DeepFM, CatBoost 코드도 저장소에 있다. CatBoost는 VAE 후보 100편 안에서 10편을 다시 줄 세우는 경로다. 코드에 적힌 결합은 VAE 등수 0.4, CatBoost 등수 0.6이다. 실제 제출은 그 경로가 아니라 다섯 모델의 동일 가중 앙상블이다.

M2VAE 사이드 정보 메모의 로컬 Recall@10은 상호작용만 0.0753, 가중을 조정한 v1이 0.0777이다. 차이는 0.0024다. 이 숫자는 유저당 랜덤 양성 1개의 적중률이라 대회 Recall@10이 아니다.

#### 말해도 되는 것

2025년 12월 15일부터 2026년 1월 7일까지 부스트캠프 영화 추천 대회에서 VAE 계열을 구현하고, EDA로 앙상블 전략을 정했다. 시청 로그는 5,154,471건, 유저 31,360명, 영화 6,807편, 밀도 약 2.4%다. Static 구간은 VAE, 시간순 구간은 BERT4Rec과 gSASRec으로 보고, 최종 제출은 EASE, RecVAE, M2VAE, BERT4Rec, gSASRec을 가중치 0.2로 합친 것이다. 성적은 7팀 중 1위다. 이미 본 영화는 빼고 유저당 10편을 제출한다.

#### 말하면 안 되는 것

1위나 가중치 0.2가 저장소 리더보드 파일에 있다고 말하면 안 된다. 대회 결과와 제출 구성으로 확인한 것이다. CatBoost 재정렬이나 S3Rec을 최종 제출이라고 말하면 안 된다. M2VAE Recall@10 0.07대를 대회 점수로 말하면 안 된다. 사이드 정보가 성능을 크게 올렸다고 말하면 안 된다. 기록된 차이는 약 0.0024다. 희소도가 99.9%를 넘었다고 말하면 안 된다. 이 데이터 밀도는 약 2.4%다. 별점 RMSE, 인기순 승리, MMR, RAG, 한국어 설명, API, Docker 배포는 이 프로젝트의 이야기가 아니다.

### why-song-serious

기간은 2026.01.16~2026.02.06이다. 저장소는 https://github.com/DaGoMi1/why-song-serious 이다. 원본 팀 저장소는 https://github.com/boostcampaitech8/pro-recsys-finalproject-recsys-03 이다.

네이버 부스트캠프 AI Tech 최종 프로젝트로 만든 팀 음악 추천 서비스다. 팀은 구X민, 박X연, 송X호, 이다검, 이X재, 최X우다. 이다검의 역할은 FAISS와 DeepFM 모델링, 그리고 그 모델의 서빙 연동이다. 백엔드는 송X호, 프론트엔드는 박X연이다. 추천 추론은 FastAPI 앱 Why Song Serious AI API로 뜨고, 헬스 경로는 /health다.

#### 풀려던 문제

선택한 곡을 입력으로 플레이리스트를 만든다. 오프라인 Recall@10만 보면 EASE 0.2601, LightGCN 0.2023, DeepFM 0.0205다. DeepFM 숫자는 처음 보는 유저를 가정한 콜드 스타트 테스트다. 서비스는 Recall 1등을 서빙하지 않았다. 후보를 빨리 뽑고, 오디오 피처로 콜드 스타트를 순위 매기려고 two-stage를 썼다.

#### 데이터

Kaggle Spotify_1Million_Tracks다. 라이선스는 Open Data Commons Attribution License (ODC-By) v1.0이다. 출처는 https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks 이다.

#### 만든 시스템

후보는 FAISS가 100곡을 뽑고, DeepFM이 그중 10곡을 내보낸다. 설정은 retrieval_top_k 100, rerank_top_k 10이다. DeepFM 임베딩 차원은 64, hidden layers는 256, 128, 64, dropout은 0.4다. 범주 피처는 pid, id, artists와 구간화된 오디오 피처다. 오디오 열은 acousticness, valence, energy, danceability, instrumentalness, loudness, speechiness, tempo, popularity다. 각 열의 bin이 범주 피처로 들어간다. 처음 보는 유저 pid는 8이다.

FAISS 쿼리는 시드 곡 오디오 피처를 스케일한 뒤, 평균 벡터와 곡별 벡터를 같이 넣는다. 곡마다 k개씩 찾고 중복과 시드 곡을 뺀 다음 상위 k를 후보로 쓴다. 평균만 쓰면 템포 30, 40, 180, 170의 중심이 105처럼 서로 다른 취향이 가운데로 섞인다. 그래서 평균을 없앤 것이 아니라 개별 곡 벡터를 쿼리에 더했다. 시드가 학습 상호작용에 없으면 pid 824067을 쓴다.

DeepFM 손실은 focal_binary_cross_entropy_with_logits다. alpha는 0.8, gamma는 2.0이다. 주석은 양성 대 음성을 1대 4로 두고, 맞히기 쉬운 샘플의 손실 가중을 낮춘다고 적는다. 식은 -(1 - p_t)^gamma * log(p_t)에 alpha를 붙인 형태다. 연속 피처 binning은 이상치 영향을 줄이고 비선형 관계를 학습하려는 전처리로 README에 있다. 코드의 구간 이름에 pop_grade는 없고 popularity_bin이 있다.

Docker Compose로 서비스를 띄우는 절차가 README에 있다. PostgreSQL을 요구한다.

서빙 추론 시간은 저장소 로그가 아니라 로컬에서 확인한 값이다. DeepFM만 쓰면 3초대였고, FAISS로 후보를 줄인 two-stage는 0.5초대였다.

#### 말해도 되는 것

2026년 1월 16일부터 2월 6일까지 부스트캠프 최종 프로젝트에서 FAISS 후보 100곡과 DeepFM 재정렬 10곡을 모델링하고, 그 추론을 FastAPI로 서빙하는 쪽을 맡았다. 오프라인 Recall@10은 EASE가 0.2601로 가장 높고 DeepFM 콜드 스타트는 0.0205다. 서빙은 Recall 순위가 아니라 후보 검색과 피처 랭킹을 나누려고 two-stage를 썼다. 로컬에서 본 서빙 추론 시간은 DeepFM 단일 3초대에서 two-stage 0.5초대로 줄었다. Focal Loss alpha 0.8, gamma 2.0으로 쉬운 정답의 손실을 낮췄다. FAISS는 평균 벡터와 곡별 벡터를 함께 쿼리로 쓴다. 오디오 피처와 popularity는 bin으로 넣어 DeepFM 범주 피처가 된다.

#### 말하면 안 되는 것

DeepFM이 Recall에서 EASE나 LightGCN을 이겼다고 말하면 안 된다. 표의 DeepFM은 0.0205다. 백엔드나 프론트를 만들었다고 말하면 안 된다. 역할 표에서 백엔드는 송X호, 프론트엔드는 박X연이다. 그 3초대와 0.5초대를 README나 벤치 로그에 있는 숫자라고 말하면 안 된다. 로컬 서빙 추론에서 확인한 대략의 시간이다. pop_grade라는 이름으로 곡 빈도 구간을 만들었다고 말하면 안 된다. 구간에 남은 이름은 popularity_bin을 포함한 오디오 bin이다. 평균 벡터를 빼고 곡별 벡터만 검색한다고 말하면 안 된다. 추론 코드는 평균 벡터와 개별 곡 벡터를 같이 쌓는다. LLM 설명이나 클러스터 맵을 본인 역할이라고 말하면 안 된다. 역할 표의 LLM 기반 설명과 클러스터는 다른 팀원이다.

### why-this-product

기간은 2026.09.11~2026.09.23이다. 저장소는 https://github.com/DaGoMi1/why-this-product 이다.

Amazon All_Beauty 카탈로그에서 상품을 찾고, 그 후보 안에서만 "왜 이 상품인가"를 리뷰와 설명 스니펫으로 쓰는 쇼핑 어시스턴트다. RecSys, 검색, RAG, 서빙을 한 사람이 끝까지 붙인 솔로 프로젝트이고, 구현과 문서에 Cursor를 썼다. LLM은 이미 고른 후보 밖 상품을 고르지 못한다.

#### 풀려던 문제

영어 쿼리로 뷰티 상품을 찾고, 각 상품에 한국어 한두 문장 이유를 붙인다. 이유는 영어 원문 스니펫을 인용한다. 개인화 추천인 user_id 경로도 남겨 두었지만, 오프라인 평가 끝에 그 경로의 기본은 학습 랭커가 아니라 인기순이 되었다.

#### 데이터

데이터는 Amazon Reviews 2018 All_Beauty다. Ni, Li, McAuley, EMNLP-IJCNLP 2019. 리뷰는 약 37만 건이고 메타데이터는 약 3.3만 상품이다. 속성 품질 리포트 기준 상품은 32,488개다.

전체 유저는 319,335명이다. 유저당 리뷰 중앙값은 1, 75%도 1, 평균은 1.12다. 평점 분포는 1점 38,486, 2점 19,854, 3점 28,809, 4점 50,952, 5점 218,980이다. 5점이 약 61%다.

카탈로그 공백은 brand 47.9%, description 54.4%, price 65.1%가 비어 있다. 카테고리는 전부 All Beauty 하나라 unique category는 1이다. 검색은 제목, 브랜드, 설명 텍스트에 기대야 했다.

희소도는 유저×아이템 행렬에서 상호작용이 차지하는 칸이 극히 적다는 뜻이다. 상호작용 약 35.7만(평점 분포 합)을 유저 319,335명과 상품 약 3.3만 개의 곱으로 나누면 밀도는 약 0.0034%이고, 희소도는 약 99.997%다. 99.9%를 넘었다는 말은 이 계산과 맞다.

분할은 랜덤이 아니다. timestamp 오름차순으로 전역 시간 기준 train, valid, test를 0.8, 0.1, 0.1로 나눈다. 인기도, 아이템 통계, 랭커 피처, RAG 리뷰는 train만 쓴다. valid와 test 리뷰는 설명 근거에 넣지 않는다.

#### 만든 시스템

임베딩 모델은 sentence-transformers/all-MiniLM-L6-v2다. 추천용 FAISS인 faiss_index와 설명용 FAISS인 rag_index는 분리했다. 추천 인덱스의 아이템 문장은 title, brand, description이다.

- Retrieve: 인기순, content FAISS, iALS. 합칠 때는 RRF. 서빙에서 user_id는 인기 top-200이고, 쿼리는 content FAISS다.
- Rank: LightGBM, XGBoost, CatBoost. 서빙에서는 꺼 두고 use_ranker 플래그만 있다.
- Re-rank: MMR, 임베딩 코사인. 서빙에서 켜 두고 람다는 0.5다.
- Explain: 상품 청크 FAISS와 gpt-4o-mini. 이미 고른 ASIN만 받는다. API 키가 없으면 503이다.
- Serve: FastAPI, Streamlit, Docker Compose. 추천과 설명을 API로 나눴다.

POST /api/recommend는 user_id면 인기순과 MMR, query면 content FAISS와 MMR이다. 응답에 timings_ms로 retrieve, rank, rerank 시간을 넣는다. POST /api/explain은 이미 고른 item_ids 1개에서 10개만 받는다. 한국어 이유, 영어 스니펫, 토큰 수를 돌려준다.

UI 기본은 영어 쿼리다. 카탈로그가 영어라 "I need a hydrating serum"처럼 넣는다. 데모 유저는 면도기, 세럼, 향수, 메이크업, 구강 케어 5명이다. 추천 뒤에 설명을 호출하고, 사유 아래에 meta와 review를 인용한다.

#### 추천 실험

평가는 별점 RMSE가 아니다. 리스트 추천이다. 긍정 라벨은 전부 rating이 5 이상이다. 표본은 valid에 5점이 있는 warm 유저 최대 200명이다. 지표는 Recall@10, NDCG@10, Coverage, ILD다. ILD는 리스트 안 임베딩이 얼마나 다른지다. 실험 전에 예측을 적고, 실측과 비교한 뒤 탈락을 문서에 남겼다.

최종 리스트에서 관련은 5점이다.

- 인기순: Recall@10 0.1900, NDCG@10 0.0698.
- iALS, rating 5 이상: Recall@10 0.0425, NDCG@10 0.0213.
- content FAISS, per_seed: Recall@10 0.0550, NDCG@10 0.0421.
- RRF(인기, iALS): Recall@10 0.1125, NDCG@10 0.0451.
- RRF(인기, content): Recall@10 0.1100, NDCG@10 0.0496.
- 재정렬 최고인 RRF(인기, content)와 CatBoost: Recall@10 0.0575, NDCG@10 0.0364.
- 카탈로그 단독 최고인 CatBoost: Recall@10 0.0400, NDCG@10 0.0275.

풀을 200개까지 넓히면 RRF(인기, content) Recall@200이 0.3500으로 인기순 0.3350보다 높다. 그 이득은 top-10까지 내려오지 않았다. 그래서 서빙 리스트는 인기순 단일이다. use_hybrid와 use_ranker는 기본 off다.

라벨을 느슨하게 뒀을 때도 같은 방향이었다. 리뷰만 있으면 정답이던 구간에서 인기순 Recall@10은 0.1689, XGBoost 재정렬 0.0938, LightGBM 0.0813, CatBoost 0.0650, iALS 최고(rating 5 이상) 0.1048, RRF(인기, iALS) 0.1114였다. 랭커는 인기 순서를 흔들면서 점수가 내려갔다.

iALS는 평점을 회귀하지 않고, 임계 미만 리뷰는 양성에서 뺐다. all 0.0475, 3점 이상 0.0450, 4점 이상 0.0675, 5점 이상 0.1048이다. 5점만 남겨도 학습량이 크게 줄지 않았고 4점 이하를 빼는 쪽이 나았다. 그래도 유저당 리뷰 중앙값 1인 롱테일에서 협업 필터링 단독은 인기순보다 약했다.

Two-Tower의 유저 벡터는 타깃 이전 5점 아이템 임베딩 평균이고 최대 10개다. 아이템 타워는 ID 임베딩 dim 64이고, 손실은 in-batch softmax다. train 유저의 90.3%는 리뷰 1개라 타깃을 빼면 히스토리가 없고, 5점 양성의 89.3%가 학습에서 빠졌다. 남은 학습 페어는 train의 6.6%인 18,768개다. 5 epoch 손실은 6.22에서 6.13이었다. Recall@10은 0.0000이라 API에 넣지 않았다.

Content를 유저 히스토리 시드로 쓸 때, 최근 구매를 평균하면 립스틱과 샴푸가 둘 다 아닌 점이 된다. 시드마다 검색하고 최대 코사인으로 합치는 per_seed가 나았다. 시드 2개 이상 49명에서 Recall@10이 0.0204에서 0.0510이 되었다. 전체도 0.0450에서 0.0525가 되었다. 서빙 모드는 per_seed다. 인기순에는 못 미쳤다.

RRF는 점수가 아니라 등수만 합친다. 식은 1/(60+rank)다. 가중합은 인기순 0.1689를 0.0400까지 깎았고, RRF는 그보다는 나았지만 세 조합 모두 인기순 이하였다. content를 세 채널에 넣으면 헤드가 밀려 더 내려갔다.

부스팅 랭커는 카탈로그 전체가 아니라 인기 top-200만 다시 줄 세웠다. 양성은 train에서 그 유저의 마지막 아이템이고 나머지는 hard negative다. 피처는 train 통계만 쓴다. log_pop_count, item_n, item_mean_rating, user_n, pop_rank, content_max_sim, ials_score, same_brand, same_category다. 리뷰 본문과 valid 평점은 피처로 쓰지 않았다. 5점 기준 양성-in-pop은 8,894명이고, 후보에 양성이 없어 버린 비율은 39.9%다. 트리 구현체만 바꿔도 인기순을 넘지 못했다.

DeepFM, LambdaMART, 채널별 랭커 재학습, RMSE는 하지 않았다. 같은 희소 라벨과 pop-200 후보에서 순서만 흔드는 모델이라 격자를 뒤집는 근거가 없다고 보고 닫았다. 이 결론은 All_Beauty 리스트 추천에만 해당한다.

#### 다양성

MMR은 인기 top-10 위에만 얹었다. 관련도와 이미 고른 상품과의 유사도를 같이 본다. lambda_diversity가 다양성 벌점이고, 관련도 가중은 1에서 람다를 뺀 값이다. 유사도는 콘텐츠 임베딩 코사인이다.

- 람다 0, 인기순: Recall@10 0.1900, NDCG@10 0.0698, ILD 0.759.
- 람다 0.3: Recall@10 0.1950, NDCG@10 0.0844, ILD 0.799.
- 람다 0.5, 서빙: Recall@10 0.1700, NDCG@10 0.0747, ILD 0.864.
- 람다 0.7: Recall@10 0.0275, NDCG@10 0.0113, ILD 0.913.

람다 0.5는 Recall을 0.1900에서 0.1700으로 조금 낮추고 ILD를 0.864까지 올렸다. 람다 0.7은 Recall 0.0275로 무너져서 뺐다. Recall을 크게 떨어뜨리지는 않았다는 말은 람다 0.5에 대한 말이다. 카테고리 개수는 데이터 자체가 하나라 다양성 지표로 쓸 수 없었고, 임베딩 거리인 ILD로 봤다.

신규 상품, 즉 train에 없는 ASIN을 content로 최대 20개 넣어도 top-10 히트는 0이었다. cold-user 200명에서 인기순 Recall@10은 0.0860, MMR 0.5는 0.0785다. cold-item 정답은 17건 전부 0이었다.

#### 쿼리 검색

쿼리 경로는 인기순과 섞지 않는다. 사용자 문장을 임베딩하고, 미리 만들어 둔 아이템 임베딩인 title, brand, description과 비교한 뒤 MMR을 적용한다.

검색 품질은 구매 Recall과 따로 쟀다. 영어 쿼리 20개를 ingredient, concern, product로 나누고, 제목, 브랜드, 설명에 특징 토큰이 있는지로 규칙 양성을 만들었다. 쿼리당 최대 40개다. 사람이 상품을 보고 다시 라벨한 정답은 아니다. 그 점을 문서에 명시했다.

1차인 content FAISS와 MMR은 mean Precision@10 0.360, Recall@10 0.097, 오탐 62, 미탐 692였다. 성분 쿼리인 retinol night cream Precision 0.90, hyaluronic acid serum 0.80이 고민이나 범용 쿼리보다 나았다. hydrating serum은 top-10 중 9개가 토큰 규칙을 깨는 오탐이었다. 임베딩이 세럼 옆의 크림을 가져왔다.

그다음 한 축만 고쳤다. 평가에 쓰는 쿼리에 한해 FAISS 풀에 같은 토큰 AND 게이트를 걸고 그다음 MMR을 했다. 통과분이 k보다 적으면 짧은 리스트를 그대로 반환하고 인기 상품으로 채우지 않았다. 재측정에서 Precision@10은 0.360에서 0.545, Recall@10은 0.097에서 0.133, 오탐은 62에서 0이 되었다. hydrating serum 오탐 9건은 0이 되었다. 오탐 0은 게이트가 평가 규칙과 같아서 나온 결과이므로, 사람 적합성의 증명으로 말하지 않는다. 브랜드 쿼리는 이 20개에 없다.

#### RAG와 LLM

LLM은 추천 Recall을 올리는 모델이 아니다. 이미 고른 ASIN 안에서 이유만 쓴다.

청크는 상품마다 둘로 나눈다. meta는 제목, 브랜드, 설명을 이어 512자에서 단어 경계로 자른다. review는 그 상품의 train 리뷰 중 최신 5개이고 역시 512자다. valid와 test 리뷰는 넣지 않는다.

설명 때 쿼리와 맞는 스니펫을 상품당 3개 고른다. 점수는 FAISS 유사도에 쿼리 토큰 겹침을 더하고, 토큰이 겹치는 리뷰 청크에는 0.25를 더해 메타보다 우선한다. UI는 그 영어 원문을 사유 아래에 보여 준다.

이유는 한글 한두 문장이고, 상품명과 브랜드명만 영어를 유지한다. 스니펫에 있는 내용만 쓴다. 가격, 재고, 스니펫에 없는 성분이나 효과를 만들지 않는다. 출력은 item_id와 reason의 JSON이다. temperature는 0.2이고 모델은 gpt-4o-mini다. 모델이 다른 item_id를 돌려주면 그 이유는 버린다. select_k가 0보다 크면 선택도 주어진 목록의 부분집합만 허용한다. API 키가 없으면 설명을 대체 문장으로 만들지 않고 503이다.

한 JSON에 상품 여러 개를 맡기면 사유가 비는 경우가 있어, 상품마다 호출하고 ThreadPool 기본 8로 병렬화했다. 토큰량은 같고 대기만 겹친다.

설명 보조 지표는 쿼리 20개와 데모 유저 5명, k는 5, 사유 125건이다. 후보 밖 ASIN은 0/125, 가격과 재고 과장은 0/125, 빈 사유는 0이다. 이유 평균은 약 66자다. 직렬이면 설명 p50이 약 5.4초이고, 벤치 한 번은 7.9초였다. 병렬 p50은 약 1.4초다. 추천 단계인 검색과 MMR은 약 92ms라 체감 지연은 거의 전부 LLM이다. 비용은 요청당 약 0.00030달러에서 0.00036달러다. 검색 게이트를 넣은 뒤 설명 대상 ASIN이 바뀌어서 같은 지표를 다시 쟀고, 환각 0과 빈 사유 0은 유지됐다.

#### 일하는 방식

평가 없는 모델은 README에 올리지 않는다. 서빙 기본을 바꿀 때는 숫자를 다시 잰다. 검색 게이트도 프롬프트는 그대로 두고 검색만 바꾼 뒤 Precision, 오탐, 설명 환각을 재측정했다. 규칙으로 만든 gold를 사람이 검수한 정답처럼 말하지 않는다. 예측을 먼저 적고 실측과 어긋난 곳도 EVAL에 남겼다. 예는 rating 3 이상이 all보다 약간 낮은 것, Recall@200 1위가 인기순이 아니라 RRF인 것이다.

#### 말해도 되는 것

Amazon All_Beauty에서 유저×상품 희소도가 99.9%를 넘었고, 유저당 리뷰 중앙값은 1이었다. XGBoost, LightGBM, CatBoost, iALS, content FAISS, RRF, Two-Tower를 같은 temporal split에서 비교했고, top-10은 인기순이 가장 좋았다. 랭킹 모델을 인기 후보 위에 얹으면 순서가 흔들리면서 Recall이 인기순보다 낮아졌다. 그래서 개인화 경로의 서빙 기본은 인기순으로 두고, 랭커는 플래그로만 남겼다. 쿼리 검색은 제목, 브랜드, 설명 임베딩의 content FAISS이고, MMR 람다 0.5로 Recall을 조금 양보해 리스트 다양성인 ILD를 올렸다. 람다 0.7은 Recall이 무너져서 쓰지 않았다. 설명은 검색과 다른 인덱스다. 상품 메타와 train 리뷰를 512자 청크로 나누고, 쿼리와 토큰이 겹치는 리뷰를 우선해 근거로 보여 준 뒤, LLM이 그 스니펫만으로 한국어 이유를 쓰게 했다. 후보에 없는 상품을 만들거나, 스니펫에 없는 가격, 재고, 성분을 말하는 경우는 평가 표본에서 0건이었다. 희소한 구매 기록에서는 랭킹 모델보다 인기순이 앞설 수 있고, 그때 서비스의 중심을 검색과 근거 있는 설명으로 옮겼다.

#### 말하면 안 되는 것

랭킹 모델이 인기순을 이겼다고 말하면 안 된다. 이기지 못했다. 사람이 라벨한 검색 정답으로 Precision 0.545를 받았다고 말하면 안 된다. 규칙 gold이고, 오탐 0은 그 규칙과 같은 게이트를 검색에 넣어서 나온 값이다. LLM이 추천 품질을 올렸다고 말하면 안 된다. LLM은 설명만 하고, 추천 지표와 섞지 않았다. 카테고리 다양성을 높였다고 말하면 안 된다. 이 카탈로그의 카테고리는 하나다. Two-Tower를 서비스에 넣었다고 말하면 안 된다. 학습 후 Recall@10이 0이라 빼 두었다. 클라우드에 공개 배포했거나 CI가 있다고 말하면 안 된다. Docker Compose까지이고, GitHub Actions와 공개 데모 배포는 아직이다.

주로 쓰는 기술은 Python, FastAPI, OpenAI, FAISS, PyTorch, LightGBM, Spring Boot, JPA, JWT, MySQL, Redis, Docker입니다.

## Interests

LangGraph와 LangChain으로 개인 질의응답을 만드는 데 관심이 있습니다. 추천 검색과 LLM 설명을 한 서비스로 잇는 일도 관심사입니다.
