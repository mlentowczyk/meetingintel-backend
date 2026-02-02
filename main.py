from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from research_service import generate_meeting_brief
import uvicorn

app = FastAPI(title="MeetingIntel API")

# CORS - allow extension to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class Attendee(BaseModel):
    email: str
    name: str

class BriefRequest(BaseModel):
    meeting_id: str
    meeting_title: str
    meeting_time: str
    attendees: List[Attendee]

# Response model
class BriefResponse(BaseModel):
    meeting_id: str
    attendees: List[dict]
    conversation_starters: List[str]
    questions_to_ask: List[str]
    strategy: str
    generated_at: str

@app.get("/")
def read_root():
    return {
        "service": "MeetingIntel API",
        "version": "1.0",
        "status": "active"
    }

@app.post("/api/generate-brief", response_model=BriefResponse)
async def generate_brief(request: BriefRequest):
    """
    Generate meeting brief using Claude AI
    """
    try:
        # Call Claude to research and generate brief
        brief = await generate_meeting_brief(
            meeting_title=request.meeting_title,
            meeting_time=request.meeting_time,
            attendees=[{"email": a.email, "name": a.name} for a in request.attendees]
        )
        
        # Add meeting ID
        brief["meeting_id"] = request.meeting_id
        
        return brief
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating brief: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
