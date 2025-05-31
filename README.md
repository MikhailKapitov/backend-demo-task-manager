# backend-demo-task-manager

A simple backend for a REST API CRUD task manager.

Main tech. used:

- Java + Spring;
- Python (To show off that that's what microservices are good with) + Flask (Kinda new to Flask, haven't done stuff with it in a while);
- SQL;
- JWT (New to the refresh stuff);
- Argon2 for password hashing;
- Microservice architecture using Eureka + API Gateway.

To boot Java microservices: 
```bash
mvn spring-boot:run
```
(Or use a relevant provided Maven script.)

To start up Python microservices:
```bash
pip install -r requirements
python3 main.py
```
(Or "python" instead of "python3".)
