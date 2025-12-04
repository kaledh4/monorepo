import os
import json
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from app.data_fetcher import get_all_data
from app.analyzer import generate_insight
from dotenv import load_dotenv

# Load env vars (for local testing)
load_dotenv()

def build_site():
    print("🚀 Starting Daily Build...")
    
    # 1. Fetch Data
    print("📊 Fetching Market Data...")
    try:
        raw_data = get_all_data()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return

    # 2. Generate AI Insight
    print("🧠 Generating AI Insight...")
    try:
        insight_html = generate_insight(raw_data)
    except Exception as e:
        print(f"❌ Error generating insight: {e}")
        insight_html = "<p>Error generating insight.</p>"

    # 3. Prepare Output Directory
    output_dir = "public"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    os.makedirs(f"{output_dir}/static")

    # 4. Copy Static Assets
    print("🎨 Copying Static Assets...")
    if os.path.exists("app/static"):
        shutil.copytree("app/static", f"{output_dir}/static", dirs_exist_ok=True)

    # 5. Render HTML
    print("📝 Rendering HTML...")
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("index.html")
    
    # Prepare context for Jinja
    current_time = datetime.now()
    context = {
        "insight": {
            "html": insight_html,
            "raw_data": raw_data,
            "date": current_time.strftime("%Y-%m-%d"),
            "timestamp": current_time.isoformat()
        },
        "generated_at": current_time.strftime("%A, %B %d, %Y at %I:%M %p")
    }
    
    html_content = template.render(context)
    
    with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ Build Complete! Output in /public")

if __name__ == "__main__":
    build_site()