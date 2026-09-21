// 부모 빌드 스크립트입니다. 버전 번호와 공통 설정만 담습니다.
plugins {
    id("org.springframework.boot") version "4.1.1" apply false
}

allprojects {
    group = "com.address.refine.diagnostics"
    version = "0.1.0-SNAPSHOT"
}

subprojects {
    apply(plugin = "java")

    extensions.configure<JavaPluginExtension> {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(21))
        }
    }

    repositories {
        mavenCentral()
    }

    tasks.withType<JavaCompile>().configureEach {
        options.encoding = "UTF-8"
    }

    tasks.withType<Test>().configureEach {
        useJUnitPlatform()
    }

    dependencies {
        // Spring Boot BOM으로 의존성 버전을 맞춥니다. 빌드 단위마다 버전을 적지 않습니다.
        "implementation"(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))
        "testImplementation"("org.springframework.boot:spring-boot-starter-test")
        "testRuntimeOnly"("org.junit.platform:junit-platform-launcher")
    }
}
