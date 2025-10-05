# Copyright 2025 jainendra. 
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit_okta import okta_login_wrapper
from dotenv import load_dotenv
import os
import requests
from fastmcp import Client
from fastmcp.client.auth import BearerAuth
import asyncio
import time

import tracemalloc
tracemalloc.start()

load_dotenv()

provider_url=os.getenv("provider_url")
client_id=os.getenv("client_id")
client_secret=os.getenv("client_serret")
base_url=os.getenv("base_url")
redirect_uri = os.getenv("redirect_uri")
mcpserver_url = os.getenv("mcpserver_url")
mcpclient_url = os.getenv("mcpclient_url")


def send_token_to_mcp_server(token):
    """
    Send the access token to the MCP server for validation.
    """
    mcp_server_url = f"{mcpserver_url}/verify_token"
    headers = {"Authorization": token}

    response = requests.post(mcp_server_url, headers=headers)

    if response.status_code == 200:
        st.success("Token is valid. Connected to MCP server.")
    else:
        st.error(f"Failed to connect to MCP server: {response.text}")


async def list_tools_from_mcp_server(token):
    """
    Fetch and display all tools available in the MCP server.
    """
    client = Client(f"{mcpserver_url}/mcp", auth=BearerAuth(token=token))
    #await client.ping()

    # Await the coroutine to get the actual list of tools
    async with client:
        tools = await client.list_tools()

    final_tool = []

    st.info(f"Total tools available: {len(tools)}")
    for t in tools:
         final_dict = {
             "name": t.name,
             "description": t.description,
             "schema": t.inputSchema,
         }
         final_tool.append(final_dict)

    st.header("Available Tools on MCP Server")
    for tool in final_tool:
        st.write(f"- {tool['name']}: {tool['description']}")
        st.write(f"schema: {t.inputSchema}\n")

    return {"Available tools on this MCP server": final_tool}




async def app():
    # Here came your business logic
    st.header("You are logged in successfully!")

    if "token" in st.session_state:
        access_token = st.session_state["token"]["access_token"]
        send_token_to_mcp_server(access_token)
        await list_tools_from_mcp_server(access_token)



async def main():
    okta_config = {
        "okta_base_url": base_url,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }

    await okta_login_wrapper(okta_config, app)  # Call synchronously

    time.sleep(2)

    st.info("session info")

    st.info(st.session_state)

    if "token" in st.session_state:
        access_token = st.session_state["token"]["access_token"]

    client = Client(f"{mcpserver_url}/mcp", auth=BearerAuth(token=access_token))
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        #toools metadata
        st.info(tools)
        
        # Execute operations
        input_data = {"data": "jainendra","token":access_token}
        st.write()
        result = await client.call_tool(tools[0].name, input_data)
        st.write(f"Tool Name: ", tools[0].name, f"Tool description: ",tools[0].description)
        st.write("Result from tool execution:")
        st.info(result.content)
        

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())  # Use asyncio.run to execute the main coroutine
    except Exception as e:
        st.write(e)
        raise e
