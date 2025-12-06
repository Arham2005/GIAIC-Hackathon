"""
Fill empty chapters with AI-generated content using Gemini
"""

import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Chapters that need content
EMPTY_CHAPTERS = {
    "03-sensors-and-actuators": "Sensors and Actuators",
    "05-control-systems": "Control Systems",
    "06-perception-and-vision": "Perception and Vision",
    "08-reinforcement-learning": "Reinforcement Learning",
    "09-neural-networks-for-control": "Neural Networks for Control",
    "11-manipulation-and-grasping": "Manipulation and Grasping",
    "12-human-robot-interaction": "Human-Robot Interaction",
    "13-sim-to-real-transfer": "Sim-to-Real Transfer",
    "14-safety-and-ethics": "Safety and Ethics",
    "15-future-of-physical-ai": "Future of Physical AI"
}

def generate_chapter(chapter_id: str, title: str) -> str:
    """Generate comprehensive chapter content"""
    
    prompt = f"""Write a comprehensive technical textbook chapter on "{title}" for a Physical AI & Humanoid Robotics course.

The chapter should be 2000-2500 words and include:

1. **Introduction & Overview** (2-3 paragraphs)
2. **Core Concepts** (4-5 major sections with subsections)
3. **Technical Details** (equations, algorithms, or code examples where relevant)
4. **Real-World Applications** (2-3 practical examples)
5. **Key Takeaways** (bullet points summary)
6. **Further Reading** (3-4 resources)

Use markdown formatting with proper headers (##, ###), code blocks, bullet points, and emphasis.
Make it educational, practical, and engaging for students.
Focus on clarity and technical accuracy."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating {title}: {e}")
        return f"# {title}\n\n*Content generation failed. Please try again.*"

def main():
    docs_dir = Path("docs")
    
    print("📚 Filling Empty Chapters with AI Content")
    print("=" * 60)
    
    for chapter_id, title in EMPTY_CHAPTERS.items():
        filepath = docs_dir / f"{chapter_id}.md"
        
        # Check if file is empty or too short
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            if len(content) > 500:
                print(f"⏭️  Skipping {chapter_id} (already has content)")
                continue
        
        print(f"\n📝 Generating: {title}")
        print(f"   File: {chapter_id}.md")
        
        # Generate content
        content = generate_chapter(chapter_id, title)
        
        # Save to file
        filepath.write_text(content, encoding='utf-8')
        
        print(f"✅ Saved: {len(content)} characters")
    
    print("\n" + "=" * 60)
    print("✨ All chapters filled!")
    print("Run: npm start to see the updated book")

if __name__ == "__main__":
    main()