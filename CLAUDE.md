# CLAUDE.md: address-refine-diagnostics

이 저장소에서 코드를 만들 때 지킬 것만 담습니다.
무엇을 만드는 물건인지와 왜 그렇게 정했는지는 `design/`에 있고 여기에 옮겨 적지 않습니다.
프로젝트를 어떻게 진행하는지는 Claude 프로젝트 「주소정제 솔루션」이 맡습니다.

---

## 1. 기억으로 코드를 쓰지 않습니다

칼럼 이름, 자릿수, 기본 키, 코드값, 모듈 이름, 물리명은 아래 파일을 열어 확인한 뒤에 씁니다.

| 찾는 것 | 어디 |
|---|---|
| 칼럼 이름 · 자릿수 · 기본 키 | `design/06-source-schema.md` 2절 자료별 ERD, 5절 전체 관계 ERD |
| 코드값 | `design/04-source-data.md` 6절 |
| 테이블과 칼럼의 물리 정의 | `design/02-data-model.md` 6절 |
| 모듈 이름 | `design/03-pipeline.md` 0절 「모듈 이름」 |
| 단계별 처리 순서 | `design/03-pipeline.md` 2절 |
| 인터페이스 15개와 책임 | `design/07-interface.md` 4절 |
| 구조 검사 규칙 8가지 | `design/07-interface.md` 6절 |
| 적재 순서와 갱신 흐름 | `design/04-source-data.md` 8절 |
| 기대 정제 값 케이스 | `design/05-expected-results.md` 4절 |
| 업무 용어 | `design/01-scope.md` 0절 |
| 물리명 (테이블·칼럼) | `design/standard-dict/표준용어정의서.csv` |
| 사유코드 18개 | `design/standard-dict/사유코드정의서.csv` |

`04-source-data.md`와 `06-source-schema.md`는 분량이 많습니다. 전체를 읽지 말고 필요한 절만 읽습니다.

**설계 문서에 없는 규격·자릿수·코드값을 만들어 내지 않습니다.** 설계 문서에 없으면 원천 자료를 직접 열어 확인하고, 그래도 못 닫으면 그 자리에서 사용자에게 묻습니다. 확인 필요 표시를 파일에 남기지 않습니다.

---

## 2. `design/`은 고치지 않습니다

**이 저장소의 `design/`이 설계 문서의 정본입니다.** 2026-09-13에 정했습니다.

코딩하면서 설계와 달라지는 것이 생기면 설계 문서를 고치지 않고 구현본을 별도 파일로 만듭니다. 설계 기준선이 커밋 `93489c9`이고, 그 시점의 문서를 고치면 설계와 구현 사이의 궤적이 사라집니다.

예외는 이름입니다. 자바 타입 이름은 `design/07-interface.md` 4절의 이름을 그대로 쓰고, 바꿔야 할 이유가 생기면 그 표도 함께 고칩니다. 사용자에게 알리지 않고 다른 이름을 쓰지 않습니다.

---

## 3. 코드가 지킬 불변 조건 2가지

**런타임 경로에 LLM 호출을 넣지 않습니다.** 표준 주소인지 판정하는 일, 닮은 이름을 후보로 제안하는 일, 후보가 실재하는지 확인하는 일은 전부 코드가 합니다.

**지역을 코드에 고정하지 않습니다.** 서울을 하드코딩하지 않고 행정구역 단계 수도 고정하지 않습니다. 지역 값을 늘리는 것만으로 확장되는 구조로 만듭니다.

나머지 구조 규칙 8가지는 `design/07-interface.md` 6절이 정본입니다. 검사 대상은 `AddressBranch` 주입 방식, 단계 간 호출, `ExistenceVerifier` 우회, 버린 조각 기록, 등급과 사유의 칼럼 수, 코어의 카카오 의존, 허용 오타의 출처, `RefineContext`의 수명입니다. **ArchUnit 테스트가 아직 없어도 규칙은 지킵니다.**

---

## 4. 빌드 단위 4개

```
address-refine-diagnostics/
  settings.gradle.kts  빌드 단위 3개를 묶습니다
  build.gradle.kts     부모 빌드 스크립트. 버전 번호와 공통 설정만 담습니다
  db-gen/         원천 파일을 읽어 엔진 자료를 만드는 배치입니다
  refine-core/    정제 로직 전체. 단계 모듈 8개, RefineOrchestrator, 자원 포트 인터페이스
  refine-api/     교정·검출 진입점과 ResponseStrategy 구현. 실행되는 Spring Boot 앱입니다
```

