# soul-sync
An AI wingman to sync souls across the globe.

Ideally all you need to setup the server is:
```
docker-compose up
```
> Tho I am currently working on fixing some port issue in it. Once done, setting up the server should be seemeless for the front-end team.


For the time being if you wanna work with it you can setup server manually locally via:

Install all dependencies with
```
pip install -r requirements.txt
```

MacOS: 
Will also have to install postgresql via 
```
brew install postgresql
```

You will also need an OpenAI API, and export it to OAIKEY env variable
```
export OAIKEY=<your key>
```

Start server:
```
uvicorn soul_sync_chat_api:app --host 0.0.0.0 --port 8000
```

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