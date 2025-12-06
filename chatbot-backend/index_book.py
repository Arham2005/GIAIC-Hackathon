"""
Index book chapters into Qdrant vector database
"""

import os
import sys
import httpx
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

BACKEND_URL = "http://localhost:8000"
DOCS_DIR = Path(__file__).parent.parent / "docs"

def read_chapter(file_path: Path) -> tuple[str, str]:
    """Read chapter content and extract title"""
    content = file_path.read_text(encoding='utf-8')
    
    # Extract title from first heading
    lines = content.split('\n')
    title = "Untitled"
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            break
    
    return title, content

def index_chapters():
    """Index all chapters from docs folder"""
    
    print("🚀 Starting chapter indexing...")
    print(f"📁 Reading from: {DOCS_DIR}")
    
    if not DOCS_DIR.exists():
        print(f"❌ Error: docs directory not found at {DOCS_DIR}")
        return
    
    # Get all markdown files except intro
    chapter_files = sorted([
        f for f in DOCS_DIR.glob("*.md")
        if f.name not in ["intro.md", "README.md"]
        and not f.name.startswith("tutorial-")
    ])
    
    print(f"📚 Found {len(chapter_files)} chapters to index\n")
    
    indexed_count = 0
    failed_count = 0
    
    for chapter_file in chapter_files:
        chapter_id = chapter_file.stem  # filename without extension
        
        try:
            title, content = read_chapter(chapter_file)
            
            # Skip if content is too short (likely error file)
            if len(content) < 200:
                print(f"⏭️  Skipping {chapter_id} (content too short)")
                continue
            
            print(f"📝 Indexing: {chapter_id}")
            print(f"   Title: {title}")
            print(f"   Size: {len(content)} chars")
            
            # Send to backend
            response = httpx.post(
                f"{BACKEND_URL}/index",
                json={
                    "chapter_id": chapter_id,
                    "title": title,
                    "content": content
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully indexed: {chapter_id}\n")
                indexed_count += 1
            else:
                print(f"❌ Failed to index {chapter_id}: {response.text}\n")
                failed_count += 1
        
        except Exception as e:
            print(f"❌ Error indexing {chapter_id}: {e}\n")
            failed_count += 1
    
    print("\n" + "="*60)
    print(f"✨ Indexing complete!")
    print(f"✅ Successfully indexed: {indexed_count} chapters")
    print(f"❌ Failed: {failed_count} chapters")
    print("="*60)

if __name__ == "__main__":
    try:
        index_chapters()
    except Exception as e:
        print(f"❌ Fatal error: {e}")