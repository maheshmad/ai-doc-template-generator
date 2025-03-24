import pytest
from datetime import datetime
from uuid import uuid4
from app.templates_service import Template, TemplateModel

# Sample template chunks data
sample_template_chunks = [
    # Main template (chunk_order = 0)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "main-chunk-001", 
        "template_chunk_order": 0,
        "template_name": "Commercial Certificate of Insurance",
        "template_content": "CERTIFICATE OF LIABILITY INSURANCE\nTHIS CERTIFICATE IS ISSUED AS A MATTER OF INFORMATION ONLY AND CONFERS NO RIGHTS UPON THE CERTIFICATE HOLDER.",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Producer Information (chunk_order = 1)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "producer-chunk-001",
        "template_chunk_order": 1,
        "template_name": "Producer Information", 
        "template_content": "PRODUCER\n[Producer Name]\n[Street Address]\n[City, State, ZIP]\nPhone: [Phone Number]\nEmail: [Email]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Insured Information (chunk_order = 2)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "insured-chunk-001",
        "template_chunk_order": 2,
        "template_name": "Insured Information",
        "template_content": "INSURED\n[Company Name]\n[Street Address]\n[City, State, ZIP]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    }
]

async def insert_template_test_data():
    """Insert sample template data into templates collection"""
    # Clear existing templates
    await Template.collection.delete_many({})
    
    # Insert all template chunks
    for chunk_data in sample_template_chunks:
        template_model = TemplateModel(**chunk_data)
        await Template.create(template_model)

if __name__ == "__main__":
    import asyncio
    asyncio.run(insert_template_test_data())

