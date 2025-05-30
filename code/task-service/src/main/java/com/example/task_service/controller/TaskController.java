package com.example.task_service.controller;

import com.example.task_service.dto.TaskRequest;
import com.example.task_service.dto.TaskResponse;
import com.example.task_service.model.Task;
import com.example.task_service.service.TaskService;

import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

import org.springframework.security.core.Authentication;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    // TODO: Add userId verification.

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    // @GetMapping
    // public ResponseEntity<List<TaskResponse>> getAllTasks() {
    //     List<TaskResponse> responses = taskService.getAllTasks()
    //         .stream()
    //         .map(this::convertToResponse)
    //         .collect(Collectors.toList());
    //     return ResponseEntity.ok(responses);
    // }

    @GetMapping("/{id}")
    public ResponseEntity<TaskResponse> getTaskById(@PathVariable("id") UUID id, Authentication authentication) {
        
        Optional<Task> opt = taskService.getTaskById(id);
        
        if (!opt.get().getUserId().toString().equals(authentication.getName())){
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        return opt.map(task -> ResponseEntity.ok(convertToResponse(task)))
                  .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @GetMapping("/get-specific")
    public ResponseEntity<List<TaskResponse>> getFilteredTasks(
        @RequestParam(required = false) Integer status, Authentication authentication
    ) {

        String userId = authentication.getName();
        
        List<Task> tasks = taskService.getTasksByUserIdAndStatus(userId, status);
        
        List<TaskResponse> responses = tasks.stream()
            .map(this::convertToResponse)
            .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    @PostMapping
    public ResponseEntity<TaskResponse> createTask(@Valid @RequestBody TaskRequest request, Authentication authentication) {

        String userId = authentication.getName();
        
        Task task = new Task();
        task.setTitle(request.title());
        task.setDescription(request.description());
        task.setStatus(request.status());
        task.setUserId(userId);

        Task created = taskService.saveTask(task);
        return ResponseEntity.status(HttpStatus.CREATED)
                             .body(convertToResponse(created));
    }

    @PutMapping("/{id}")
    public ResponseEntity<TaskResponse> updateTask(
        @PathVariable("id") UUID id,
        @Valid @RequestBody TaskRequest request,
        Authentication authentication
    ) {
        
        Optional<Task> opt = taskService.getTaskById(id);
        if (opt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        if (!opt.get().getUserId().toString().equals(authentication.getName())){
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }

        Task toUpdate = opt.get();
        toUpdate.setTitle(request.title());
        toUpdate.setDescription(request.description());
        toUpdate.setStatus(request.status());

        Task updated = taskService.saveTask(toUpdate);
        return ResponseEntity.ok(convertToResponse(updated));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable("id") UUID id, Authentication authentication) {
        if (taskService.getTaskById(id).isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        if (!taskService.getTaskById(id).get().getUserId().toString().equals(authentication.getName())){
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        taskService.deleteTask(id);
        return ResponseEntity.noContent().build();
    }

    private TaskResponse convertToResponse(Task task) {
        return new TaskResponse(
            task.getId(),
            task.getTitle(),
            task.getDescription(),
            task.getStatus(),
            task.getCreatedAt(),
            task.getUpdatedAt(),
            task.getUserId()
        );
    }
}
