"""Script generator for devotional video content using OpenAI."""
import openai
from typing import Dict, List
from config import Config

class DevotionalScriptGenerator:
    """Generate devotional scripts for Radha Krishna videos."""
    
    def __init__(self):
        """Initialize the script generator."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = Config.OPENAI_API_KEY
        self.duration_minutes = Config.VIDEO_DURATION_MINUTES
    
    def generate_script(self, theme: str = None) -> Dict[str, any]:
        """
        Generate a devotional script.
        
        Args:
            theme: Optional theme for the devotional content
            
        Returns:
            Dictionary with script segments, timing, and metadata
        """
        prompt = self._create_prompt(theme)
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a spiritual guide creating devotional content about Radha Krishna. Your content is peaceful, uplifting, and appropriate for meditation and spiritual reflection."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            script_content = response.choices[0].message.content
            
            # Parse and structure the script
            return self._structure_script(script_content, theme)
            
        except Exception as e:
            raise Exception(f"Error generating script: {str(e)}")
    
    def _create_prompt(self, theme: str = None) -> str:
        """Create the prompt for script generation."""
        base_theme = theme or "divine love and devotion"
        
        prompt = f"""Create a {self.duration_minutes}-minute devotional meditation script about Radha Krishna.

Theme: {base_theme}

Requirements:
1. The script should be calming, spiritual, and appropriate for meditation
2. Include teachings about devotion, love, and spiritual growth
3. Reference stories or qualities of Radha and Krishna
4. The tone should be peaceful and reflective
5. Divide the content into approximately 6 segments of 5 minutes each
6. Each segment should have a clear theme or teaching
7. Use simple, accessible language
8. The content should be copyright-safe and original

Format your response as follows:
SEGMENT 1: [Title]
[Content for approximately 5 minutes of narration]

SEGMENT 2: [Title]
[Content for approximately 5 minutes of narration]

... continue for all 6 segments

End with a peaceful closing reflection."""
        
        return prompt
    
    def _structure_script(self, script_content: str, theme: str) -> Dict:
        """Structure the raw script into segments."""
        segments = []
        current_segment = None
        current_content = []
        
        for line in script_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a segment header
            if line.startswith('SEGMENT'):
                if current_segment:
                    # Save previous segment
                    segments.append({
                        'title': current_segment,
                        'content': ' '.join(current_content).strip(),
                        'duration': 300  # 5 minutes per segment
                    })
                    current_content = []
                
                # Extract title
                if ':' in line:
                    current_segment = line.split(':', 1)[1].strip()
                else:
                    current_segment = f"Part {len(segments) + 1}"
            else:
                current_content.append(line)
        
        # Add last segment
        if current_segment and current_content:
            segments.append({
                'title': current_segment,
                'content': ' '.join(current_content).strip(),
                'duration': 300
            })
        
        return {
            'theme': theme or 'divine love and devotion',
            'total_duration': self.duration_minutes * 60,
            'segments': segments,
            'full_script': '\n\n'.join(s['content'] for s in segments)
        }
    
    def get_weekly_themes(self) -> List[str]:
        """Get suggested themes for weekly videos."""
        return [
            "The Divine Love of Radha and Krishna",
            "Krishna's Teachings on Dharma",
            "Radha's Devotion and Surrender",
            "The Flute of Krishna - Call to the Soul",
            "Rasleela - The Divine Dance",
            "Krishna's Childhood - Innocence and Joy",
            "Radha's Separation - Deepening Devotion",
            "Krishna as the Supreme Friend",
            "The Gopis' Love - Pure Devotion",
            "Krishna's Message in the Bhagavad Gita",
            "Radha's Grace and Compassion",
            "The Yamuna River - Sacred Waters"
        ]
