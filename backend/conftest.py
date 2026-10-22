import sys
from pathlib import Path

# Cho phép `import app...` khi chạy pytest từ thư mục backend/.
sys.path.insert(0, str(Path(__file__).resolve().parent))
