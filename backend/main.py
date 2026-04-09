import sys

import uvicorn

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "business"
    if target not in ("business", "ai"):
        raise SystemExit("usage: python main.py [business|ai]")
    uvicorn.run(f"app.{target}.main:app", host="0.0.0.0", port=8000, reload=True)
