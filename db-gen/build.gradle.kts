// 행정안전부 원천 파일을 읽어 엔진 자료로 만드는 배치입니다.
// 하위 컴포넌트는 원천 복원과 엔진 전환 2개입니다.
// refine-core를 의존하지 않습니다. 두 구성 요소는 서로를 호출하지 않고 엔진 DB 하나로만 만납니다.
// 근거는 design/01-scope.md 6-2절입니다.
plugins {
    id("org.springframework.boot")
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter")
}
