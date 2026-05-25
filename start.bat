start cmd /k "cd C:\aianycam\backend && py -m uvicorn main:app --host 0.0.0.0 --port 8080"
start cmd /k "cd C:\aianycam\frontend && npm start"
start cmd /k "cloudflared tunnel --url http://localhost:8080"