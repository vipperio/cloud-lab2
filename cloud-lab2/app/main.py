
import os
import json

from contextlib import asynccontextmanager
from functools import lru_cache
from threading import Lock
from time import perf_counter

import redis
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg.conninfo import make_conninfo
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL and os.getenv("DB_HOST"):
    DATABASE_URL = make_conninfo(
        host=os.environ["DB_HOST"],
        port=5432,
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
    )

REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
CACHE_KEY = "notes:all"

NOTES = [
    {"id": 1, "title": "Cloud Computing", "content": "Introduction to cloud"},
    {"id": 2, "title": "Docker", "content": "Containerization"},
    {"id": 3, "title": "AWS", "content": "Cloud infrastructure"},
]

pool = None
cache = None

stats_lock = Lock()
stats = {
    "cache_hits": 0,
    "cache_misses": 0,
    "cache_bypasses": 0,
    "db_queries": 0,
}


def increment(name):
    with stats_lock:
        stats[name] += 1


@asynccontextmanager
async def lifespan(app):
    global pool, cache

    if DATABASE_URL and REDIS_URL:
        pool = ConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=10,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        pool.open(wait=True)

        cache = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
        )
        cache.ping()

        with pool.connection() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(202602)")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)

            count = conn.execute(
                "SELECT COUNT(*) AS count FROM notes"
            ).fetchone()["count"]

            if count == 0:
                with conn.cursor() as cur:
                    cur.executemany(
                        """
                        INSERT INTO notes (title, content)
                        VALUES (%s, %s)
                        """,
                        [
                            (item["title"], item["content"])
                            for item in NOTES
                        ],
                    )


    try:
        yield
    finally:
        if cache is not None:
            cache.close()
        if pool is not None:
            pool.close()


app = FastAPI(
    title="Cloud Lab 2 API",
    version="3.0.0",
    lifespan=lifespan,
)


class NoteCreate(BaseModel):
    title: str
    content: str


@app.get("/")
def home():
    return {"message": "Cloud Lab 2 API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


def require_database():
    if pool is None or cache is None:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL and Redis are not configured",
        )


def read_notes_from_db():
    increment("db_queries")

    with pool.connection() as conn:
        return conn.execute(
            "SELECT id, title, content FROM notes ORDER BY id"
        ).fetchall()


@app.get("/notes")
def notes(use_cache: bool = True):

    # Compatibility with the previous AWS configuration.
    if pool is None:
        return NOTES

    if not use_cache:
        increment("cache_bypasses")
        return read_notes_from_db()

    # Step 1: Check Redis.
    cached_data = cache.get(CACHE_KEY)

    if cached_data is not None:
        increment("cache_hits")
        return json.loads(cached_data)

    # Step 2: Cache miss. Read PostgreSQL.
    increment("cache_misses")
    result = read_notes_from_db()

    # Step 3: Store result in Redis for 60 seconds.
    cache.setex(
        CACHE_KEY,
        CACHE_TTL,
        json.dumps(result),
    )

    return result


@app.get("/notes/{note_id}")
def note(note_id: int):
    if pool is None:
        for item in NOTES:
            if item["id"] == note_id:
                return item
    else:
        with pool.connection() as conn:
            item = conn.execute(
                "SELECT * FROM notes WHERE id = %s",
                (note_id,),
            ).fetchone()

        if item is not None:
            return item

    raise HTTPException(
        status_code=404,
        detail="Note not found",
    )


@app.post("/notes", status_code=201)
def create_note(data: NoteCreate):
    require_database()

    with pool.connection() as conn:
        result = conn.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (%s, %s)
            RETURNING id, title, content
            """,
            (data.title, data.content),
        ).fetchone()

    # Invalidate the list cache after committing.
    cache.delete(CACHE_KEY)

    return result


@app.get("/redis/stats")
def redis_stats():
    require_database()

    with stats_lock:
        result = stats.copy()

    total = (
        result["cache_hits"]
        + result["cache_misses"]
    )

    result["hit_rate_percent"] = round(
        result["cache_hits"] / total * 100,
        2,
    ) if total else 0

    result["cache_ttl_seconds"] = CACHE_TTL
    result["remaining_ttl_seconds"] = cache.ttl(CACHE_KEY)

    return result


@app.post("/redis/reset")
def reset_redis():
    require_database()

    cache.delete(CACHE_KEY)

    with stats_lock:
        for key in stats:
            stats[key] = 0

    return {"status": "reset"}


# Previous CPU workload from Lab 2.
def expensive_calculation(iterations: int) -> int:
    total = 0

    for i in range(iterations):
        total += (i * i) % 7919

    return total


@lru_cache(maxsize=128)
def cached_calculation(iterations: int) -> int:
    return expensive_calculation(iterations)


@app.get("/compute")
def compute(
    iterations: int = Query(
        default=1000000,
        ge=1000,
        le=3000000,
    ),
    use_cache: bool = True,
):
    started = perf_counter()

    value = (
        cached_calculation(iterations)
        if use_cache
        else expensive_calculation(iterations)
    )

    return {
        "iterations": iterations,
        "use_cache": use_cache,
        "result": value,
        "compute_ms": round(
            (perf_counter() - started) * 1000, 3
        ),
    }


@app.get("/cache/stats")
def cache_stats():
    info = cached_calculation.cache_info()

    return {
        "hits": info.hits,
        "misses": info.misses,
        "maxsize": info.maxsize,
        "currsize": info.currsize,
    }
