import pytest
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import asyncio
from pathlib import Path

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

# Import after environment is loaded
from app.templates_service import Template, TemplateModel
from app.config import Config


# Sample test data
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
    },
    
    # Coverage Type - General Liability (chunk_order = 3)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "general-liability-chunk-001",
        "template_chunk_order": 3,
        "template_name": "General Liability Coverage",
        "template_content": "COMMERCIAL GENERAL LIABILITY\nOccurrence Form\nEach Occurrence Limit: $[Amount]\nDamage to Rented Premises: $[Amount]\nMed Exp (Any one person): $[Amount]\nPersonal & Adv Injury: $[Amount]\nGeneral Aggregate: $[Amount]\nProducts-Comp/Op Agg: $[Amount]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Coverage Type - Automobile Liability (chunk_order = 4)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "auto-liability-chunk-001",
        "template_chunk_order": 4,
        "template_name": "Automobile Liability Coverage",
        "template_content": "AUTOMOBILE LIABILITY\nAny Auto\nCombined Single Limit: $[Amount]\nBodily Injury (Per person): $[Amount]\nBodily Injury (Per accident): $[Amount]\nProperty Damage: $[Amount]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Coverage Type - Umbrella Liability (chunk_order = 5)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "umbrella-liability-chunk-001",
        "template_chunk_order": 5,
        "template_name": "Umbrella Liability Coverage",
        "template_content": "UMBRELLA LIABILITY\nEach Occurrence: $[Amount]\nAggregate: $[Amount]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Coverage Type - Workers Compensation (chunk_order = 6)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "workers-comp-chunk-001",
        "template_chunk_order": 6,
        "template_name": "Workers Compensation Coverage",
        "template_content": "WORKERS COMPENSATION AND EMPLOYERS' LIABILITY\nStatutory Limits\nE.L. Each Accident: $[Amount]\nE.L. Disease - Ea Employee: $[Amount]\nE.L. Disease - Policy Limit: $[Amount]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Certificate Holder (chunk_order = 7)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "cert-holder-chunk-001",
        "template_chunk_order": 7,
        "template_name": "Certificate Holder Information",
        "template_content": "CERTIFICATE HOLDER\n[Name]\n[Street Address]\n[City, State, ZIP]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Cancellation Notice (chunk_order = 8)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "cancellation-chunk-001",
        "template_chunk_order": 8,
        "template_name": "Cancellation Notice",
        "template_content": "CANCELLATION\nSHOULD ANY OF THE ABOVE DESCRIBED POLICIES BE CANCELLED BEFORE THE EXPIRATION DATE THEREOF, NOTICE WILL BE DELIVERED IN ACCORDANCE WITH THE POLICY PROVISIONS.",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    },
    
    # Authorization (chunk_order = 9)
    {
        "template_id": "cert-of-insurance-001",
        "template_chunk_id": "authorization-chunk-001",
        "template_chunk_order": 9,
        "template_name": "Authorization",
        "template_content": "AUTHORIZED REPRESENTATIVE\n\n_______________________\nSignature\n\nDate: [Date]",
        "template_created": datetime.now(),
        "template_updated": datetime.now(),
        "linked_prompt_id": ""
    }
]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def template_db():
    """Setup and teardown for template tests"""
    # Setup: Clear the templates collection
    await Template.collection.delete_many({})
    print("Templates collection cleared")
    
    yield
    
    # Teardown: Clear the templates collection
    await Template.collection.delete_many({})

@pytest.mark.asyncio
async def test_create_template(template_db):
    """Test creating a new template"""
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    assert template_id == template_data.template_id
    
    # Verify template was created
    template = await Template.get(template_id)
    assert template is not None
    assert template.template_name == "Commercial Certificate of Insurance"

@pytest.mark.asyncio
async def test_get_template(template_db):
    """Test retrieving a template"""
    # First create a template
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    # Then retrieve it
    template = await Template.get(template_id)
    assert template is not None
    assert template.template_id == template_id
    assert template.template_name == "Commercial Certificate of Insurance"

@pytest.mark.asyncio
async def test_update_template(template_db):
    """Test updating a template"""
    # First create a template
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    # Update the template
    template_data.template_name = "Updated Certificate Name"
    success = await Template.update(template_id, template_data)
    assert success is True
    
    # Verify the update
    updated_template = await Template.get(template_id)
    assert updated_template.template_name == "Updated Certificate Name"

@pytest.mark.asyncio
async def test_delete_template(template_db):
    """Test deleting a template"""
    # First create a template
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    # Delete the template
    success = await Template.delete(template_id)
    assert success is True
    
    # Verify deletion
    template = await Template.get(template_id)
    assert template is None

@pytest.mark.asyncio
async def test_list_all_templates(template_db):
    """Test listing all templates"""
    # Create multiple templates
    for chunk in sample_template_chunks[:2]:  # Create first two chunks
        template_data = TemplateModel(**chunk)
        await Template.create(template_data)
    
    # List all templates
    templates = await Template.list_all()
    assert len(templates) == 1  # Should only return main templates (chunk_order = 0)
    assert templates[0].template_chunk_order == 0

@pytest.mark.asyncio
async def test_add_chunk(template_db):
    """Test adding a chunk to a template"""
    # First create main template
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    # Add a chunk
    chunk_content = "New chunk content"
    chunk_id = await Template.add_chunk(template_id, chunk_content)
    
    # Verify chunk was added
    chunks = await Template.get_chunks(template_id)
    assert len(chunks) == 2  # Main template + new chunk
    assert any(chunk.template_chunk_id == chunk_id for chunk in chunks)

@pytest.mark.asyncio
async def test_reorder_chunks(template_db):
    """Test reordering template chunks"""
    # Create template with multiple chunks
    template_id = "cert-of-insurance-001"
    chunk_ids = []
    for chunk in sample_template_chunks[:3]:  # Create first three chunks
        template_data = TemplateModel(**chunk)
        await Template.create(template_data)
        chunk_ids.append(chunk.get("template_chunk_id"))
    
    # Reorder chunks
    reversed_chunks = chunk_ids[::-1]  # Reverse the order
    success = await Template.reorder_chunks(template_id, reversed_chunks)
    assert success is True
    
    # Verify new order
    chunks = await Template.get_chunks(template_id)
    assert chunks[0].template_chunk_id == reversed_chunks[0]

@pytest.mark.asyncio
async def test_search_templates(template_db):
    """Test searching templates"""
    # Create sample templates
    for chunk in sample_template_chunks[:2]:
        template_data = TemplateModel(**chunk)
        await Template.create(template_data)
    
    # Search for templates
    results = await Template.search("Certificate")
    assert len(results) > 0
    assert "Certificate" in results[0].template_name

@pytest.mark.asyncio
async def test_insert_sample_template():
    """Test inserting the complete sample template"""
    # Clear existing templates
    await Template.collection.delete_many({})
    
    # Insert all chunks
    for chunk_data in sample_template_chunks:
        template_model = TemplateModel(**chunk_data)
        template_id = await Template.create(template_model)
        assert template_id is not None
    
    # Verify all chunks were inserted
    template_id = "cert-of-insurance-001"
    chunks = await Template.get_chunks(template_id)
    assert len(chunks) == len(sample_template_chunks)
    
    # Verify chunk order
    assert all(chunk.template_chunk_order == i for i, chunk in enumerate(chunks)) 