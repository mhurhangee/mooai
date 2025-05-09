"""
Models for structured responses in the MooAI assistant.

This module contains Pydantic models used for structured outputs
from the OpenAI Agent SDK.
"""
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field


class SuggestedPrompt(BaseModel):
    """
    Model for a suggested prompt in Slack's required format.
    
    Slack requires both title and message fields for suggested prompts.
    """
    title: str = Field(..., description="Short title for the prompt")
    message: str = Field(..., description="Full message content of the prompt")


class StructuredResponse(BaseModel):
    """
    Structured response format for the MooAI assistant.
    
    This model defines the structure that the OpenAI Agent will use
    when generating responses in Slack threads.
    """
    thread_title: Optional[str] = Field(
        None, 
        description="Title for the thread, used to update the assistant thread title"
    )
    message_title: Optional[str] = Field(
        None, 
        description="Title for the message, displayed as a header above the response"
    )
    response: str = Field(
        ..., 
        description="The main response content in markdown format"
    )
    followups: Optional[List[str]] = Field(
        None, 
        description="Suggested follow-up prompts for the user"
    )
    
    def get_formatted_prompts(self) -> List[Dict[str, str]]:
        """
        Convert the followups list to the format required by Slack API.
        
        Returns:
            A list of dictionaries with 'title' and 'message' keys.
        """
        if not self.followups:
            return []
            
        return [
            {"title": prompt, "message": prompt}
            for prompt in self.followups
        ]
