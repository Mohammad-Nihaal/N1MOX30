from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class VoiceAssistantRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class VoiceAssistantResponse(BaseModel):
    success: bool
    message: str
    intent: str
    action: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False
    assistant_state: str = "ready"
    suggestions: List[str] = Field(default_factory=list)
