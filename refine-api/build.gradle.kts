// 교정과 검출 진입점 2개를 나눠 받고, 전략에 맞는 형태로 응답을 조립합니다.
// 실행되는 Spring Boot 앱입니다. 근거는 design/01-scope.md 6-4절입니다.
plugins {
    id("org.springframework.boot")
}

dependencies {
    implementation(project(":refine-core"))
    implementation("org.springframework.boot:spring-boot-starter-web")
}
