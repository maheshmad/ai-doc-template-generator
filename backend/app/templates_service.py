from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
import io
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional, Dict, Any, List
import os
from app.config import Config
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from pymongo import UpdateOne

router = APIRouter()

class TemplateModel(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid4()))
    template_chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    template_chunk_order: int = Field(default=0)
    template_name: str        
    template_content: str
    template_created: datetime = Field(default_factory=datetime.now)
    template_updated: datetime = Field(default_factory=datetime.now)
    linked_prompt_id: str = Field(default="")

class Template:
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    collection = db.templates

    @classmethod
    async def create(cls, template_data: TemplateModel) -> str:
        """Create a new template"""
        try:
            # Ensure template_id and chunk_id are set
            if not template_data.template_id:
                template_data.template_id = str(uuid4())
            if not template_data.template_chunk_id:
                template_data.template_chunk_id = str(uuid4())
            
            # Set timestamps
            template_data.template_created = datetime.now()
            template_data.template_updated = datetime.now()
            
            result = await cls.collection.insert_one(template_data.model_dump())
            return template_data.template_id
        except Exception as e:
            raise Exception(f"Error creating template: {str(e)}")

    @classmethod
    async def get(cls, template_id: str) -> Optional[TemplateModel]:
        """Retrieve a template by ID"""
        try:
            # First try to find by template_id
            template = await cls.collection.find_one({"template_id": template_id})
            if not template:
                # Then try to find by chunk_id
                template = await cls.collection.find_one({"template_chunk_id": template_id})
            return TemplateModel(**template) if template else None
        except Exception as e:
            raise Exception(f"Error retrieving template: {str(e)}")

    @classmethod
    async def get_chunks(cls, template_id: str) -> List[TemplateModel]:
        """Retrieve all chunks for a template"""
        try:
            cursor = cls.collection.find({
                "template_id": template_id
            }).sort("template_chunk_order", 1)
            chunks = await cursor.to_list(length=None)
            return [TemplateModel(**chunk) for chunk in chunks]
        except Exception as e:
            raise Exception(f"Error retrieving template chunks: {str(e)}")

    @classmethod
    async def update(cls, template_id: str, template_data: TemplateModel) -> bool:
        """Update a template by ID"""
        try:
            template_data.template_updated = datetime.now()
            result = await cls.collection.update_one(
                {"template_id": template_id},
                {"$set": template_data.model_dump()}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error updating template: {str(e)}")

    @classmethod
    async def delete(cls, template_id: str) -> bool:
        """Delete a template and all its chunks"""
        try:
            result = await cls.collection.delete_many({
                "template_id": template_id
            })
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error deleting template: {str(e)}")

    @classmethod
    async def list_all(cls) -> List[TemplateModel]:
        """Retrieve all templates (only main templates, not chunks)"""
        try:
            cursor = cls.collection.find({
                "template_chunk_order": 0  # Main templates have order 0
            })
            templates = await cursor.to_list(length=None)
            return [TemplateModel(**template) for template in templates]
        except Exception as e:
            raise Exception(f"Error listing templates: {str(e)}")

    @classmethod
    async def add_chunk(cls, template_id: str, content: str) -> str:
        """Add a new chunk to an existing template"""
        try:
            # Get current max chunk order
            cursor = cls.collection.find({"template_id": template_id}).sort("template_chunk_order", -1).limit(1)
            last_chunk = await cursor.to_list(length=1)
            new_order = last_chunk[0]["template_chunk_order"] + 1 if last_chunk else 1

            new_chunk = TemplateModel(
                template_id=template_id,
                template_chunk_id=str(uuid4()),
                template_chunk_order=new_order,
                template_name="",  # Can be updated if needed
                template_content=content
            )
            
            result = await cls.collection.insert_one(new_chunk.model_dump())
            return new_chunk.template_chunk_id
        except Exception as e:
            raise Exception(f"Error adding template chunk: {str(e)}")

    @classmethod
    async def delete_chunk(cls, chunk_id: str) -> bool:
        """Delete a specific chunk"""
        try:
            result = await cls.collection.delete_one({
                "template_chunk_id": chunk_id
            })
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error deleting template chunk: {str(e)}")

    @classmethod
    async def reorder_chunks(cls, template_id: str, chunk_order: List[str]) -> bool:
        """Reorder chunks for a template"""
        try:
            operations = []
            for index, chunk_id in enumerate(chunk_order):
                operations.append(
                    UpdateOne(
                        {"template_chunk_id": chunk_id},
                        {"$set": {"template_chunk_order": index}}
                    )
                )
            if operations:
                result = await cls.collection.bulk_write(operations)
                return result.modified_count > 0
            return False
        except Exception as e:
            raise Exception(f"Error reordering template chunks: {str(e)}")

    @classmethod
    async def search(cls, query: str) -> List[TemplateModel]:
        """Search templates by name or content"""
        try:
            cursor = cls.collection.find({
                "$or": [
                    {"template_name": {"$regex": query, "$options": "i"}},
                    {"template_content": {"$regex": query, "$options": "i"}}
                ],
                "template_chunk_order": 0  # Only search main templates
            })
            templates = await cursor.to_list(length=None)
            return [TemplateModel(**template) for template in templates]
        except Exception as e:
            raise Exception(f"Error searching templates: {str(e)}")

@router.post("/api/templates")
async def create_template(template_data: TemplateModel):
    """Create a new template"""
    try:
        template_id = await Template.create(template_data)
        return {"template_id": template_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/templates")
async def list_templates():
    """Get all templates (main templates only, not chunks)"""
    try:
        templates = await Template.list_all()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID"""
    try:
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/templates/{template_id}")
async def update_template(template_id: str, template_data: TemplateModel):
    """Update a template"""
    try:
        success = await Template.update(template_id, template_data)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template and all its chunks"""
    try:
        success = await Template.delete(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/templates/{template_id}/chunks")
async def get_template_chunks(template_id: str):
    """Get all chunks for a template"""
    try:
        chunks = await Template.get_chunks(template_id)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/templates/{template_id}/chunks")
async def add_template_chunk(template_id: str, content: str):
    """Add a new chunk to a template"""
    try:
        chunk_id = await Template.add_chunk(template_id, content)
        return {"chunk_id": chunk_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/templates/{template_id}/chunks/{chunk_id}")
async def delete_template_chunk(template_id: str, chunk_id: str):
    """Delete a specific chunk from a template"""
    try:
        success = await Template.delete_chunk(chunk_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chunk not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/templates/{template_id}/chunks/reorder")
async def reorder_template_chunks(
    template_id: str, 
    chunk_order: List[str]
):
    """Reorder chunks in a template"""
    try:
        success = await Template.reorder_chunks(template_id, chunk_order)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/templates/search")
async def search_templates(query: str):
    """Search templates by name or content"""
    try:
        templates = await Template.search(query)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 