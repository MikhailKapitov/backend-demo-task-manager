package com.example.task_service.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.Map;

@FeignClient(name = "jwt-service")
public interface JwtClient {

    @PostMapping("/api/token/verify")
    Map<String, Object> verifyToken(@RequestBody Map<String, String> request);

}
