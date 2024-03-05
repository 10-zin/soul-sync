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
    python db_setup.py
    uvicorn src.soul_sync_chat_api:app --host 0.0.0.0 --port 8000 --reload
    ```

### NOTE:
> This repo is an embarrasement to all TDD followers (incl. us). Patience is key, if we get time and interest, tests shall be added and TDD shall be followed :) Till then.. we gotta meet our asignment deadlines!

## Development
- If for some reason VS code is acting up, you can always reload the window by pressing `Cmd + Shift + P` and typing `Reload Window` or `Dev Containers: Rebuild Container`

To test the server:

### Chatting Endpopint
```
curl -X 'POST' \
  'http://127.0.0.1:8000/soul_sync/ai_wingman_chat/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text_message": "My latest message is yolo",
  "from_id": "user123",
  "to_id": "user000"
}'
```

### Paginated Conversation History Endpoint
```
curl -X 'GET' 'http://127.0.0.1:8000/soul_sync/get_messages/?from_id=user123&to_id=user000&offset=0&limit=10'
```

### Initiate Conversation via AI Wingman
```
curl -X POST "http://127.0.0.1:8000/soul_sync/ai_wingman_initiate_chat/" \
     -H "Content-Type: application/json" \
     -d '{"from_id": "user123", "to_id": "user000"}'
```

For a clear conv history -> Try it with a random user in case you've already used 'user123'.