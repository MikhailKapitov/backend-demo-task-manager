package com.example.task_service.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "\"Task\"")
public class Task {

    // id, title, description, status, createdAt, updatedAt

    @Id
    @GeneratedValue(generator = "UUID")
    @GenericGenerator(name = "UUID", strategy = "org.hibernate.id.UUIDGenerator")
    @Column(name = "id", columnDefinition = "BINARY(16)", nullable = false)
    private UUID id;
    
    @Column(name = "title")
    private String title;

    @Column(name = "description")
    private String description;

    // 0 (todo), 1 (in_progress), 2 (done)
    @Column(name = "status", nullable = false)
    private Integer status = 0;

    @Column(name = "created_at", updatable = false, nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @PrePersist
    protected void onCreate() {
        
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        
        return;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
        return;
    }

}
