# test_tui.py

from core.auth import send_otp, get_auth_token, verify_token
from core.token_manager import load_access_token
from core.countries import COUNTRY_CODES, get_country_code
from core.batches import fetch_purchased_batches, save_batches_to_file, get_saved_batches

def select_country():
    print("Select your country:")
    for idx, country in enumerate(COUNTRY_CODES.keys(), start=1):
        print(f"{idx}. {country}")
    choice = int(input("Enter choice number: "))
    country_name = list(COUNTRY_CODES.keys())[choice - 1]
    return country_name, get_country_code(country_name)

def main():
    print("=== PW Extractor Auth Test ===")

    # Select country
    country_name, country_code = select_country()
    print(f"Selected country: {country_name} ({country_code})")

    # Enter phone
    phone = input("Enter your phone number: ").strip()

    # Send OTP
    print("Sending OTP...")
    send_otp(phone, country_code)


    # Enter OTP
    otp = input("Enter the OTP received: ").strip()

    # Get token
    print("Authenticating...")
    if not get_auth_token(phone, otp):
        print("❌ Failed to authenticate. Check OTP or try again.")
        return
    print("✅ Token saved to .env")

    # Verify token
    token = load_access_token()
    print("Verifying saved token...")
    if verify_token(token):
        print("✅ Token is valid!")
    else:
        print("❌ Token is invalid or expired.")

if __name__ == "__main__":
    main()
