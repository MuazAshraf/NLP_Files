import requests
import webbrowser
from urllib.parse import urlencode

# Your LinkedIn application credentials
CLIENT_ID = "77b10ivd233hfp"
CLIENT_SECRET = "WPL_AP1.G3vf8Oqtjr4dOoUu.h74dLQ=="
REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = "openid profile w_member_social email"

def get_authorization_url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

def get_access_token(auth_code):
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    params = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=params)
    return response.json()

if __name__ == "__main__":
    # 1. First get a new authorization code
    auth_url = get_authorization_url()
    print("Please visit this URL to authorize the application:")
    print(auth_url)
    webbrowser.open(auth_url)
    
    # 2. After authorization, get the code from the user
    auth_code = input("\nEnter the authorization code from the callback URL: ")
    
    # 3. Exchange the code for an access token
    result = get_access_token(auth_code)
    print("\nResponse:", result)
