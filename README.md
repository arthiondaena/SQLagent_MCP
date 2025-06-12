# SQLagent_MCP

This project provides an interface for querying a bookings database using natural language, with support for multiple server backends (STDIO, SSE, HTTP) and a client agent.

## Setup

1. **Clone the repository** and navigate to the project directory.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Unix/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install the requirements**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:

   - Create a `.env` file in the project root with your database and API keys, e.g.:
     ```
     POSTGRES_URI=your_postgres_connection_string
     SQL_MODEL_API_KEY=your_api_key
     ```

---

## Server Types

- **STDIO Server**: Communicates via standard input/output. Useful for local, simple agent-server interaction.
- **SSE Server**: Uses Server-Sent Events over HTTP for streaming responses.
- **HTTP Server**: Uses HTTP with streamable responses for integration with web clients or APIs.

---

## Running with STDIO

1. **Uncomment the STDIO server parameter line** in `mcp_smol_client.py`:
   ```python
   server_parameters = StdioServerParameters(command="python", args=["mcp_stdio_server.py"])
   ```
   (Comment out any other `server_parameters` lines.)

2. **Run the client**:
   ```bash
   python mcp_smol_client.py
   ```

---

## Running with SSE

1. **Start the SSE server**:
   ```bash
   python mcp_sse_server.py
   ```

2. **Uncomment the SSE server parameter line** in `mcp_smol_client.py`:
   ```python
   # server_parameters = {"url": "http://localhost:3005/sse"}
   ```
   (Comment out any other `server_parameters` lines.)

3. **Run the client**:
   ```bash
   python mcp_smol_client.py
   ```

---

## Running with HTTP

1. **Start the HTTP server**:
   ```bash
   python mcp_http_server.py
   ```

2. **Uncomment the HTTP server parameter line** in `mcp_smol_client.py`:
   ```python
   # server_parameters = {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable-http"}
   ```
   (Comment out any other `server_parameters` lines.)

3. **Run the client**:
   ```bash
   python mcp_smol_client.py
   ```

---

## Notes

- Only one server should be running at a time.
- Make sure to set the correct environment variables before running the servers or client.
- For more details, refer to the comments in each Python file.
