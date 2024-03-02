# soul-sync
An AI wingman to sync souls across the globe.

## Set Up
1. [Install VS Code](https://code.visualstudio.com/)
2. [Install Docker](https://code.visualstudio.com/docs/devcontainers/tutorial#_install-docker)
3. [Install VS Code Dev Containers Extension](https://code.visualstudio.com/docs/devcontainers/tutorial#_install-the-extension)
4. Clone this repository
5. Copy `.env.example` to `.env` and fill in the necessary environment variables.
    - Update `OPENAI_API_KEY` with your open ai api key
6. Run
    ```
    python db_setup.py
    uvicorn soul_sync_chat_api:app --host 0.0.0.0 --port 8000 --reload
    ```

## Development
- If for some reason VS code is acting up, you can always reload the window by pressing `Cmd + Shift + P` and typing `Reload Window` or `Dev Containers: Rebuild Container`

To test the server:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/soul_sync/ai_wingman_chat/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text_message": "Hey this is Tenzin, wassup?",
  "from_id": "user123",
  "to_id": "user000"
}'
```