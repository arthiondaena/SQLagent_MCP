from mcp.server.fastmcp import FastMCP
from starlette.routing import Mount

from utils import sqlChatInfo, sql_inference, extract_code_blocks
from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from fastapi import FastAPI

env = dotenv_values()

uri = env['POSTGRES_URI']

mcp = FastMCP("test")
system_prompt = sqlChatInfo(uri)

@mcp.tool()
def bookings_database(question: str) -> str:
    """Return the answer to a question which will be retrieved from a database,
     which contains all the customer booking information
     The function returns a list of tuples. Each tuple contains the resultant row from the database query.
     The database contains information like mail, phone number, name, date, slot, booking date, booking time.
     DO NOT ask the bookings_database to retrieve all the booking information or all the theatre bookings.
     Example question:
     1. What are the top 3 most booked theatres?
     2. Who are the top 3 most visited customers?
     3. What are the number of bookings monthly?
     Example function call
     >> bookings_database("What are the top 3 most booked theatres?")
     Args:
        question: The question to be answered.
    """
    query = sql_inference(question, system_prompt)
    query = extract_code_blocks(query)[0]
    db = create_engine(uri)
    with db.connect() as conn:
        q_result = conn.execute(text(query)).fetchall()
    result = [t._tuple() for t in q_result]
    return str(result)

# Create a FastAPI app
app = FastAPI(
    title="MCP API Server",
    description="MCP Server with API Key Authentication",
    version="1.0.0"
)

app.routes.append(Mount('/', app=mcp.sse_app()))

if __name__ == "__main__":
    # mcp.run(transport="streamable-http")
    mcp.settings.port = 3005

    # Run FastAPI app with uvicorn instead of the MCP app directly
    import uvicorn

    uvicorn.run(app, host=mcp.settings.host, port=mcp.settings.port)
