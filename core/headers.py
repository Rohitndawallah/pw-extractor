def get_default_headers(token: str = ""):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Referer": "https://www.pw.live/",
        "Randomid": "a997919f-4400-4416-a447-fe172d4d9be4"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
