from mcp.server.fastmcp import FastMCP

from utils import sqlChatInfo, sql_inference, extract_code_blocks
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

env = dotenv_values()

uri = env['POSTGRES_URI']

mcp = FastMCP("test")
system_prompt = sqlChatInfo(uri)

@mcp.tool()
def bookings_database(question: str) -> str:
    """Returns the answer to a question which will be retrieved from a database,
     which contains all the customer booking information
     The function returns a string which contains a list of tuples. Each tuple contains the resultant row from the database query.
     After calling the function, use ast.literal_eval to convert the string to a list of tuples.
     It is very important to use ast.literal_eval after calling the function to avoid errors.
     Don't print all the results since it can consume a large number of tokens, use slicing to print only a subset of results.
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

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
