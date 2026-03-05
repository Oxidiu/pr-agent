import os
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
from pr_agent.agent.pr_agent import PRAgent
from pr_agent.config_loader import get_settings

app = FastAPI()
agent = PRAgent()

@app.post("/webhook")
async def bitbucket_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print(f"Received webhook: {data.get('event_key')}")

    # Extragem URL-ul PR-ului din formatul Bitbucket Cloud
    try:
        pr_url = data['pullrequest']['links']['html']['href']
        print(f"Processing PR: {pr_url}")

        # Rulăm comanda în background pentru a nu bloca Bitbucket (timeout)
        background_tasks.add_task(agent.handle_request, pr_url, "/review")
        background_tasks.add_task(agent.handle_request, pr_url, "/describe")

        return {"status": "accepted", "url": pr_url}
    except KeyError:
        return {"status": "ignored", "reason": "No PR URL found in payload"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
