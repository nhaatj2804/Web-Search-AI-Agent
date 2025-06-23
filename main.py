import uuid
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel
import asyncio
from search import google_search
from model import process, process_deepseek
from get_result import getResult
import os
from dotenv import load_dotenv
import time
from create_database import load_documents, split_documents, save_to_chroma
from query import query
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Agent Web search")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
class SearchRequest(BaseModel):
    query: str
    collection_id: str | None = None


# Store active WebSocket connections
active_connections: set[WebSocket] = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

async def broadcast_status(message: str):
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps({"status": message}))
        except:
            active_connections.remove(connection)

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/search")
async def search(request: SearchRequest):
    try:
        start_time = time.time()
        
        # Generate collection ID if not provided
        collection_id = request.collection_id or str(uuid.uuid4())
        
        # Get API credentials
        google_api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("CSE_ID")
        
        if not google_api_key or not cse_id:
            raise HTTPException(status_code=500, detail="Missing API credentials")

        # Extract keywords and perform Google search
        # keyword = reorder_keywords(request.query)
        # print(f"Keyword: {keyword}")
        results = google_search(request.query, google_api_key, cse_id)
        
        processed_results = []
        # Process each search result
        os.makedirs("data", exist_ok=True)
        for r in results:
            result = {
                "link": r["link"],
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "displayLink": r.get("displayLink", ""),
                "pagemap": r.get("pagemap", {})
            }
            processed_results.append(result)
            await broadcast_status(f"Processing: {result['link']}")
        print(f"Processed results: {len(processed_results)} items")
        await getResult([r["link"] for r in processed_results], request.query, collection_id)

        # Process new documents into a new collection
        await broadcast_status("Analyzing collected information...")
        new_documents = load_documents(collection_id)
        if new_documents:
            chunks = split_documents(new_documents)
            collection_id = save_to_chroma(chunks, collection_id)
        
        # Get context and generate answer from the collection
        context_text = query(request.query, collection_id)
        if not context_text:
            return {
                "answer": "No relevant information found for your query.",
                "results": processed_results
            }

        answer = process_deepseek(context_text, request.query)
        end_time = time.time()

        return {
            "answer": answer,
            "results": processed_results,
            "time_taken": round(end_time - start_time, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)