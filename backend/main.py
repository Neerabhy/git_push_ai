__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# 👇 FIXED: Removed the extra space before this line
from backend.crew.crew_logic import TravelCrew 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static folder so the browser can find style.css and script.js
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def get_home():
    return FileResponse("frontend/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket Connected!")
    
    try:
        while True:
            # Receive JSON from the frontend
            data = await websocket.receive_text()
            
            # 👇 ADDED: Inner try-except so a single error doesn't kill the chat
            try:
                request_data = json.loads(data)
                
                # Extract BOTH the prompt and the chat history
                user_prompt = request_data.get("prompt", "")
                chat_history = request_data.get("history", []) 
                
                print(f"🚀 Received prompt: {user_prompt}")
                print(f"📚 History Length: {len(chat_history)} messages")
                
                # Send a status update immediately
                await websocket.send_json({"type": "status", "message": "Agents are orchestrating your trip... 🔍"})

                # -------------------------------------------------------------
                # 👇 REAL CREW LOGIC ENABLED 👇
                # -------------------------------------------------------------
                
                # 1. Package the inputs
                inputs = {
                     "user_request": user_prompt,
                     "chat_history": str(chat_history)
                }
                
                # 2. Instantiate your crew
                # (Note: Adjust this depending on exactly how your TravelCrew class is built. 
                # Usually you call .crew().kickoff() or just .kickoff())
                travel_app = TravelCrew()
                
                # 3. Run the AI agents! 
                # Using asyncio.to_thread prevents CrewAI from freezing your WebSocket while it thinks
                final_itinerary = await asyncio.to_thread(travel_app.crew().kickoff, inputs=inputs)
                
                # 4. Send the REAL final itinerary back
                await websocket.send_json({"type": "result", "result": str(final_itinerary)})

            except Exception as message_error:
                print(f"⚠️ Agent/Processing Error: {message_error}")
                await websocket.send_json({"type": "error", "message": f"Agent error: {str(message_error)}"})

    except WebSocketDisconnect:
        print("❌ Client disconnected")