package com.lexilegal;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class LexiLegalApplication {

    public static void main(String[] args) {
        SpringApplication.run(LexiLegalApplication.class, args);
    }
}

