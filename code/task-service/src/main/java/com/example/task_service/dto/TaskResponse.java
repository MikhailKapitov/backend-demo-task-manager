package com.example.task_service.dto;

import java.util.UUID;
import java.time.LocalDateTime;

public record TaskResponse(

    // id, title, description, status, createdAt, updatedAt

    UUID id,
    String title,
    String description,
    Integer status,
    LocalDateTime createdAt,
    LocalDateTime updatedAt,
    String userId

) {}
