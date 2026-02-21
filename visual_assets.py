"""Fetch royalty-free visual assets for devotional videos."""
import base64
import requests
import time
import re
from pathlib import Path
from typing import List, Dict
from config import Config

class VisualAssetFetcher:
    """Fetch royalty-free images and videos for Radha Krishna devotional content."""
    
    def __init__(self):
        """Initialize the visual asset fetcher."""
        self.google_key = Config.GOOGLE_API_KEY
        self.pexels_key = Config.PEXELS_API_KEY
        self.pixabay_key = Config.PIXABAY_API_KEY
        self.google_image_model = Config.GOOGLE_IMAGE_MODEL
        self.visual_provider_order = [
            p.strip().lower()
            for p in Config.VISUAL_PROVIDER_ORDER.split(",")
            if p.strip()
        ]
    
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
        images: List[Path] = []

        provider_order = self.visual_provider_order or ["google", "pexels", "pixabay"]

        for provider in provider_order:
            if images:
                break

            try:
                if provider == "google" and self.google_key:
                    images = self._generate_with_google(query, num_images, output_dir)
                elif provider == "pexels" and self.pexels_key:
                    images = self._fetch_from_pexels(query, num_images, output_dir)
                elif provider == "pixabay" and self.pixabay_key:
                    images = self._fetch_from_pixabay(query, num_images, output_dir)
            except Exception as e:
                print(f"{provider.title()} visual generation failed: {e}")
        
        # If no API keys or both failed, provide guidance
        if not images:
            print(f"\nNo images fetched. To fetch images automatically:")
            print("1. Add GOOGLE_API_KEY (AI Studio) or PEXELS_API_KEY / PIXABAY_API_KEY")
            print("2. Optional: set VISUAL_PROVIDER_ORDER=google,pexels,pixabay")
            print(f"\nAlternatively, manually download images with query '{query}' to: {output_dir}")
        
        return images

    def _sanitize_query(self, query: str) -> str:
        """Return a filesystem-safe query string."""
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", query.strip().lower())
        return cleaned.strip("_") or "scene"

    def _generate_with_google(
        self,
        query: str,
        num_images: int,
        output_dir: Path,
    ) -> List[Path]:
        """Generate images with Google Gemini image generation."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.google_image_model}:generateContent"
        )
        params = {"key": self.google_key}
        query_slug = self._sanitize_query(query)

        prompt = (
            f"Create a high-quality cinematic 16:9 devotional background image for: {query}. "
            "No text, no watermark, no logos, no people posing for camera, "
            "soft spiritual ambience, natural colors, suitable for video storytelling."
        )

        image_paths: List[Path] = []
        for idx in range(num_images):
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"],
                    "temperature": 0.8,
                },
            }

            response = requests.post(url, params=params, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            image_bytes = self._extract_image_bytes(data)
            if not image_bytes:
                raise RuntimeError(
                    f"Google image response did not include image bytes for query '{query}'"
                )

            image_path = output_dir / f"google_{query_slug}_{idx+1:03d}.png"
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)
            print(f"Generated: {image_path.name}")
            time.sleep(0.2)

        return image_paths

    def _extract_image_bytes(self, response_json: Dict) -> bytes:
        """Extract inline image bytes from Gemini generateContent response."""
        for candidate in response_json.get("candidates", []):
            content = candidate.get("content", {})
            for part in content.get("parts", []):
                inline_data = part.get("inlineData") or {}
                encoded = inline_data.get("data")
                if encoded:
                    return base64.b64decode(encoded)

        return b""
    
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
