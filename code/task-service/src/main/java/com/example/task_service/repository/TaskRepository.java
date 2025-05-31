package com.example.task_service.repository;

import com.example.task_service.model.Task;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;
import java.util.List;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface TaskRepository extends JpaRepository<Task, UUID> {
	@Query("SELECT t FROM Task t WHERE t.userId = :userId AND (:status IS NULL OR t.status = :status)")
    List<Task> findByUserIdAndStatus(@Param("userId") String userId, @Param("status") Integer status);
}
