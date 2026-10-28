# Sample Microservices App

This is a realistic, intentionally decoupled microservices application used as a testbed for the CloudChange analysis tool.

## Architecture & Dependency Graph

```mermaid
graph TD
    Frontend[Frontend (NGINX)] --> Gateway[API Gateway]
    Gateway --> Order[Order Service]
    Order --> Payment[Payment Service]
    Order --> User[User Service]
    Payment --> DB[(PostgreSQL)]
```

### Components
1. **Frontend:** Static HTML/JS served by NGINX. Triggers checkout.
2. **API Gateway:** Entry point for API calls. Routes `/api/checkout` to Order Service.
3. **Order Service:** Orchestrates the order. Calls User Service to validate the user, then calls Payment Service to process payment.
4. **Payment Service:** Simulates payment processing and records transaction to Database.
5. **User Service:** Manages user data.
6. **PostgreSQL:** Backing database for Payment Service (Mocked connection).

## Running Locally

Each service is a FastAPI app (except Frontend) and has its own `Dockerfile` and `requirements.txt`. They can be run independently using `uvicorn main:app --port <port>` or containerized via Docker.
