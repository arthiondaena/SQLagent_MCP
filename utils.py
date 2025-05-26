import conf
from var import markdown_info, system_prompt_template
from dotenv import dotenv_values
from typing import List, Tuple
from openai import OpenAI
from sqlalchemy import (
    create_engine,
    MetaData,
    inspect,
    Table,
    select,
    distinct,
    text
)
from sqlalchemy.schema import CreateTable
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.engine import Engine
import re

env = dotenv_values()
uri = env['POSTGRES_URI']

def get_sample_rows(engine:Engine, table:Table, row_count: int = 3) -> str:
    """Gets the sample rows of a table using the SQLAlchemy engine"""
    # build the select command
    command = select(table).limit(row_count)

    # save the columns in string format
    columns_str = "\t".join([col.name for col in table.columns])

    try:
        # get the sample rows
        with engine.connect() as connection:
            sample_rows_result = connection.execute(command)  # type: ignore
            # shorten values in the sample rows
            sample_rows = list(
                map(lambda ls: [str(i)[:100] for i in ls], sample_rows_result)
            )

        # save the sample rows in string format
        sample_rows_str = "\n".join(["\t".join(row) for row in sample_rows])

    # in some dialects when there are no rows in the table a
    # 'ProgrammingError' is returned
    except ProgrammingError:
        sample_rows_str = ""

    return (
        f"{row_count} rows from {table.name} table:\n"
        f"{columns_str}\n"
        f"{sample_rows_str}"
    )

def get_unique_values(engine:Engine, table:Table) -> str:
    """Gets the unique values of each column in a table using the SQLAlchemy engine"""
    unique_values = {}
    for column in table.c:
        command = select(distinct(column))

        try:
            # get the sample rows
            with engine.connect() as connection:
                result = connection.execute(command)  # type: ignore
                # shorten values in the sample rows
                unique_values[column.name] = [str(u) for u in result]

            # save the sample rows in string format
            # sample_rows_str = "\n".join(["\t".join(row) for row in sample_rows])
            # in some dialects when there are no rows in the table a
            # 'ProgrammingError' is returned
        except ProgrammingError:
            unique_values[column.name] = ""

    output_str = f"Unique values of each column in {table.name}: \n"
    for column, values in unique_values.items():
        output_str += f"{column} has {len(values)} unique values: {' '.join(values[:20])}"
        if len(values) > 20:
            output_str += ", ...."
        output_str += "\n"

    return output_str

def get_info_sqlalchemy(uri:str = None) -> dict[str, str] | None:
    """Gets the dialect name, accessible tables and table schemas using the SQLAlchemy engine"""
    if uri is None:
        uri = env['POSTGRES_URI']
    engine = create_engine(uri)
    # Get dialect name using inspector
    inspector = inspect(engine)
    dialect = inspector.dialect.name
    # Metadata for tables and columns
    m = MetaData()
    m.reflect(engine)

    tables = {}
    for table in m.tables.values():
        tables[table.name] = str(CreateTable(table).compile(engine)).rstrip()
        tables[table.name] += "\n\n/*"
        tables[table.name] += "\n" + get_sample_rows(engine, table)+"\n"
        tables[table.name] += "\n" + get_unique_values(engine, table)+"\n"
        tables[table.name] += "*/"

    return {'sql_dialect': dialect, 'tables': ", ".join(tables.keys()), 'tables_schema': "\n\n".join(tables.values())}

def sql_inference(prompt: str, system_prompt: str) -> str:
    """Use the SQL_BASE_URL API to get the answer to a question"""
    client = OpenAI(
        base_url=conf.SQL_BASE_URL,
        api_key=env['SQL_MODEL_API_KEY']
    )
    # prompt = system_prompt + "\n\n" + prompt
    chat_completion = client.chat.completions.create(
        model=conf.SQL_MODEL,
        messages=[{
            "role": "system",
            "content": system_prompt
        },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=3000,
    )
    return chat_completion.choices[0].message.content

def sqlChatInfo(uri: str) -> str:
    """Get the information about a database in the form of a system prompt for the SQL agent"""
    db_info = get_info_sqlalchemy(uri)
    markdown = markdown_info.format(**db_info)
    system_prompt = system_prompt_template.format(markdown_info=markdown)
    return system_prompt

def extract_code_blocks(text):
    pattern = r"```(?:\w+)?\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches