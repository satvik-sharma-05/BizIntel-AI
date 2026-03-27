"""
Business API - MongoDB Only
Multi-tenant SaaS with business access verification
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from bson import ObjectId
from ..database.mongodb import collections
from ..api.auth import get_current_user_id

router = APIRouter()

# Business Access Verification
async def verify_business_access(business_id: str, user_id: str):
    """
    Verify that the user has access to the specified business.
    Raises HTTPException if access is denied.
    Returns the business document if access is granted.
    """
    try:
        businesses = collections.businesses()
        business = await businesses.find_one({
            "_id": ObjectId(business_id),
            "user_id": user_id
        })
        
        if not business:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Business not found or you don't have permission"
            )
        
        return business
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying business access: {str(e)}")

class BusinessCreate(BaseModel):
    business_name: str
    industry: str
    city: str
    state: str
    initial_investment: float
    description: str = ""

class BusinessUpdate(BaseModel):
    business_name: str = None
    industry: str = None
    city: str = None
    state: str = None
    initial_investment: float = None
    description: str = None

class BusinessResponse(BaseModel):
    id: str
    business_name: str
    industry: str
    city: str
    state: str
    initial_investment: float
    description: str
    created_at: str

@router.post("/business/create")
async def create_business(
    business: BusinessCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create new business in MongoDB"""
    try:
        businesses = collections.businesses()
        users = collections.users()
        
        # Create business document
        business_doc = {
            "user_id": user_id,
            "business_name": business.business_name,
            "industry": business.industry,
            "city": business.city,
            "state": business.state,
            "initial_investment": business.initial_investment,
            "description": business.description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await businesses.insert_one(business_doc)
        business_id = str(result.inserted_id)
        
        # Add business_id to user's business_ids array
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"business_ids": business_id}}
        )
        
        return {
            "id": business_id,
            "name": business.business_name,
            "business_name": business.business_name,  # Keep for backward compatibility
            "industry": business.industry,
            "city": business.city,
            "state": business.state,
            "investment": business.initial_investment,
            "initial_investment": business.initial_investment,  # Keep for backward compatibility
            "description": business.description,
            "created_at": business_doc["created_at"].isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business/list")
async def list_businesses(user_id: str = Depends(get_current_user_id)):
    """List all businesses for user from MongoDB"""
    try:
        businesses = collections.businesses()
        
        cursor = businesses.find({"user_id": user_id}).sort("created_at", -1)
        business_list = await cursor.to_list(length=100)
        
        return [
            {
                "id": str(b["_id"]),
                "name": b["business_name"],
                "business_name": b["business_name"],  # Keep for backward compatibility
                "industry": b["industry"],
                "city": b["city"],
                "state": b["state"],
                "investment": b["initial_investment"],
                "initial_investment": b["initial_investment"],  # Keep for backward compatibility
                "description": b.get("description", ""),
                "created_at": b["created_at"].isoformat()
            }
            for b in business_list
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business/{business_id}")
async def get_business(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get business by ID from MongoDB with access verification"""
    try:
        # Verify access
        business = await verify_business_access(business_id, user_id)
        
        return {
            "id": str(business["_id"]),
            "name": business["business_name"],
            "business_name": business["business_name"],
            "industry": business["industry"],
            "city": business["city"],
            "state": business["state"],
            "investment": business["initial_investment"],
            "initial_investment": business["initial_investment"],
            "description": business.get("description", ""),
            "created_at": business["created_at"].isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/business/{business_id}")
async def delete_business(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete business from MongoDB with access verification"""
    try:
        # Verify access
        await verify_business_access(business_id, user_id)
        
        businesses = collections.businesses()
        users = collections.users()
        
        # Delete business
        await businesses.delete_one({"_id": ObjectId(business_id)})
        
        # Remove from user's business_ids
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"business_ids": business_id}}
        )
        
        # Delete related data (business-scoped)
        await collections.conversations().delete_many({"business_id": business_id})
        await collections.market_analysis().delete_many({"business_id": business_id})
        await collections.location_analysis().delete_many({"business_id": business_id})
        await collections.forecasts().delete_many({"business_id": business_id})
        await collections.agent_logs().delete_many({"business_id": business_id})
        await collections.documents().delete_many({"business_id": business_id})
        await collections.rag_chunks().delete_many({"business_id": business_id})
        
        return {"message": "Business deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/business/{business_id}")
async def update_business(
    business_id: str,
    updates: BusinessUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update business details and trigger re-analysis
    
    This endpoint:
    1. Updates MongoDB business document
    2. Updates Neo4j graph relationships
    3. Triggers re-analysis pipeline (market, location, forecast)
    4. Invalidates cached data
    5. Updates agent memory
    """
    try:
        # Verify access
        business = await verify_business_access(business_id, user_id)
        
        # Build update document (only include provided fields)
        update_doc = {}
        if updates.business_name is not None:
            update_doc["business_name"] = updates.business_name
        if updates.industry is not None:
            update_doc["industry"] = updates.industry
        if updates.city is not None:
            update_doc["city"] = updates.city
        if updates.state is not None:
            update_doc["state"] = updates.state
        if updates.initial_investment is not None:
            update_doc["initial_investment"] = updates.initial_investment
        if updates.description is not None:
            update_doc["description"] = updates.description
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_doc["updated_at"] = datetime.utcnow()
        
        # Update MongoDB
        businesses = collections.businesses()
        await businesses.update_one(
            {"_id": ObjectId(business_id)},
            {"$set": update_doc}
        )
        
        # Update Neo4j if location or industry changed
        if "city" in update_doc or "state" in update_doc or "industry" in update_doc:
            try:
                from ..database.neo4j_client import neo4j_client
                
                # Update business node
                neo4j_client.run_query(
                    """
                    MERGE (b:Business {id: $business_id})
                    SET b.name = $name,
                        b.industry = $industry,
                        b.city = $city,
                        b.state = $state,
                        b.updated_at = datetime()
                    """,
                    {
                        "business_id": business_id,
                        "name": update_doc.get("business_name", business["business_name"]),
                        "industry": update_doc.get("industry", business["industry"]),
                        "city": update_doc.get("city", business["city"]),
                        "state": update_doc.get("state", business["state"])
                    }
                )
            except Exception as e:
                print(f"Neo4j update error: {str(e)}")
        
        # Invalidate cached data
        api_cache = collections.api_cache()
        await api_cache.delete_many({
            "cache_key": {"$regex": f"^(market|location|forecast)_{business_id}"}
        })
        
        # Clear old analysis data to trigger re-analysis
        if "city" in update_doc or "state" in update_doc or "industry" in update_doc:
            await collections.market_analysis().delete_many({"business_id": business_id})
            await collections.location_analysis().delete_many({"business_id": business_id})
            await collections.forecasts().delete_many({"business_id": business_id})
        
        # Get updated business
        updated_business = await businesses.find_one({"_id": ObjectId(business_id)})
        
        return {
            "id": str(updated_business["_id"]),
            "name": updated_business["business_name"],
            "business_name": updated_business["business_name"],
            "industry": updated_business["industry"],
            "city": updated_business["city"],
            "state": updated_business["state"],
            "investment": updated_business["initial_investment"],
            "initial_investment": updated_business["initial_investment"],
            "description": updated_business.get("description", ""),
            "created_at": updated_business["created_at"].isoformat(),
            "updated_at": updated_business["updated_at"].isoformat(),
            "message": "Business updated successfully. Analysis data will be regenerated on next request."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update business error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
