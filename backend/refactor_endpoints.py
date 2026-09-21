import re
import os

base_dir = "e:/AI_Second_Brain_DAU/backend/app/api"
routers_dir = os.path.join(base_dir, "routers")
os.makedirs(routers_dir, exist_ok=True)

with open(os.path.join(base_dir, "endpoints.py"), "r", encoding="utf-8") as f:
    content = f.read()

# Extract header (everything before first @router)
header_match = re.search(r'(.*?)(?=@router\.)', content, flags=re.DOTALL)
header = header_match.group(1) if header_match else ""

# Ensure common imports in header
if "from fastapi import APIRouter" not in header:
    header = "from fastapi import APIRouter, Depends, HTTPException, UploadFile, File\n" + header

# Find all endpoints
endpoints = re.findall(r'(@router\.[a-z]+\("([^"]+)"\).*?(?=@router\.[a-z]+\("|\Z))', content, flags=re.DOTALL)

routers_map = {
    "documents": [],
    "review": [],
    "system": [],
    "analytics": [],
    "chat": [],
    "audit": [],
    "search": []
}

for full_match, path in endpoints:
    if path.startswith("/extract") or path.startswith("/upload") or path.startswith("/documents") or path == "/legal-data" or path.startswith("/document/"):
        routers_map["documents"].append(full_match)
    elif path.startswith("/topics"):
        routers_map["documents"].append(full_match) # Group topics into documents for simplicity
    elif path.startswith("/review") or path.startswith("/pending"):
        routers_map["review"].append(full_match)
    elif path.startswith("/system"):
        routers_map["system"].append(full_match)
    elif path.startswith("/analytics") or path.startswith("/document-impact"):
        routers_map["analytics"].append(full_match)
    elif path.startswith("/chat"):
        routers_map["chat"].append(full_match)
    elif path.startswith("/audit"):
        routers_map["audit"].append(full_match)
    elif path.startswith("/search"):
        routers_map["search"].append(full_match)
    else:
        routers_map["documents"].append(full_match)

# Write each router
for router_name, router_endpoints in routers_map.items():
    if not router_endpoints:
        continue
    
    file_path = os.path.join(routers_dir, f"{router_name}.py")
    
    with open(file_path, "w", encoding="utf-8") as f:
        # Write imports
        f.write("from fastapi import APIRouter, Depends, HTTPException, UploadFile, File\n")
        f.write("from pydantic import BaseModel\n")
        f.write("from typing import Dict, Any, List, Optional\n")
        f.write("from sqlalchemy.orm import Session\n")
        f.write("import os\n")
        f.write("import random\n")
        f.write("from ...db.session import get_db\n")
        f.write("from ...db.models import Document, Obligation, Threshold, DocumentRelation, AuditTrail\n")
        f.write("from ...services.nlp_pipeline import generate_rag_answer, extractor, classify_text\n")
        f.write("from ...services.pdf_parser import extract_text_from_pdf, chunk_document\n")
        f.write("from ...services.ingestion.crawl_documents import crawl_chinhphu, get_sync_status, BASE_OUTPUT_DIR\n")
        
        # Add local models that were in endpoints.py if needed
        # We will extract Pydantic models from the header
        models = re.findall(r'(class\s+[a-zA-Z0-9_]+\s*\(BaseModel\):.*?)(?=class|@router|\Z)', header, flags=re.DOTALL)
        for model in models:
            f.write("\n" + model.strip() + "\n")
            
        f.write("\nrouter = APIRouter()\n\n")
        
        for ep in router_endpoints:
            # Reconstruct the endpoints using the new router name if needed, but it's already @router.
            f.write(ep + "\n")

# Recreate endpoints.py
main_endpoints_content = """from fastapi import APIRouter
from .routers import documents, review, system, analytics, chat, audit, search

router = APIRouter()

router.include_router(documents.router, tags=["Documents"])
router.include_router(review.router, tags=["Review"])
router.include_router(system.router, tags=["System"])
router.include_router(analytics.router, tags=["Analytics"])
router.include_router(chat.router, tags=["Chat"])
router.include_router(audit.router, tags=["Audit"])
router.include_router(search.router, tags=["Search"])
"""

with open(os.path.join(base_dir, "endpoints.py"), "w", encoding="utf-8") as f:
    f.write(main_endpoints_content)

print("Refactoring complete.")
