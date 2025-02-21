from typing import List
from pydantic import BaseModel, Field
from app.db import search_vector_db
from app.openaiutils import get_embedding
from app.templates_service import Template, TemplateModel

class QueryKnowledgeBaseTool(BaseModel):
    """Query the knowledge base to answer user questions"""
    query_input: str = Field(description='The natural language query input string. The query input should be clear and standalone.')

    async def __call__(self, rdb):
        query_vector = await get_embedding(self.query_input)        
        chunks = await search_vector_db(rdb, query_vector)        
        formatted_sources = [f'SOURCE: {c["doc_name"]}\n"""\n{c["text"]}\n"""' for c in chunks]
        return f"\n\n---\n\n".join(formatted_sources) + f"\n\n---"

class QueryByTemplateIdTool(BaseModel):
    """Query the templates using the template id"""
    query_input: str = Field(description='the template id to be retrieved')

    async def __call__(self):
        templates = await Template.get_chunks(self.query_input)
        return templates

class SaveTemplateTool(BaseModel):
    """This tool saves the template to the database"""
    template: List[TemplateModel]

    async def __call__(self):
        templates = await Template.create_many(self.template)
        return "Successfully saved the template"