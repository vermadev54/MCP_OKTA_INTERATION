from fastmcp import FastMCP
from dataclasses import dataclass
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from dotenv import load_dotenv
import os
import jwt
import requests
import logging
from streamlit_okta.auth.okta import Okta

load_dotenv()

provider_url = os.getenv("provider_url")
client_id = os.getenv("client_id")
client_secret = os.getenv("client_serret")
base_url = os.getenv("base_url")

# Initialize Okta configuration
okta_config = {
    "okta_base_url": base_url,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": base_url  # Assuming base_url is used as redirect_uri
}
okta = Okta(okta_config)

mcp = FastMCP("MyServer")

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

@mcp.custom_route("/verify_token", methods=["POST"])
async def verify_token(request: Request) -> PlainTextResponse:
    """
    Verify the token sent by the client using Okta's verify_tokens_from_okta method.
    """
    token = request.headers.get("Authorization")
    if not token:
        return PlainTextResponse("Missing token", status_code=401)

    try:
        # Use Okta's verify_tokens_from_okta method
        okta.verify_tokens_from_okta(access_token=token, refresh_token="")
        return PlainTextResponse("Token is valid", status_code=200)
    except Exception as e:
        return PlainTextResponse(f"Invalid token: {str(e)}", status_code=401)


@mcp.tool
async def process(data: str, token: str) -> str:
    """
    Process data only if the token is valid.
    """

    try:
        # Use Okta's verify_tokens_from_okta method
        okta.verify_tokens_from_okta(access_token=token, refresh_token="")
        return (f"Token is valid and Processed data is : {data})")

    except Exception as e:
        return PlainTextResponse(f"Invalid token: {str(e)}", status_code=401)

@dataclass
class Person:
    name: str
    age: int
    email: str

@mcp.tool
async def get_user_profile(user_id: str, token: str) -> Person:
    """
    Get a user's profile information only if the token is valid.
    """
    try:
        # Use Okta's verify_tokens_from_okta method
        okta.verify_tokens_from_okta(access_token=token, refresh_token="")
        return ("Token is valid")
    except Exception as e:
        return PlainTextResponse(f"Invalid token: {str(e)}", status_code=401)


if __name__ == "__main__":
    mcp.run(transport="http")  # Health check at http://localhost:8000/health