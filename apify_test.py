from apify_client import ApifyClientAsync
import asyncio
import os
import json
from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get API token from environment variable for security
API_TOKEN = os.environ.get("APIFY_API_TOKEN", "apify_api_FbtkrS4Yfjd5l893XxdabBHd1j2GoD1jzqDn")
if not API_TOKEN:
    logger.error("APIFY_API_TOKEN environment variable is not set")
    exit(1)

# Configuration - easily adjustable
CONFIG = {
    "output_dir": "instagram_data",
    "save_to_json": True,
    "max_retries": 3,
    "retry_delay": 5,  # seconds
    "target_usernames": ["instagram"]  # Replace with usernames you want to scrape
}

# Define scraper configurations
SCRAPERS = {
    "profiles": {
        "actor_id": "apify/instagram-profile-scraper",
        "input": {
            "usernames": CONFIG["target_usernames"],
            "resultsType": "details",  # Get detailed profile information
            "searchLimit": 1           # We need just 1 result per username
        }
    },
    "posts": {
        "actor_id": "apify/instagram-post-scraper",
        "input": {
            "usernames": CONFIG["target_usernames"],
            "resultsLimit": 100,       # Increase this if you need more posts
            "additionalData": True,    # Get additional post metadata
            "expandOwners": True       # Include user info for post owners
        }
    },
    "comments": {
        "actor_id": "apify/instagram-comment-scraper",
        "input": {
            # Will be populated dynamically after post scraping
            "postUrls": [],
            "maxItems": 50             # Max comments per post
        }
    }
}

class InstagramScraper:
    def __init__(self, api_token: str, config: Dict[str, Any]):
        self.client = ApifyClientAsync(api_token)
        self.config = config
        self.results = {}
        
        # Create output directory if it doesn't exist
        if self.config["save_to_json"]:
            os.makedirs(self.config["output_dir"], exist_ok=True)

    async def run_scraper(self, name: str, actor_id: str, run_input: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        logger.info(f"Starting {name} scraper...")
        
        # Implement retry logic
        for attempt in range(1, self.config["max_retries"] + 1):
            try:
    # Run the Actor and wait for it to finish
                run = await self.client.actor(actor_id).call(run_input=run_input)
                
                if not run or "defaultDatasetId" not in run:
                    logger.error(f"Failed to run {name} scraper: Invalid response")
                    return None

                # Get dataset client for the run
                dataset_client = self.client.dataset(run["defaultDatasetId"])
                
                # Get all items from the dataset
                items = []
                async for item in dataset_client.iterate_items():
                    items.append(item)
                
                # Save results to JSON if configured
                if self.config["save_to_json"] and items:
                    output_file = os.path.join(self.config["output_dir"], f"{name}_data.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(items, f, ensure_ascii=False, indent=2)
                    logger.info(f"Saved {len(items)} items to {output_file}")
                
                logger.info(f"Successfully scraped {len(items)} items from {name}")
                return items
                
            except Exception as e:
                if attempt < self.config["max_retries"]:
                    logger.warning(f"Attempt {attempt} failed for {name}: {str(e)}. Retrying in {self.config['retry_delay']} seconds...")
                    await asyncio.sleep(self.config["retry_delay"])
                else:
                    logger.error(f"All {self.config['max_retries']} attempts failed for {name}: {str(e)}")
                    return None

    async def scrape_user_complete_data(self):
        """Scrape complete data for Instagram users: profile info and all posts with details"""
        # 1. Get profile information
        profiles = await self.run_scraper("profiles", SCRAPERS["profiles"]["actor_id"], SCRAPERS["profiles"]["input"])
        if not profiles:
            logger.error("Failed to scrape profile data, stopping")
            return
            
        self.results["profiles"] = profiles
        logger.info(f"Scraped profile information for {len(profiles)} users")
        
        # 2. Get all posts for these users
        posts = await self.run_scraper("posts", SCRAPERS["posts"]["actor_id"], SCRAPERS["posts"]["input"])
        if not posts:
            logger.error("Failed to scrape posts data, stopping")
            return
            
        self.results["posts"] = posts
        logger.info(f"Scraped {len(posts)} posts from target users")
        
        # 3. Extract post URLs to scrape comments if needed
        if len(posts) > 0 and "comments" in SCRAPERS:
            # Get post URLs from the results (limited to the first 10 to avoid rate limits)
            post_urls = [post.get("url", "") for post in posts[:10] if post.get("url")]
            
            if post_urls:
                # Update comments scraper input with post URLs
                SCRAPERS["comments"]["input"]["postUrls"] = post_urls
                
                # Get comments for these posts
                comments = await self.run_scraper(
                    "comments", 
                    SCRAPERS["comments"]["actor_id"], 
                    SCRAPERS["comments"]["input"]
                )
                if comments:
                    self.results["comments"] = comments
                    logger.info(f"Scraped comments for {len(post_urls)} posts")
            else:
                logger.warning("No post URLs found for comment scraping")
        
        # 4. Create a consolidated report
        self.generate_consolidated_report()
    
    def generate_consolidated_report(self):
        """Generate a consolidated report with all user data"""
        report = {}
        
        # Process profile data
        for profile in self.results.get("profiles", []):
            username = profile.get("username")
            if not username:
                continue
                
            report[username] = {
                "profile": {
                    "username": username,
                    "full_name": profile.get("fullName", ""),
                    "biography": profile.get("biography", ""),
                    "followers_count": profile.get("followersCount", 0),
                    "following_count": profile.get("followingCount", 0),
                    "posts_count": profile.get("postsCount", 0),
                    "highlights_count": profile.get("highlightsCount", 0),
                    "is_private": profile.get("private", False),
                    "is_verified": profile.get("verified", False),
                    "profile_pic_url": profile.get("profilePicUrl", ""),
                    "external_url": profile.get("externalUrl", "")
                },
                "posts": []
            }
        
        # Add post data to respective users
        for post in self.results.get("posts", []):
            username = post.get("ownerUsername")
            if not username or username not in report:
                continue
                
            # Extract hashtags from caption
            caption = post.get("caption", "")
            hashtags = []
            if caption:
                hashtags = [word for word in caption.split() if word.startswith("#")]
            
            # Add post details to user's posts
            post_data = {
                "id": post.get("id", ""),
                "shortcode": post.get("shortCode", ""),
                "url": post.get("url", ""),
                "caption": caption,
                "hashtags": hashtags,
                "mentions": [word for word in caption.split() if word.startswith("@")],
                "likes_count": post.get("likesCount", 0),
                "comments_count": post.get("commentsCount", 0),
                "timestamp": post.get("timestamp", ""),
                "location": post.get("locationName", ""),
                "is_video": post.get("isVideo", False),
                "video_view_count": post.get("videoViewCount", 0) if post.get("isVideo", False) else 0,
                "image_url": post.get("displayUrl", "")
            }
            
            # Add post data to user's posts list
            report[username]["posts"].append(post_data)
        
        # Save consolidated report
        if report and self.config["save_to_json"]:
            output_file = os.path.join(self.config["output_dir"], "consolidated_user_data.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved consolidated user data to {output_file}")
            
            # Also create user-specific files for easier access
            for username, user_data in report.items():
                output_file = os.path.join(self.config["output_dir"], f"user_{username}_data.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved user data for {username} to {output_file}")

async def main():
    # Initialize the scraper
    scraper = InstagramScraper(API_TOKEN, CONFIG)
    
    # Run complete user data scraping
    await scraper.scrape_user_complete_data()

if __name__ == "__main__":
    asyncio.run(main())




