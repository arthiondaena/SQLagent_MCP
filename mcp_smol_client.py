from smolagents import CodeAgent, ToolCollection, OpenAIServerModel
from mcp.client.stdio import StdioServerParameters
import conf
from dotenv import load_dotenv
import os

load_dotenv()

model = OpenAIServerModel(
        model_id=conf.SQL_MODEL,
        api_base=conf.SQL_BASE_URL,
        api_key=os.environ['SQL_MODEL_API_KEY']
    )

# For STDIO server
server_parameters = StdioServerParameters(command="python", args=["mcp_stdio_server.py"])

# For SSE server
# server_parameters = {"url": "http://localhost:3005/sse"}

# For streamable HTTP:
# Streamable HTTP support implementation is in progress for smolagents. https://github.com/huggingface/smolagents/pull/1384
# server_parameters = {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable-http"}

with ToolCollection.from_mcp(
    server_parameters,
    trust_remote_code=True
) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], model=model, max_steps=10, verbosity_level=2,
                      additional_authorized_imports=['matplotlib.pyplot', 'ast', 'pandas', 'eval'])
    agent.run("Plot a graph for number of bookings each theatre has received")
