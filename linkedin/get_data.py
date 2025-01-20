import requests
import json
from datetime import datetime

class LinkedInAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self):
        """Get user information using OpenID Connect userinfo endpoint"""
        url = "https://api.linkedin.com/v2/userinfo"
        try:
            response = requests.get(url, headers=self.headers)
            print(f"\nDebug UserInfo:")
            print(f"Status Code: {response.status_code}")
            if response.ok:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception in UserInfo: {str(e)}")
            return None

    def get_posts(self):
        """Get user's posts using w_member_social scope"""
        # Note: This might need different endpoint based on LinkedIn's documentation
        url = "https://api.linkedin.com/v2/ugcPosts"
        try:
            response = requests.get(url, headers=self.headers)
            print(f"\nDebug Posts:")
            print(f"Status Code: {response.status_code}")
            if response.ok:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception in Posts: {str(e)}")
            return None

def save_to_file(data, filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename

def main():
    ACCESS_TOKEN = "AQVvR30HTh9P9zjItMGPKuzlKjEtpaANfjQy0JjUChBehxdURD6CUCLgnAsONduhGtxhw4fToNq2hXta6wXtDTwumUd_ydZWhIxm6JWYlgwrxPysFg3Ns7ElJYNmrZe69ISBJyHa5EdN47NOnqiO3rtiQwD83pRQtN8eomNrIpj8N0ki9stnq5MgpWF3AgOHD1wyB9FIVizN6dfkKBANQGciLD23ydb7iDQr1f6HSq9TlWy-OwHvi15UHPqX1ga77_c6zeRlXMoQ4kS6O5F1IK0QE5f2UiLr1WIa7aYj0llnejqvjioFzSpbJeIgibF6mud1eVl2-Hn4US_wn0YmNaKoxjJbXg"
    
    linkedin = LinkedInAPI(ACCESS_TOKEN)
    
    # Get user info
    user_info = linkedin.get_user_info()
    posts = linkedin.get_posts()
    
    all_data = {
        "timestamp": datetime.now().isoformat(),
        "user_info": user_info,
        "posts": posts
    }
    
    # Print the collected data
    print("\n=== LinkedIn Profile Data ===")
    if user_info:
        print("\nUser Info:")
        print(json.dumps(user_info, indent=2))
    
    if posts:
        print("\nPosts:")
        print(json.dumps(posts, indent=2))
    
    # Save to file
    filename = save_to_file(all_data, "linkedin_data")
    print(f"\nComplete data has been saved to {filename}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {str(e)}")