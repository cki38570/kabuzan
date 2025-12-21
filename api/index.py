from webapp.main import app

# Vercel serverless function entry point
# It expects a variable named 'app' or similar WSGI/ASGI handler
# Since FastAPI is ASGI, Vercel python runtime handles it if we export it.
