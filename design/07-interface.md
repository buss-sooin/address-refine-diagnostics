# 설계7: 인터페이스 정의서

이 문서는 정제 코어와 API 서비스의 인터페이스를 정합니다. 짝이 되는 그림은 `component-uml.drawio`이고, 처리 흐름은 `03-pipeline.md`에 있습니다.
여러 설계 문서에 흩어져 있던 규칙마다 그 규칙을 지키는 구조를 정리했습니다.

자바 타입 이름은 후보이고 구현 단계에서 확정합니다.

---

## 1. 용어

패턴 이름은 외래어 표기로 적고 원어를 병기합니다.

| 말 | 원어 | 비고 |
|---|---|---|
| 스트래티지 패턴 | Strategy | 업무 용어 「전략」(교정 전략·검출 전략)과 겹치므로 패턴은 외래어로 적어 구분합니다 |
| 컴포지트 패턴 | Composite | |
| 템플릿 메서드 패턴 | Template Method | |
| 컨텍스트 객체 | Context | |
| 포트와 어댑터 | Ports and Adapters | Hexagonal 아키텍처라고도 합니다 |
| 리절트 객체 | Result | GoF 목록에 없는 관용 기법입니다 |
| 오케스트레이터 | Orchestrator | 단계를 차례로 호출하는 객체입니다 |

---

## 2. 원칙 4가지

구조는 아래 규칙 4가지에서 나왔습니다.

| # | 원칙 | 근거 |
|---|---|---|
| 1 | 실패는 예외가 아니라 value로 돌려줍니다 | 이 솔루션이 제공하는 가치는 정제된 주소가 아니라 사용자가 바로 조치할 수 있는 실패 사유입니다 (`01-scope.md` 1절) |
| 2 | 단계의 호출 순서는 한 곳만 압니다 | 지번 뒤에 도로명이 다시 오는 입력이 있고, `AddressBranch` 구현은 앞으로 늘어납니다 (`03-pipeline.md` 상태 전이표) |
| 3 | 케이스를 나열하지 않고 규칙으로 구현합니다 | 이 프로젝트는 케이스마다 정규식을 덧붙이던 방식을 없애려고 시작했습니다 |
| 4 | 코어는 저장소를 포트로만 조회하고 외부 주소 서비스는 호출하지 않습니다 | 카카오 API의 지연과 장애가 CS 위험으로 이어졌습니다 (`01-scope.md` 2절 문제 3, 4절) |

---

## 3. 패턴 6가지

| 패턴 | 적용 부분 | 의도 | 근거 규칙 | 어긋난 구현 |
|---|---|---|---|---|
| 리절트 객체 | 모든 단계의 반환 value | 실패를 value로 돌려줘야 사유를 제공할 수 있습니다 | 원칙 1 | 못 찾으면 예외를 던지고, 받는 쪽에는 "실패"만 남습니다 |
| 스트래티지 | `ResponseStrategy` | 처리는 하나로 두고 반환 모양만 소비자에 맞춥니다 | 교정 전략과 검출 전략의 반환 value를 같은 모양으로 맞추지 않습니다 | 반환 타입이 하나이고 그 안에 「교정이면」 분기가 생깁니다 |
| 템플릿 메서드 | `RefineOrchestrator` | 순서를 한 곳에 두어 단계를 건너뛸 수 없게 합니다 | `ExistenceVerifier`의 실재 확인을 건너뛰지 않습니다 | 단계가 다음 단계를 직접 호출합니다 |
| 컨텍스트 객체 | `RefineContext` | 단계가 서로를 모르는 채로 값을 다음 단계에 넘깁니다 | 버린 토큰을 감추지 않습니다 · 무상태 | 버린 토큰이 지역 변수에 있다가 사라집니다 |
| 컴포지트 | `AddressBranch` 구현 3개 | 구현을 모두 실행해야 교집합이 나옵니다 | `AddressBranch` 구현에 우선순위를 두지 않습니다 | 구현 하나를 골라 호출합니다 |
| 포트와 어댑터 | 자원 포트 3개 | 저장소 구현이 바뀌어도 코어를 고치지 않습니다 | 원칙 4 | 코어가 DB나 사전 구현을 직접 조회합니다 |

### 구조가 같아도 쓰는 방식이 반대인 인터페이스 2개

`AddressBranch`와 `DictionarySearcher`는 둘 다 인터페이스 하나에 구현이 여럿인 구조입니다. 그러나 구현을 쓰는 방식은 정반대입니다.

