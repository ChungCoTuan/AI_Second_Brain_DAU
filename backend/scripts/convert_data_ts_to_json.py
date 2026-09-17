"""Convert data.ts to JSON for lazy loading."""
import sys
import re
import json

sys.stdout.reconfigure(encoding="utf-8")

with open("frontend/src/data.ts", "r", encoding="utf-8") as f:
    content = f.read()

# Remove the TypeScript export declaration prefix and trailing semicolon
prefix = "export const DEMO_DATA: any = "
if content.startswith(prefix):
    json_str = content[len(prefix):].strip()
    # Remove trailing semicolon if present
    if json_str.endswith(";"):
        json_str = json_str[:-1].strip()

try:
    data = json.loads(json_str)
    print(f"✅ Parsed successfully. Root keys: {list(data.keys())}")

    # Save to public/data.json for lazy loading
    import os
    os.makedirs("frontend/public", exist_ok=True)
    output_path = "frontend/public/data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=None)  # compact

    size = os.path.getsize(output_path)
    print(f"✅ Saved to {output_path} ({size:,} bytes)")
    print(f"   Structure:")
    for k, v in data.items():
        if isinstance(v, list):
            print(f"     {k}: list[{len(v)}]")
        elif isinstance(v, dict):
            print(f"     {k}: dict[{len(v)} keys]")
        else:
            print(f"     {k}: {type(v).__name__} = {str(v)[:50]}")

except json.JSONDecodeError as e:
    print(f"❌ JSON parse error: {e}")
    # Show the context around the error
    line_no = e.lineno
    lines = json_str.split("\n")
    start = max(0, line_no - 3)
    end = min(len(lines), line_no + 2)
    print(f"Context around line {line_no}:")
    for i, l in enumerate(lines[start:end], start=start+1):
        print(f"  {i}: {l[:100]}")
