package com.lexilegal.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("LexiLegal AI API")
                .version("1.0.0")
                .description("Backend REST API for LexiLegal AI legal document simplification")
                .contact(new Contact().name("LexiLegal Team")));
    }
}

