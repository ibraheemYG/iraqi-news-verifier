from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
import threading
import asyncio

# Import the new simplified modules
from telegram_reader import get_telegram_messages
from rag_arabert import generate_response
from vector_store import init_vector_store, upsert_articles, search
from news_fetchers import fetch_all_external
from urllib.parse import urlparse


# --- Lifespan Management for DB Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting up...")
    # Initialize AraBERT-based vector store (SQLite persistence)
    init_vector_store()
    print("Vector store initialized (AraBERT embeddings).")
    yield
    print("Server shutting down.")

# --- API Setup ---
app = FastAPI(
    title="Iraqi News Verifier API (Telegram Edition)",
    description="An API to verify news claims against a trusted knowledge base from Telegram channels.",
    version="3.0.0", # Major version bump for Telegram integration
    lifespan=lifespan
)

class QueryRequest(BaseModel):
    query_text: str

# --- API Endpoints ---

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/verify")
async def verify_news(request: QueryRequest):
    """Receives a news query, verifies it, and returns the verdict with an explanation."""
    query = request.query_text
    if not query:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    print(f"\nReceived query for verification: '{query}'")
    
    # --- Early filtering for short, casual messages ---
    word_count = len(query.strip().split())
    casual_keywords = ["مرحبا", "مرحباً", "اهلا", "أهلا", "هلا", "السلام", "صباح", "مساء", "شكرا", "شكراً", "تحية"]
    
    if word_count <= 4 and any(keyword in query for keyword in casual_keywords):
        # Return a simple, direct response without searching the database
        print("Short casual message detected. Skipping AraBERT search.")
        casual_response = "مرحباً! هذا النظام مخصص للتحقق من الأخبار والإجابة على أسئلة حول الأحداث في العراق. الرجاء إدخال خبر أو سؤال للتحقق منه."
        return {"verdict": casual_response, "source": None, "status": "casual"}
    
    # --- Normal verification flow ---
    contexts, is_relevant, best_sim = search(query, top_k=8)

    print(f"Top contexts found: {[ (c.get('title'), c.get('similarity')) for c in contexts[:3] ]}")
    
    # Generate a response whether context was found or not
    print("Generating response from LLM...")
    verdict, is_question = generate_response(user_query=query, retrieved_context=contexts, is_relevant=is_relevant)

    # Determine status based on verdict content with strict rules
    status = "unverified"  # Default
    
    print(f"Verdict from LLM: {verdict[:150]}...")  # Log first 150 chars
    print(f"is_relevant: {is_relevant}, is_question: {is_question}, best_sim: {best_sim:.3f}")
    
    # --- Status Determination Logic ---
    if is_question:
        # For questions, the concept of verification doesn't apply.
        status = "answered"
        print("✓ Status path: ANSWERED (detected question)")
    elif is_relevant:
        # High-confidence copy/paste: auto-verify
        if best_sim >= 0.85:
            status = "verified"
            print(f"✓ Status path: VERIFIED (copy/near-duplicate best_sim={best_sim:.3f})")
        # Strong similarity: verify unless LLM explicitly rejects
        elif best_sim >= 0.65:
            rejection_markers = ["⚠️", "غير مؤكد", "لا يمكن التأكد", "لم أجد", "لا يوجد"]
            explicit_reject = any(mark in verdict[:120] for mark in rejection_markers)
            if not explicit_reject:
                status = "verified"
                print(f"✓ Status path: VERIFIED (strong sim {best_sim:.3f}, no explicit rejection)")
            else:
                status = "unverified"
                print(f"✗ Status path: UNVERIFIED (LLM explicit rejection with strong sim {best_sim:.3f})")
        # Medium similarity: require positive LLM signal
        elif best_sim >= 0.50:
            positive = ("✅" in verdict) or ("موثوق" in verdict and "غير" not in verdict[:70])
            if positive:
                status = "verified"
                print(f"✓ Status path: VERIFIED (medium sim {best_sim:.3f} + positive LLM)")
            else:
                status = "unverified"
                print(f"✗ Status path: UNVERIFIED (medium sim {best_sim:.3f} but no positive LLM)")
        else:
            status = "unverified"
            print(f"✗ Status path: UNVERIFIED (low sim {best_sim:.3f})")
    else:
        status = "unverified"
        print("✗ Status path: UNVERIFIED (no relevant context)")

    print(f"==> Final status: {status.upper()}")
    
    source_info = None
    if status in ("verified", "answered") and contexts:
        # Build a human-friendly source label
        url = contexts[0].get("url", "")

        def humanize_source(u: str) -> str:
            if not u:
                return "مصدر خارجي"
            if "t.me" in u:
                parts = u.split("/")
                # Expect: https://t.me/<username>/<id> or https://t.me/c/<id>/<post>
                if len(parts) > 3 and parts[3] and parts[3] != "c":
                    return f"قناة @{parts[3]}"
                return "قناة تليجرام"
            domain = urlparse(u).netloc.lower().replace("www.", "")
            mapping = {
                "moe.gov.iq": "موقع وزارة التربية",
                "moedu.gov.iq": "موقع وزارة التربية",
                "mohesr.gov.iq": "موقع وزارة التعليم العالي",
                "moi.gov.iq": "موقع وزارة الداخلية",
                "mod.mil.iq": "موقع وزارة الدفاع",
                "oil.gov.iq": "موقع وزارة النفط",
                "pmo.iq": "موقع رئاسة الوزراء",
                "facebook.com": "فيسبوك",
                "x.com": "تويتر",
                "twitter.com": "تويتر",
                "instagram.com": "إنستغرام",
                "youtube.com": "يوتيوب",
            }
            for key, label in mapping.items():
                if key in domain:
                    return label
            return f"موقع {domain}" if domain else "مصدر خارجي"

        source_label = humanize_source(url)
        source_info = {"url": url, "label": source_label}

    # --- Normalize verdict text to avoid contradictions with status ---
    def normalize_verdict(status_val: str, raw_text: str) -> str:
        try:
            negative_markers = [
                "لا توجد معلومات",
                "لا تتضمن النصوص",
                "لا يمكن التأكد",
                "لم أجد",
                "لا يوجد",
                "غير مؤكد",
            ]
            if status_val == "verified":
                # Compose a deterministic, concise confirmation
                src_label = source_info.get("label") if source_info else "المصادر"
                src_url = source_info.get("url") if source_info else ""
                line1 = "✅ الخبر موثوق"
                line2 = f"تم التحقق من الخبر بمقارنته مع المحتوى الموجود في قاعدة البيانات من {src_label}، باستخدام تقنية الاسترجاع المعزز بالذكاء الاصطناعي (RAG)."
                line3 = f"المصدر: {src_url}" if src_url else ""
                return "\n".join([l for l in [line1, line2, line3] if l])
            elif status_val == "unverified":
                # Ensure header exists and keep the LLM explanation
                header = "⚠️ الخبر غير مؤكد"
                body = raw_text or ""
                if not (body.strip().startswith("⚠️") or "الخبر غير مؤكد" in body[:40]):
                    body = header + "\n" + body
                return body.strip()
            else:
                # answered/casual -> keep as is
                return raw_text
        except Exception:
            return raw_text

    final_verdict = normalize_verdict(status, verdict)
    
    # The LLM now provides the full response text
    return {"verdict": final_verdict, "source": source_info, "status": status}