| | `AddressBranch` | `DictionarySearcher` |
|---|---|---|
| 구현을 쓰는 방식 | 모두 실행하고 결과를 합칩니다 | 하나를 골라 그것만 씁니다 |
| 패턴 | 컴포지트 | 스트래티지 |
| 자바에서 주입받는 것 | 구현 목록 | 구현 하나 |
| 근거 | 「`AddressBranch` 구현에 우선순위를 두지 않습니다」 | 「다른 검색 방법을 더할 때는 구현을 하나 더 만들어 교체합니다」 |

두 인터페이스를 「인터페이스와 구현」이라고만 적으면 `AddressBranch`에서도 구현 하나만 고르는 코드가 나오고, 그러면 교집합을 만들 수 없습니다.

---

## 4. 인터페이스 15개

### 4-1. `RefineOrchestrator`만 호출하는 단계 8개

| 단계 | 자바 타입 이름 | `RefineContext`에서 읽는 것 | `RefineContext`에 적는 것 |
|---|---|---|---|
| 파서 | `AddressParser` | 원문 · 우편번호 · 전략 value | 토큰 목록 · 고쳐 읽은 부분 |
| 관문 | `AddressGate` | 토큰 목록 | 주소 여부 |
| 표기 구분 | `NotationClassifier` | 토큰 목록 | 성립하는 표기 집합 |
| 갈래 | `AddressBranch` | 토큰 목록 · 전략 value · 좁힌 범위 | 구현별 후보 집합 · 층 결과 |
| 행정동 판정 | `AdminDongJudge` | 토큰 목록 | 사유 |
| 합치기 | `CandidateMerger` | 구현별 후보 집합 | 건물 후보 집합 · 버린 토큰 목록 |
| 실재 확인 | `ExistenceVerifier` | 건물 후보 · 상세 토큰 · 전략 value | 살아남은 후보 · 상세 확정 수준 |
| 응답 판정 | `ResultGrader` | 후보 · 버린 토큰 · 상세 확정 수준 · 전략 value | 등급 · 사유 |

#### 단계마다 맡는 일과 하지 않는 일

| 자바 타입 이름 | 맡는 일 | 하지 않는 일 |
|---|---|---|
| `AddressParser` | 단위 표기 글자로 끊고 사전에서 찾습니다 | 옳고 그름을 정하지 않습니다. 좁힌 범위의 후보 목록을 만들지 않습니다 |
| `AddressGate` | 주소로 볼 만한 입력인지 구분합니다 | 옳은 주소인지 판단하지 않습니다. 단위 표기가 있는지로 판단하지 않습니다 |
| `NotationClassifier` | 성립하는 표기를 모두 표시합니다 | 표기 4가지 중 하나를 고르지 않습니다 |
| `AddressBranch` | 후보 집합을 만듭니다 | 건물을 하나로 정하지 않습니다 |
| `AdminDongJudge` | 입력에 행정동이 쓰였다는 사실과 사유를 만듭니다 | 후보를 찾지 않습니다. 실재 확인을 거치지 않습니다 |
| `CandidateMerger` | 후보를 건물 단위로 맞춰 교집합이나 합집합을 냅니다 | `AddressBranch` 구현에 우선순위를 두지 않습니다 |
| `ExistenceVerifier` | DB에 있는 후보만 남깁니다 | 유사도로 순위를 매기지 않습니다 |
| `ResultGrader` | 등급과 사유를 각각 정합니다 | 후보가 하나로 좁혀졌다고 버린 토큰을 감추지 않습니다 |

`AddressBranch`의 구현 3개는 같은 인터페이스를 구현합니다. `RoadBranch` · `LotBranch` · `BuildingNameBranch`는 받는 value와 반환 value의 모양이 같고 내부 처리만 다릅니다.

### 4-2. 여러 단계가 함께 호출하는 판정 부품 2개

| 부품 | 자바 타입 이름 | 호출하는 쪽 | 입력 value | 반환 value |
|---|---|---|---|---|
| 층 판정기 | `LevelJudge` | `AddressParser` · `RoadBranch` · `BuildingNameBranch` | 토큰 · 층 이름 · 허용 오타 | 층 결과 2개 |
| 후보 검색기 | `DictionarySearcher` | `LevelJudge` | 토큰 · 층 이름 | 후보 목록. 후보마다 유사도가 붙습니다 |

`LotBranch`는 `LevelJudge`를 호출하지 않습니다. 건물번호와 지번은 정확 일치로 판정하고 유사도를 재지 않기 때문입니다.

### 4-3. 구현이 코어 밖에 있는 자원 포트 3개

