from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from ..services.llm_service import chat_with_business_context, analyze_business_opportunity
from ..services.intelligent_chat import intelligent_chat
from ..database.mongodb import collections
from ..api.auth import get_current_user_id
from ..utils.structured_output import format_chat_response
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class ChatRequest(BaseModel):
    business_id: str
    message: str
    mode: Optional[str] = "full_intelligence"  # Chat mode

class ChatResponse(BaseModel):
    conversation_id: str
    business_id: str
    message: str
    response: str
    structured_response: Optional[Dict] = None
    timestamp: str
    agents_used: Optional[List[str]] = None
    rag_used: Optional[bool] = False
    citations: Optional[List[Dict]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    user_id: str = Depends(get_current_user_id)
):
    """
    Intelligent AI Chat endpoint
    Combines documents (RAG), specialized agents, and general AI knowledge
    """
    try:
        # Get business details and verify ownership
        business = await collections.businesses().find_one({
            "_id": ObjectId(request.business_id),
            "user_id": user_id
        })
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Get conversation history from MongoDB
        history_docs = await collections.conversations().find(
            {"business_id": request.business_id}
        ).sort("timestamp", -1).limit(5).to_list(length=5)
        
        # Format history for LLM
        conversation_history = []
        for doc in reversed(history_docs):
            conversation_history.append({"role": "user", "content": doc.get("message", "")})
            conversation_history.append({"role": "assistant", "content": doc.get("response", "")})
        
        # Use intelligent chat service with mode
        result = await intelligent_chat.process_message(
            message=request.message,
            business_id=request.business_id,
            business=business,
            conversation_history=conversation_history,
            mode=request.mode  # Pass mode
        )
        
        ai_response = result.get("response", "")
        citations = result.get("citations", [])
        agents_used = result.get("agents_used", [])
        rag_used = result.get("rag_used", False)
        
        # Format response
        structured_response = format_chat_response(ai_response)
        if citations:
            structured_response["citations"] = citations
        if agents_used:
            structured_response["agents_used"] = agents_used
        structured_response["sources"] = result.get("sources", {})
        
        # Save to MongoDB
        conversation = {
            "user_id": user_id,
            "business_id": request.business_id,
            "message": request.message,
            "response": ai_response,
            "structured_response": structured_response,
            "agents_used": agents_used if agents_used else None,
            "rag_used": rag_used,
            "citations": citations if citations else None,
            "sources": result.get("sources", {}),
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        inserted = await collections.conversations().insert_one(conversation)
        
        return ChatResponse(
            conversation_id=str(inserted.inserted_id),
            business_id=request.business_id,
            message=request.message,
            response=ai_response,
            structured_response=structured_response,
            timestamp=datetime.utcnow().isoformat(),
            agents_used=agents_used if agents_used else None,
            rag_used=rag_used,
            citations=citations if citations else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

def _needs_agent_analysis(message: str) -> bool:
    """Determine if message needs multi-agent analysis"""
    keywords = [
        "expand", "expansion", "location", "city", "market", "competition",
        "forecast", "revenue", "profit", "analysis", "opportunity", "should i",
        "recommend", "best", "where", "strategy", "growth", "invest"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

def _needs_rag(message: str) -> bool:
    """Determine if message needs RAG (document retrieval)"""
    # Always try RAG first if documents exist
    # Let the RAG pipeline decide if documents are relevant
    return True  # Always attempt RAG, it will fallback if no documents

@router.get("/chat/history/{business_id}")
async def get_chat_history(
    business_id: str, 
    limit: int = 10,
    user_id: str = Depends(get_current_user_id)
):
    """Get chat history for a specific business (requires authentication)"""
    try:
        # Verify business ownership
        business = await collections.businesses().find_one({
            "_id": ObjectId(business_id),
            "user_id": user_id
        })
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        conversations = await collections.conversations().find(
            {"business_id": business_id, "user_id": user_id}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return {
            "business_id": business_id,
            "conversations": [
                {
                    "id": str(conv["_id"]),
                    "message": conv.get("message", ""),
                    "response": conv.get("response", ""),
                    "timestamp": conv["timestamp"].isoformat()
                }
                for conv in conversations
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/clear/{business_id}")
async def clear_chat_history(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Clear chat history for a business (requires authentication)"""
    try:
        # Verify business ownership
        business = await collections.businesses().find_one({
            "_id": ObjectId(business_id),
            "user_id": user_id
        })
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Delete all conversations for this business
        result = await collections.conversations().delete_many({
            "business_id": business_id,
            "user_id": user_id
        })
        
        return {
            "success": True,
            "deleted_count": result.deleted_count,
            "message": "Chat history cleared successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/analyze-business")
async def analyze_business_endpoint(
    business_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    """Comprehensive business analysis using AI (requires authentication)"""
    try:
        # Verify business ownership
        business = await collections.businesses().find_one({
            "_id": ObjectId(business_id),
            "user_id": user_id
        })
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        analysis = analyze_business_opportunity(
            business_name=business.get("name"),
            industry=business.get("industry"),
            city=business.get("city"),
            state=business.get("state"),
            investment=business.get("investment"),
            description=business.get("description", "")
        )
        
        return analysis
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