def run_telegram_and_populate():
    """
    A synchronous wrapper that runs the async get_telegram_messages function
    and then populates the database.
    """
    print("\n--- Starting background Telegram fetch and population process ---")
    
    try:
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the async function and get the results - per user request fetch 50 per channel
        articles = loop.run_until_complete(get_telegram_messages(limit_per_channel=10))

        if not articles:
            print("Telegram fetch process finished, but no articles were found.")
            return

        print(f"Total articles fetched from Telegram: {len(articles)}")
        upsert_articles(articles)
        print("--- Background Telegram fetch and population process finished ---")

    except Exception as e:
        print(f"An error occurred during the Telegram process: {e}")
    finally:
        # Clean up the event loop
        if 'loop' in locals():
            loop.close()


@app.post("/populate-from-telegram")
async def populate_from_telegram_endpoint():
    """
    Triggers a background task to fetch messages from Telegram and populate the database.
    """
    print("Received request to populate from Telegram. Starting in background.")
    # Run the synchronous wrapper in a separate thread
    thread = threading.Thread(target=run_telegram_and_populate)
    thread.start()
    
    return {"message": "Telegram fetch and population process started in the background. This may take several minutes. Please check the terminal for login prompts if this is the first run."}


def run_external_news_and_populate():
    print("\n--- Starting background External News fetch and population process ---")
    try:
        articles = fetch_all_external(limit_each=50)
        if not articles:
            print("External news fetch finished, but no articles were found.")
            return
        print(f"Total external articles fetched: {len(articles)}")
        upsert_articles(articles)
        print("--- Background External News fetch and population process finished ---")
    except Exception as e:
        print(f"An error occurred during external news process: {e}")


@app.post("/populate-from-news")
async def populate_from_news_endpoint():
    print("Received request to populate from external news. Starting in background.")
    thread = threading.Thread(target=run_external_news_and_populate)
    thread.start()
    return {"message": "External news fetch and population process started in the background."}

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting FastAPI server (Telegram Edition)...")
    print("Access the API docs at http://127.0.0.1:8001/docs")
    # Start without auto-reload to avoid extra reloader processes during normal runs
    uvicorn.run("api:app", host="127.0.0.1", port=8001)
