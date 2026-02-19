"""Fetch royalty-free visual assets for devotional videos."""
import requests
import time
from pathlib import Path
from typing import List, Dict
from config import Config

class VisualAssetFetcher:
    """Fetch royalty-free images and videos for Radha Krishna devotional content."""
    
    def __init__(self):
        """Initialize the visual asset fetcher."""
        self.pexels_key = Config.PEXELS_API_KEY
        self.pixabay_key = Config.PIXABAY_API_KEY
    
    def fetch_images(
        self, 
        query: str, 
        num_images: int = 10,
        output_dir: Path = None
    ) -> List[Path]:
        """
        Fetch royalty-free images.
        
        Args:
            query: Search query (e.g., "krishna", "radha", "temple", "flowers")
            num_images: Number of images to fetch
            output_dir: Directory to save images
            
        Returns:
            List of paths to downloaded images
        """
        output_dir = Path(output_dir or Config.TEMP_DIR / "images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        images = []
        
        # Try Pexels first if available
        if self.pexels_key:
            try:
                images = self._fetch_from_pexels(query, num_images, output_dir)
            except Exception as e:
                print(f"Pexels fetch failed: {e}")
        
        # Try Pixabay if Pexels didn't work or wasn't available
        if not images and self.pixabay_key:
            try:
                images = self._fetch_from_pixabay(query, num_images, output_dir)
            except Exception as e:
                print(f"Pixabay fetch failed: {e}")
        
        # If no API keys or both failed, provide guidance
        if not images:
            print(f"\nNo images fetched. To fetch images automatically:")
            print("1. Get a free API key from https://www.pexels.com/api/ or https://pixabay.com/api/docs/")
            print("2. Add it to your .env file")
            print(f"\nAlternatively, manually download images with query '{query}' to: {output_dir}")
        
        return images
    
    def _fetch_from_pexels(
        self, 
        query: str, 
        num_images: int, 
        output_dir: Path
    ) -> List[Path]:
        """Fetch images from Pexels API."""
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/v1/search"
        
        params = {
            "query": query,
            "per_page": num_images,
            "orientation": "landscape"
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        image_paths = []
        
        for i, photo in enumerate(data.get("photos", [])):
            image_url = photo["src"]["large"]
            image_path = output_dir / f"pexels_{query}_{i+1:03d}.jpg"
            
            # Download image
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            with open(image_path, "wb") as f:
                f.write(img_response.content)
            
            image_paths.append(image_path)
            print(f"Downloaded: {image_path.name}")
            
            # Be respectful with API rate limits
            time.sleep(0.5)
        
        return image_paths
    
    def _fetch_from_pixabay(
        self, 
        query: str, 
        num_images: int, 
        output_dir: Path
    ) -> List[Path]:
        """Fetch images from Pixabay API."""
        url = "https://pixabay.com/api/"
        
        params = {
            "key": self.pixabay_key,
            "q": query,
            "image_type": "photo",
            "orientation": "horizontal",
            "per_page": num_images
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        image_paths = []
        
        for i, hit in enumerate(data.get("hits", [])):
            image_url = hit["largeImageURL"]
            image_path = output_dir / f"pixabay_{query}_{i+1:03d}.jpg"
            
            # Download image
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            with open(image_path, "wb") as f:
                f.write(img_response.content)
            
            image_paths.append(image_path)
            print(f"Downloaded: {image_path.name}")
            
            # Be respectful with API rate limits
            time.sleep(0.5)
        
        return image_paths
    
    def get_devotional_queries(self) -> List[str]:
        """Get search queries for devotional visuals."""
        return [
            "hindu temple",
            "lotus flower",
            "diya lamp",
            "peacock feather",
            "sunrise spiritual",
            "meditation nature",
            "indian spiritual",
            "sacred geometry",
            "mandala art",
            "spiritual light",
            "temple bells",
            "incense smoke",
            "flower offering",
            "spiritual garden",
            "sacred river"
        ]
    
    def fetch_diverse_images(
        self, 
        num_total: int = 30, 
        output_dir: Path = None
    ) -> List[Path]:
        """
        Fetch a diverse set of devotional images using multiple queries.
        
        Args:
            num_total: Total number of images to fetch
            output_dir: Directory to save images
            
        Returns:
            List of paths to downloaded images
        """
        queries = self.get_devotional_queries()
        images_per_query = max(2, num_total // len(queries))
        
        all_images = []
        
        for query in queries[:num_total // images_per_query]:
            print(f"\nFetching images for: {query}")
            images = self.fetch_images(query, images_per_query, output_dir)
            all_images.extend(images)
            
            if len(all_images) >= num_total:
                break
        
        return all_images[:num_total]
