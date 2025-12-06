"""
Physical AI & Humanoid Robotics Book Generator
Uses Gemini API to generate chapters for Docusaurus
"""

import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Book structure for Physical AI & Humanoid Robotics
BOOK_STRUCTURE = {
    "Part 1: Foundations": [
        "01-introduction-to-physical-ai",
        "02-robotics-fundamentals",
        "03-sensors-and-actuators",
    ],
    "Part 2: Core Concepts": [
        "04-kinematics-and-dynamics",
        "05-control-systems",
        "06-perception-and-vision",
    ],
    "Part 3: AI Integration": [
        "07-machine-learning-for-robotics",
        "08-reinforcement-learning",
        "09-neural-networks-for-control",
    ],
    "Part 4: Humanoid Robotics": [
        "10-bipedal-locomotion",
        "11-manipulation-and-grasping",
        "12-human-robot-interaction",
    ],
    "Part 5: Advanced Topics": [
        "13-sim-to-real-transfer",
        "14-safety-and-ethics",
        "15-future-of-physical-ai",
    ]
}

def generate_chapter(chapter_id: str, chapter_title: str, part: str) -> str:
    """Generate chapter content using Gemini API"""
    
    prompt = f"""You are writing a technical textbook chapter for a course on Physical AI & Humanoid Robotics.

Part: {part}
Chapter: {chapter_title}

Write a comprehensive chapter (1500-2000 words) that includes:
1. **Introduction** - Overview and learning objectives
2. **Core Concepts** - Main technical content with clear explanations
3. **Examples** - Practical examples and use cases
4. **Key Takeaways** - Summary points
5. **Further Reading** - 3-4 recommended resources

Use markdown format with:
- Clear headings (##, ###)
- Code examples where relevant (Python/C++)
- Diagrams descriptions in text
- Mathematical equations in LaTeX format ($...$)

Focus on practical understanding for students learning Physical AI and Robotics.
Make it engaging and educational."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating chapter {chapter_id}: {e}")
        return f"# {chapter_title}\n\nError generating content. Please try again."

def create_sidebar_config():
    """Generate Docusaurus sidebar configuration"""
    
    sidebar_items = []
    
    for part, chapters in BOOK_STRUCTURE.items():
        part_item = {
            "type": "category",
            "label": part,
            "items": chapters
        }
        sidebar_items.append(part_item)
    
    return {
        "tutorialSidebar": [
            {
                "type": "doc",
                "id": "intro",
                "label": "Introduction"
            },
            {
                "type": "category",
                "label": "Physical AI & Humanoid Robotics",
                "items": sidebar_items
            }
        ]
    }

def generate_intro_page():
    """Generate introduction page"""
    
    prompt = """Write an engaging introduction page for a textbook on Physical AI & Humanoid Robotics.

Include:
1. Course overview and objectives
2. Who this book is for
3. What you'll learn
4. Prerequisites
5. How to use this book

Make it motivating and clear. Use markdown format."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "# Introduction\n\nWelcome to Physical AI & Humanoid Robotics!"

def main():
    """Main generation function"""
    
    print("🤖 Physical AI & Humanoid Robotics Book Generator")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Set it with: setx GEMINI_API_KEY \"your-key-here\"")
        return
    
    # Create docs directory
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Generate intro page
    print("\n📝 Generating introduction...")
    intro_content = generate_intro_page()
    (docs_dir / "intro.md").write_text(intro_content, encoding='utf-8')
    print("✅ Introduction complete")
    
    # Generate chapters
    chapter_count = 1
    total_chapters = sum(len(chapters) for chapters in BOOK_STRUCTURE.values())
    
    for part, chapters in BOOK_STRUCTURE.items():
        print(f"\n📚 {part}")
        
        for chapter_id in chapters:
            chapter_title = chapter_id.replace('-', ' ').title()
            print(f"  [{chapter_count}/{total_chapters}] Generating: {chapter_title}...")
            
            content = generate_chapter(chapter_id, chapter_title, part)
            
            # Save to file
            chapter_file = docs_dir / f"{chapter_id}.md"
            chapter_file.write_text(content, encoding='utf-8')
            
            print(f"  ✅ Saved: {chapter_file}")
            chapter_count += 1
    
    # Generate sidebar config
    print("\n📋 Generating sidebar configuration...")
    sidebar_config = create_sidebar_config()
    sidebar_file = Path("sidebars.js")
    
    sidebar_content = f"""module.exports = {json.dumps(sidebar_config, indent=2)};"""
    sidebar_file.write_text(sidebar_content, encoding='utf-8')
    print("✅ Sidebar configuration complete")
    
    print("\n" + "=" * 60)
    print("✨ Book generation complete!")
    print(f"📁 Generated {total_chapters} chapters in: {docs_dir.absolute()}")
    print("\n🚀 Next steps:")
    print("1. Run: npm start")
    print("2. Review generated content")
    print("3. Deploy: git add . && git commit -m 'Add book content' && git push")
    print("=" * 60)

if __name__ == "__main__":
    main()