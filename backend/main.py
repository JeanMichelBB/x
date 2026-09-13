from datetime import datetime, timedelta

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base, SessionLocal, create_or_rebuild_database, enforce_tweet_limit, enforce_user_limit, enforce_message_limit
from app.auth import SECRET_KEY, ALGORITHM
from app.auth import router as auth
from jose import JWTError, jwt
from app.user import router as signup
from app.profile import router as profile
from app.messages import router as messages
from app.settings import router as settings
from app.followers import router as followers
from app.tweets import router as tweets
from app.comments import router as comments
from app.gifs import router as gifs
from app.notifications import router as notifications
from app.bookmarks import router as bookmarks
from app.lists import router as lists
from app.seed import seed_data
from app.models import User, Tweet, Message
from sqlalchemy import event
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
event.listen(Tweet, 'after_insert', enforce_tweet_limit)
event.listen(User, 'after_insert', enforce_user_limit)
event.listen(Message, 'after_insert', enforce_message_limit)

app = FastAPI()

PUBLIC_PATHS = ["/docs", "/openapi.json", "/login", "/users", "/signup", "/health", "/api/health", "/gifs", "/metrics"]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok"}


def _tweets_last_hour() -> int:
    db = SessionLocal()
    try:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        return db.query(Tweet).filter(Tweet.date_posted >= one_hour_ago).count()
    except Exception:
        return -1
    finally:
        db.close()


tweets_last_hour = Gauge(
    "x_tweets_created_last_hour",
    "Tweets created in the last hour. A silent posting-path failure drops "
    "this to zero while pods stay healthy -- invisible to infra-level checks.",
)
tweets_last_hour.set_function(_tweets_last_hour)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    allowed_iframe_origin = "https://jeanmichelbb.github.io"

    if request.url.path not in PUBLIC_PATHS:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("sub") is None:
                return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})

    response = await call_next(request)

    # Allow iframe embedding only from your portfolio
    response.headers["X-Frame-Options"] = f"ALLOW-FROM {allowed_iframe_origin}"
    response.headers["Content-Security-Policy"] = f"frame-ancestors {allowed_iframe_origin};"

    return response

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

create_or_rebuild_database()
seed_data()

app.include_router(auth)
app.include_router(signup)
app.include_router(profile)
app.include_router(messages)
app.include_router(settings)
app.include_router(followers)
app.include_router(tweets)
app.include_router(comments)
app.include_router(gifs)
app.include_router(notifications)
app.include_router(bookmarks)
app.include_router(lists)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://x.sacenpapier.org",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)