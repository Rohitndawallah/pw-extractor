# core/auth_api.py
import os
import requests
from typing import Tuple, Union
from dotenv import load_dotenv

# Constants
ORG_ID = "5eb393ee95fab7468a79d189"
BASE_URL = "https://api.penpencil.co"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer": "https://www.pw.live/",
    "Randomid": "a997919f-4400-4416-a447-fe172d4d9be4"
}

def _get_auth_headers() -> dict:
    """Return a copy of HEADERS with Authorization from .env added."""
    load_dotenv(dotenv_path="data/.env")
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("Access token not found in .env")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    return headers

def send_otp(username: str, country_code: str) -> Tuple[bool, Union[str, dict]]:
    """
    Sends OTP to the user's phone number.
    
    Args:
        username (str): Phone number of the user.
        country_code (str): Country code like '+91'.
    
    Returns:
        Tuple[bool, Union[str, dict]]: (True, success message) or (False, error dict)
    """
    url = f"{BASE_URL}/v1/users/get-otp?smsType=0"
    body = {
        "username": username,
        "countryCode": country_code,
        "organizationId": ORG_ID
    }

    try:
        response = requests.post(url, json=body, headers=HEADERS)
        data = response.json()

        if data.get("success"):
            return True, "OTP sent successfully."
        else:
            return False, {
                "message": data.get("error", {}).get("message", "Unknown error."),
                "status": data.get("error", {}).get("status", 400)
            }
    except Exception as e:
        return False, {"message": str(e), "status": 500}


def get_token(username: str, otp: str) -> Tuple[bool, Union[dict, dict]]:
    """
    Verifies OTP and returns access token and expiry.
    
    Args:
        username (str): Phone number of the user.
        otp (str): OTP entered by the user.
    
    Returns:
        Tuple[bool, Union[dict, dict]]: 
            - On success: (True, {'access_token': ..., 'expires_in': ...})
            - On error: (False, {'message': ..., 'status': ...})
    """
    url = f"{BASE_URL}/v3/oauth/token"
    body = {
        "username": username,
        "otp": otp,
        "client_id": "system-admin",
        "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
        "grant_type": "password",
        "latitude": 0,
        "longitude": 0,
        "organizationId": ORG_ID
    }

    try:
        response = requests.post(url, json=body)
        data = response.json()

        if data.get("success"):
            return True, {
                "access_token": data["data"]["access_token"],
                "expires_in": data["data"]["expires_in"]
            }
        else:
            return False, {
                "message": data.get("error", {}).get("message", "Invalid OTP or Username."),
                "status": data.get("error", {}).get("status", 412)
            }
    except Exception as e:
        return False, {"message": str(e), "status": 500}


def verify_token() -> Tuple[bool, Union[str, dict]]:
    """
    Verifies the access token stored in the .env file.

    Returns:
        Tuple[bool, Union[str, dict]]:
            - On success: (True, "Token is valid.")
            - On error: (False, {'message': ..., 'status': ...})
    """
    url = f"{BASE_URL}/v3/oauth/verify-token"
    headers = _get_auth_headers()  # ✅ Now pulls headers with Authorization included

    try:
        response = requests.post(url, headers=headers)  # ✅ Use POST (not GET)
        data = response.json()

        if data.get("success") and data.get("data", {}).get("isVerified"):
            return True, "Token is valid."
        else:
            return False, {
                "message": data.get("error", {}).get("message", "Unauthorized Access"),
                "status": data.get("error", {}).get("status", 401)
            }
    except Exception as e:
        return False, {"message": str(e), "status": 500}
