from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import re
import json
from urllib.parse import unquote


app = FastAPI(title="SQLite Query Service", version="1.0.0")

# Allow all origins (you can restrict later if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_PATH = "DATA/data.db"  # Path to your SQLite file

@app.post("/query")
def run_query(q: str = Query(..., description="SQL SELECT query")):
    try:
        # Decode the query so spaces and symbols work correctly
        decoded_query = unquote(q)
        print("decoded_query", decoded_query)
        converted = q.replace(" ", "+")
        print("converted", converted)
        
        # Optional: restrict to SELECT statements only
        if not decoded_query.strip().lower().startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
        
        conn = sqlite3.connect("data.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(decoded_query)
        rows = cursor.fetchall()
        conn.close()

        return {"rows_returned": len(rows), "data": [dict(row) for row in rows]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def root():
    return {
        "message": "SQLite Query API is running. Use /query?q=SELECT * FROM TABLE to query data."
    }

