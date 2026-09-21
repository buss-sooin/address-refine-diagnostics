// 빌드 단위 3개를 묶습니다. Gradle은 이것을 「프로젝트」라 부르지만
// 문서와 대화에서는 「빌드 단위」라 부르고, 「모듈」은 design/03-pipeline.md 0절의 처리 단위를 가리킵니다.
rootProject.name = "address-refine-diagnostics"

include("db-gen", "refine-core", "refine-api")
