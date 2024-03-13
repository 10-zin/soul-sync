# soul-sync
An AI wingman to sync souls across the globe.

## Set Up
1. [Install VS Code](https://code.visualstudio.com/)
2. [Install Docker](https://code.visualstudio.com/docs/devcontainers/tutorial#_install-docker)
3. [Install VS Code Dev Containers Extension](https://code.visualstudio.com/docs/devcontainers/tutorial#_install-the-extension)
4. Clone this repository
5. Copy `.env.example` to `.env` and fill in the necessary environment variables.
    - Update `OPENAI_API_KEY` with your open ai api key. Make sure you add your payment details and purchase some credits to use the API. $5 should be more than enough.
6. Run
    ```
    uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
    ```

## Database Migrations
To manage database migrations in a FastAPI application with SQLAlchemy models, you can use Alembic, a lightweight database migration tool designed for use with SQLAlchemy. The process typically involves initializing Alembic in your project, creating migration scripts, and then applying these migrations to your database. Below is a step-by-step guide on how to do this:

### Step 1: Create a Migration Script
Whenever you modify your models (like adding `a_new_description` column to `Item`), generate a new migration script:
```
alembic revision --autogenerate -m "Add a_new_description to items"
```
Alembic will compare your database schema (as defined by your SQLAlchemy models) against the actual database schema and generate a migration script in the `alembic/versions` directory.

### Step 2: Review the Migration Script
Check the generated script in the `alembic/versions` directory to make sure it accurately represents the changes you want to make. Alembic attempts to auto-generate the correct migration commands, but it's a good practice to review and manually adjust them if necessary.

### Step 3: Apply Migrations
To apply the migrations to your database, run:
```
alembic upgrade head
```
This command applies all pending migrations to the database.

## Development
- If for some reason VS code is acting up, you can always reload the window by pressing `Cmd + Shift + P` and typing `Reload Window` or `Dev Containers: Rebuild Container`

To test the server:

### To Sign Up
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/users' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "ray",
  "email": "ruizehung@gatech.edu",
  "password": "password"
}'
```

### To Login
```bash
curl -X POST -F 'username=ray' -F 'password=password' http://localhost:8000/token
```

### To Start a Conversation with AI Wingman
```bash
curl -X POST -H 'Authorization: Bearer your_access_token_here' http://localhost:8000/soul_sync/ai_wingman_initiate_conversation
```

### To Add User Message to a Conversation with AI Wingman
```bash
curl -X 'POST' \
  'http://localhost:8000/soul_sync/ai_wingman_conversation' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_access_token_here' \
  -d '{
  "conversation_id": "...",
  "content": "I had a nice dinner!"
}'
```

### To get conversations for a user
```bash
curl -X 'GET' \
  'http://localhost:8000/conversations/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_access_token_here'
```

### To get messages in a conversation
```bash
curl -X 'GET' \
  'http://localhost:8000/conversations/{conversation_id}/messages/?offset=0&limit=10' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_access_token_here'
```