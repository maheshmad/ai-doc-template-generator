from openai import AsyncOpenAI
import asyncio
from app.config import Config

# Initialize the async client
client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

async def get_embeddings(input, model="text-embedding-ada-002", dimensions=None):
    try:
        kwargs = {"input": input, "model": model}
        if dimensions is not None:
            kwargs["dimensions"] = dimensions
            
        response = await client.embeddings.create(**kwargs)
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Error getting embeddings: {str(e)}")
        raise

def token_size(text):
    # Use tiktoken or another tokenizer to count tokens
    # For now, returning a rough estimate based on words
    return len(text.split())

async def get_embedding(input, model=Config.EMBEDDING_MODEL, dimensions=Config.EMBEDDING_DIMENSIONS):
    res = await client.embeddings.create(input=input, model=model, dimensions=dimensions)
    return res.data[0].embedding

async def get_embeddings(input, model=Config.EMBEDDING_MODEL, dimensions=Config.EMBEDDING_DIMENSIONS):
    res = await client.embeddings.create(input=input, model=model, dimensions=dimensions)
    return [d.embedding for d in res.data]

def chat_stream(messages, model=Config.MODEL, temperature=0.1, **kwargs):
    return client.beta.chat.completions.stream(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs
    )
