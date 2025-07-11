import requests
from core.token_manager import save_tokens_to_env
from core.headers import get_default_headers

ORG_ID = "5eb393ee95fab7468a79d189"
CLIENT_ID = "system-admin"
CLIENT_SECRET = "KjPXuAVfC5xbmgreETNMaL7z"

def send_otp(phone_number: str, country_code: str):
    url = "https://api.penpencil.co/v1/users/get-otp?smsType=0"
    payload = {
        "username": phone_number,
        "countryCode": country_code,
        "organizationId": ORG_ID
    }
    try:
        response = requests.post(url, json=payload, headers=get_default_headers())
        response.raise_for_status()  # Raises exception if 4xx or 5xx
        print("✅ OTP sent successfully!")
    except requests.exceptions.RequestException as e:
        print("❌ Failed to send OTP.")
        print(f"Error: {e}")



def get_auth_token(phone_number: str, otp: str) -> bool:
    url = "https://api.penpencil.co/v3/oauth/token"
    payload = {
        "username": phone_number,
        "otp": otp,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",
        "latitude": 0,
        "longitude": 0,
        "organizationId": ORG_ID
    }
    response = requests.post(url, json=payload, headers=get_default_headers())
    if response.status_code == 200 and response.json().get("success", False):
        data = response.json()["data"]
        access_token = data["access_token"]
        expires_in = str(data["expires_in"])
        save_tokens_to_env(access_token, expires_in)
        return True
    return False

def verify_token(token: str) -> bool:
    url = "https://api.penpencil.co/v3/oauth/verify-token"
    headers = get_default_headers(token)
    response = requests.post(url, headers=headers)
    json_data = response.json()
    return json_data.get("success", False) and json_data.get("data", {}).get("isVerified", False)