| 빌드 단위 | 의존 | 근거 |
|---|---|---|
| `db-gen` | `refine-core`를 의존하지 않습니다 | `design/01-scope.md` 6-2절 |
| `refine-core` | Spring Boot 기본 의존성만 | `design/07-interface.md` 2절 원칙 4 |
| `refine-api` | `refine-core` | `design/01-scope.md` 6-4절 |

**`refine-core`의 `build.gradle.kts`에 외부 서비스 라이브러리를 넣지 않습니다.** 카카오나 T맵을 쓰는 코드가 생기면 `provider-*` 또는 `adapter-*` 빌드 단위를 새로 만들고 그 단위가 `refine-core`를 의존하게 합니다. 의존 방향이 반대가 되면 코어가 카카오에 의존하지 않는지 검사하는 규칙이 뜻을 잃습니다.

확장용 빌드 단위는 구현이 생기는 날 만듭니다. 빈 단위를 미리 만들지 않습니다.

「모듈」과 「빌드 단위」를 구분해 씁니다. 모듈은 `AddressParser`처럼 정제 흐름을 구성하는 처리 단위이고, 빌드 단위는 `refine-core`처럼 `build.gradle.kts`를 하나 가진 폴더입니다.

---

## 5. 기술 스택

| 대상 | 값 |
|---|---|
| 자바 | 21 LTS |
| 빌드 도구 | Gradle 9.7.x. Kotlin DSL이고 래퍼(`./gradlew`)로 실행합니다 |
| Spring Boot | 4.1.x |
| DB | PostgreSQL 18 |
| 그룹과 버전 | `com.address.refine.diagnostics` · `0.1.0-SNAPSHOT` |

자바 패키지는 그룹 이름을 루트로 삼아 나눕니다. 이 값들을 바꾸자고 먼저 제안하지 않습니다.

---

## 6. 검사 명령

| 목적 | 명령 | 실행 시점 |
|---|---|---|
| 수정한 빌드 단위만 컴파일 | `./gradlew --offline :<빌드 단위>:compileJava` | 파일을 수정한 직후 |
| 구조 검사 8가지 | `./gradlew --offline :refine-core:test --tests 'Arch*Test'` | 작업을 마칠 때 |
| 전체 빌드와 테스트 | `./gradlew --offline clean build` | 커밋하기 전 |

`--offline`은 의존성을 내려받지 않고 캐시만 씁니다. 의존성을 바꾼 뒤 처음 한 번은 `--offline` 없이 실행해 내려받습니다. Gradle은 데몬이 JVM을 띄워 둔 채 재사용하므로 두 번째 호출부터 빨라집니다.

`mvn`이나 전역 `gradle` 명령을 쓰지 않습니다. 저장소의 래퍼가 정해 둔 Gradle 버전으로만 실행합니다.

**ArchUnit을 파일마다 실행하지 않습니다.** 모든 클래스를 훑는 검사라 느립니다. 수정 직후에는 컴파일만 보고 구조 검사는 작업을 마친 뒤에 실행합니다.

ArchUnit 테스트는 아직 없습니다. 그동안 구조 검사 명령은 「No tests found」로 실패합니다. 이 실패는 테스트가 없다는 뜻이지 규칙 위반이 아닙니다.

`tools/`의 생성기 4개는 이 저장소에서 실행되지 않습니다. 입력으로 쓰는 `reference/` 폴더가 여기 없습니다. 표준 사전을 다시 만들어야 하면 작업장에서 실행하고 결과 파일만 옮겨 옵니다.

---

## 7. 코드에 쓰는 말

파일명은 영문 소문자와 하이픈으로 짓고 내용은 한국어로 씁니다. 예외는 `design/standard-dict/`의 CSV뿐이고 사람이 직접 여는 산출물이라 한글 이름을 씁니다.

주석과 커밋 메시지의 어미는 「~합니다」로 씁니다.

**번호나 기호만으로 대상을 가리키지 않습니다.** 「③에서 처리합니다」가 아니라 「`ExistenceVerifier`에서 처리합니다」로 적습니다. 번호를 꼭 써야 하면 `A1(필수 단위 표기 누락)`처럼 이름을 함께 적습니다.

자세한 규칙은 `.claude/rules/writing.md`에 있습니다.