| 포트 | 자바 타입 이름 | 호출하는 쪽 | 포트 뒤에 있는 것 |
|---|---|---|---|
| 사전 조회 | `DictionaryPort` | `DictionarySearcher` | 메모리 상주 사전 5개 |
| 참조 조회 | `ReferencePort` | `ExistenceVerifier` | 엔진 DB · `ref` |
| 설정 조회 | `ConfigPort` | `LevelJudge` · `ResultGrader` | `svc.config` |

### 4-4. 반환 value를 만드는 인터페이스

| 이름 | 자바 타입 이름 | 구현 |
|---|---|---|
| 응답 조립 | `ResponseStrategy` | 교정 전략 · 검출 전략 |

교정 전략은 확정 주소나 사용자가 고를 후보 목록을 돌려주고, 검출 전략은 처리 결과 전체와 실패 목록을 돌려줍니다. 두 반환 value를 같은 모양으로 맞추지 않습니다.

### 4-5. 정제 전체를 교체하는 확장 인터페이스

| 이름 | 자바 타입 이름 | 호출하는 쪽 | 구현 |
|---|---|---|---|
| 정제 | `AddressRefiner` | 교정 진입점 · 검출 진입점 | `RefineOrchestrator` |

진입점은 `RefineOrchestrator` 대신 `AddressRefiner` 타입으로 받습니다. 외부 주소 서비스는 이 인터페이스의 다른 구현으로만 붙일 수 있고, 지금은 그 구현을 만들지 않습니다.

---

## 5. `RefineContext`

`RefineContext`는 요청 하나를 처리하는 동안만 존재하고, 요청이 끝나면 버립니다. 요청이 끝난 뒤에도 남으면 그 자체가 상태가 되어 무상태 설계가 깨집니다.

| 필드 | 적는 단계 | 읽는 단계 |
|---|---|---|
| 원문 · 우편번호 · 전략 value · 설정식별자 | 진입점 | 모든 단계 |
| 토큰 목록 | `AddressParser` | `AddressGate` · `NotationClassifier` · `AddressBranch` · `AdminDongJudge` |
| 고쳐 읽은 부분 | `AddressParser` | `ResultGrader` |
| 주소 여부 | `AddressGate` | `RefineOrchestrator` |
| 성립하는 표기 집합 | `NotationClassifier` | `RefineOrchestrator` |
| 구현별 후보 집합 | `AddressBranch` | `CandidateMerger` |
| 층 결과 | `AddressParser` · `AddressBranch` | `ResultGrader` |
| 건물 후보 집합 | `CandidateMerger` · `ExistenceVerifier` | `ExistenceVerifier` · `ResultGrader` |
| 버린 토큰 목록 | `CandidateMerger` | `ResultGrader` |
| 상세 확정 수준 | `ExistenceVerifier` | `ResultGrader` |
| 등급 · 사유 | `AdminDongJudge` · `ResultGrader` | `ResponseStrategy` |

토큰 하나에는 원문 위치, 토큰 값, 걸린 층, 사전에서 찾았는지, 정확히 맞았는지 아니면 닮은 이름만 있었는지가 담깁니다.

---

## 6. 코드의 의도를 검사하는 구조 검사 규칙 8가지

구현 코드를 한 줄씩 읽는 대신 아래 8가지를 확인합니다.

| 확인할 것 | 어긋난 구현 | 깨진 규칙 |
|---|---|---|
| `AddressBranch` 구현을 목록으로 주입받는가 | 구현 하나를 골라 호출합니다 | `AddressBranch` 구현에 우선순위를 두지 않습니다 |
| 단계가 다른 단계를 호출하는가 | `AddressParser`가 `AddressGate`를 호출합니다 | 단계의 호출 순서는 한 곳만 압니다 |
| `ExistenceVerifier`를 거치지 않는 경로가 있는가 | 유사도만 보고 바로 응답합니다 | 실재 확인을 건너뛰지 않습니다 |
| 버린 토큰이 `RefineContext`에 적히는가 | 지역 변수에 있다가 사라집니다 | 버린 토큰을 감추지 않습니다 |
| 등급과 사유가 칼럼 2개인가 | 한 칼럼에 합쳐 있습니다 | 등급과 사유를 합치지 않습니다 |
| 코어가 외부 주소 서비스를 아는가 | 코어에 카카오 호출 코드가 있습니다 | 코어는 외부 주소 서비스를 호출하지 않습니다 |
| 허용 오타를 어디서 가져오는가 | 코드에 하드코딩되어 있습니다 | 허용 오타는 설정 value로 두고 실행마다 기록합니다 |
| `RefineContext`가 요청보다 오래 남는가 | 필드나 캐시에 보관합니다 | 무상태 |
