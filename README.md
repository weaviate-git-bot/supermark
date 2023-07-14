# supermark
Repository for backend of [Supermark.ai](https://app.supermark.ai) - productivity tool that lets you have an AI chat with your bookmarks.

## Run
- add `OPENAI_API_KEY` to `config/.env.prod` or `config/.env.local`
- `export PORT=8000 && docker-compose -f production.yml up fastapi` - production vector database
- `export PORT=8000 && docker-compose -f local.yml up fastapi`- local database
