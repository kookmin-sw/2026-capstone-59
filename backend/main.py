import sys

import uvicorn

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "business"
    if target not in ("business", "ai"):
        raise SystemExit("usage: python main.py [business|ai]")
    port = 8001 if target == "ai" else 8000
    uvicorn.run(f"app.{target}.main:app", host="0.0.0.0", port=port, reload=True)
