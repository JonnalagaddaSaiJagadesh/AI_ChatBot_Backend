from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from pydantic import BaseModel
from typing import List, Union
import openai  # Assuming you use an OpenAI-compatible LLM (e.g., GPT-4, Ollama)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2362",  # Make sure to use your correct MySQL credentials
        database="chatbot"  # Replace with your database name
    )

# Product Query Model
class ProductQuery(BaseModel):
    query: str

class ResponseModel(BaseModel):
    response: Union[str, List[dict]]

# Open-source LLM API call (adjust based on your chosen LLM provider)
def query_llm(user_query: str) -> str:
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Replace with your LLM model, e.g., "gpt-3.5-turbo" or "ollama/gpt4all"
            prompt=f"Answer this query based on product and supplier details: {user_query}",
            max_tokens=100
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print("LLM Error:", e)
        return "I'm unable to process this request right now. Please try again later."

# Endpoint to handle product queries
@app.post("/query/", response_model=ResponseModel)
async def get_query(query: ProductQuery):
    search_term = query.query.strip().lower()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Check for basic responses in chatbot_responses table
    cursor.execute("""
        SELECT response FROM chatbot_responses
        WHERE LOWER(query) = %s
    """, (search_term,))
    basic_response = cursor.fetchone()

    if basic_response:
        cursor.close()
        connection.close()
        return {"response": basic_response["response"]}  # Return predefined response

    # Check for products and supplier details
    cursor.execute("""
        SELECT p.name, p.description, p.price, 
               s.name AS supplier_name, s.contact_name AS supplier_contact_name, 
               s.contact_email AS supplier_contact_email, s.contact_phone AS supplier_contact_phone
        FROM products p
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE LOWER(p.name) LIKE %s OR LOWER(p.description) LIKE %s
    """, (f"%{search_term}%", f"%{search_term}%"))
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    if products:
        return {"response": products}  # Return product details
    
    # If no predefined response or product, use LLM
    llm_response = query_llm(search_term)
    return {"response": llm_response}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}
@app.post("/query/")
async def query_endpoint(data: dict):
    return {"response": "Your query response"}
