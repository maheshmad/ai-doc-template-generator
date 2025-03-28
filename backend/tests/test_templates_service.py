import pytest
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import asyncio
from pathlib import Path
from uuid import uuid4
from app.templates_service import Template, TemplateModel, TemplateContentUpdate
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

# Import after environment is loaded
from app.config import Config

# Override database for testing
@pytest.fixture(scope="session", autouse=True)
def override_db_for_testing():
    """Override the database name for testing"""
    original_db = Template.db
    # Switch to test database
    Template.db = Template.client[Config.MONGODB_TEST_DB_NAME]
    Template.collection = Template.db.templates
    
    yield
    
    # Restore original database
    Template.db = original_db

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
    # Setup: Clear the templates collection in test database
    await Template.collection.delete_many({})
    print(f"Test database '{Config.MONGODB_TEST_DB_NAME}' templates collection cleared")
    
    yield
    
    # Teardown: Clear the templates collection
    await Template.collection.delete_many({})

@pytest.fixture(scope="function")
async def sample_template(template_db):
    """Create a sample template with all its chunks for testing"""
    template_ids = []
    
    try:
        # Insert all chunks
        for chunk_data in sample_template_chunks:
            template_model = TemplateModel(**chunk_data)
            template_id = await Template.create(template_model)
            template_ids.append(template_id)
        
        # Return the main template ID (first chunk)
        yield template_ids[0]
    
    finally:
        # Cleanup if needed (template_db fixture will handle this)
        pass

@pytest.fixture(scope="function")
async def multiple_templates(template_db):
    """Create multiple different templates for testing"""
    template_ids = []
    
    try:
        # Create three different templates
        for i in range(3):
            template_data = TemplateModel(
                template_id=f"test-template-{i}",
                template_chunk_id=str(uuid4()),
                template_chunk_order=0,
                template_name=f"Test Template {i}",
                template_content=f"Test content for template {i}",
                template_created=datetime.now(),
                template_updated=datetime.now(),
                linked_prompt_id=""
            )
            template_id = await Template.create(template_data)
            template_ids.append(template_id)
        
        yield template_ids
    
    finally:
        # Cleanup this test's templates
        await Template.collection.delete_many({
            "template_id": {"$in": template_ids}
        })

@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger('templates_service')

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
async def test_get_template(sample_template):
    """Test retrieving a template"""
    template = await Template.get(sample_template)
    assert template is not None
    assert template.template_id == sample_template
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
async def test_list_all_templates(multiple_templates):
    """Test listing all templates"""
    # First ensure clean state
    await Template.collection.delete_many({
        "template_id": {"$nin": multiple_templates}
    })
    
    templates = await Template.list_all()
    # Get only the main templates (chunk_order = 0)
    main_templates = [t for t in templates if t.template_chunk_order == 0]
    assert len(main_templates) == 3
    template_ids = [t.template_id for t in main_templates]
    assert all(tid in template_ids for tid in multiple_templates)

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
async def test_reorder_chunks(sample_template):
    """Test reordering template chunks"""
    # Get current chunks
    chunks = await Template.get_chunks(sample_template)
    chunk_ids = [chunk.template_chunk_id for chunk in chunks]
    
    # Reverse the order
    reversed_ids = chunk_ids[::-1]
    
    # Update the reorder_chunks method in Template class to handle order properly
    success = await Template.reorder_chunks(sample_template, reversed_ids)
    assert success is True
    
    # Verify new order by checking template_chunk_order values
    updated_chunks = await Template.get_chunks(sample_template)
    updated_chunks_sorted = sorted(updated_chunks, key=lambda x: x.template_chunk_order)
    updated_ids = [chunk.template_chunk_id for chunk in updated_chunks_sorted]
    assert updated_ids == reversed_ids, "Chunks not in expected order after reordering"

@pytest.mark.asyncio
async def test_search_templates(sample_template):
    """Test searching templates"""
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

@pytest.mark.asyncio
async def test_update_template_content(sample_template):
    """Test updating template content"""
    new_content = """First chunk content

---

Second chunk content

---

Third chunk content"""
    
    update_data = TemplateContentUpdate(content=new_content)
    await Template.update_content(sample_template, update_data)
    
    # Verify the update
    chunks = await Template.get_chunks(sample_template)
    assert len(chunks) == 3
    assert chunks[0].template_content == "First chunk content"
    assert chunks[1].template_content == "Second chunk content"
    assert chunks[2].template_content == "Third chunk content"

@pytest.mark.asyncio
async def test_update_template_content_single_chunk(template_db):
    """Test updating template content with a single chunk"""
    # First create a template
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    # Update content with single chunk
    new_content = "Single chunk content"
    update_data = TemplateContentUpdate(content=new_content)
    
    # Update the template content
    await Template.update_content(template_id, update_data)
    
    # Verify the update
    chunks = await Template.get_chunks(template_id)
    assert len(chunks) == 1
    assert chunks[0].template_content == "Single chunk content"
    assert chunks[0].template_chunk_order == 0

@pytest.mark.asyncio
async def test_update_template_content_empty(template_db):
    """Test updating template content with empty content"""
    # First create a template
    template_data = TemplateModel(**sample_template_chunks[0])
    template_id = await Template.create(template_data)
    
    # Update with empty content
    update_data = TemplateContentUpdate(content="")
    
    # Update should create a template with empty content
    await Template.update_content(template_id, update_data)
    
    # Verify the update
    chunks = await Template.get_chunks(template_id)
    assert len(chunks) == 1
    assert chunks[0].template_content == ""
    assert chunks[0].template_chunk_order == 0

@pytest.mark.asyncio
async def test_update_template_content_invalid_id(template_db):
    """Test updating template content with invalid template ID"""
    invalid_id = str(uuid4())
    update_data = TemplateContentUpdate(content="Test content")
    
    # Should raise an exception
    with pytest.raises(Exception):
        await Template.update_content(invalid_id, update_data)

@pytest.mark.asyncio
async def test_update_template_content_preserve_metadata(template_db):
    """Test that updating content preserves template metadata"""
    # First create a template with metadata
    template_data = TemplateModel(
        template_id="test-template",
        template_chunk_id=str(uuid4()),
        template_chunk_order=0,
        template_name="Test Template",
        template_content="Original content",
        template_created=datetime.now(),
        template_updated=datetime.now(),
        linked_prompt_id="test-prompt"
    )
    template_id = await Template.create(template_data)
    
    # Update content
    new_content = "Updated content"
    update_data = TemplateContentUpdate(content=new_content)
    await Template.update_content(template_id, update_data)
    
    # Verify metadata is preserved
    chunks = await Template.get_chunks(template_id)
    assert len(chunks) == 1
    assert chunks[0].template_name == "Test Template"
    assert chunks[0].linked_prompt_id == "test-prompt"
    assert chunks[0].template_content == "Updated content" 