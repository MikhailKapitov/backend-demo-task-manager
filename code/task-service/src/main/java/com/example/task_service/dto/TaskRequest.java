package com.example.task_service.dto;

// import java.util.UUID;
import java.time.LocalDateTime;

public record TaskRequest(

    // id, title, description, status, createdAt, updatedAt

    String title,
    String description,
    Integer status,
    String userId

) {}
