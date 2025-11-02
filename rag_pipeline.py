"""
RAG Pipeline - Simplified wrapper for Streamlit integration
Combines vector store, RAG generation, and verification logic
"""
from telegram_reader import get_telegram_messages
from rag_arabert import generate_response
from vector_store import init_vector_store, upsert_articles, search
from news_fetchers import fetch_all_external
from urllib.parse import urlparse
import asyncio


class RAGPipeline:
    """Main RAG Pipeline for news verification"""
    
    def __init__(self):
        """Initialize the RAG pipeline"""
        print("Initializing RAG Pipeline...")
        init_vector_store()
        print("✓ Vector store initialized (AraBERT embeddings)")
    
    def verify_news(self, query_text: str) -> dict:
        """
        Verify a news query against the knowledge base
        
        Args:
            query_text: The news text or question to verify
            
        Returns:
            dict with keys: verdict, source, status
        """
        if not query_text or not query_text.strip():
            return {
                "verdict": "الرجاء إدخال نص للتحقق منه.",
                "source": None,
                "status": "unverified"
            }
        
        query = query_text.strip()
        print(f"\n[RAG] Verifying: '{query[:100]}...'")
        
        # --- Early filtering for casual messages ---
        word_count = len(query.split())
        casual_keywords = ["مرحبا", "مرحباً", "اهلا", "أهلا", "هلا", "السلام", "صباح", "مساء", "شكرا", "شكراً", "تحية"]
        
        if word_count <= 4 and any(keyword in query for keyword in casual_keywords):
            print("[RAG] Short casual message detected")
            casual_response = "مرحباً! هذا النظام مخصص للتحقق من الأخبار والإجابة على أسئلة حول الأحداث في العراق. الرجاء إدخال خبر أو سؤال للتحقق منه."
            return {"verdict": casual_response, "source": None, "status": "casual"}
        
        # --- Search vector store ---
        contexts, is_relevant, best_sim = search(query, top_k=8)
        print(f"[RAG] Best similarity: {best_sim:.3f}, Relevant: {is_relevant}")
        
        # --- Generate LLM response ---
        print("[RAG] Generating response...")
        verdict, is_question = generate_response(
            user_query=query,
            retrieved_context=contexts,
            is_relevant=is_relevant
        )
        
        # --- Determine status ---
        status = "unverified"  # Default
        
        if is_question:
            status = "answered"
            print(f"[RAG] Status: ANSWERED")
        elif is_relevant:
            # High-confidence: auto-verify
            if best_sim >= 0.85:
                status = "verified"
                print(f"[RAG] Status: VERIFIED (high sim {best_sim:.3f})")
            # Strong similarity: verify unless LLM rejects
            elif best_sim >= 0.65:
                rejection_markers = ["⚠️", "غير مؤكد", "لا يمكن التأكد", "لم أجد", "لا يوجد"]
                explicit_reject = any(mark in verdict[:120] for mark in rejection_markers)
                if not explicit_reject:
                    status = "verified"
                    print(f"[RAG] Status: VERIFIED (strong sim {best_sim:.3f})")
                else:
                    status = "unverified"
                    print(f"[RAG] Status: UNVERIFIED (explicit rejection)")
            # Medium similarity: require positive signal
            elif best_sim >= 0.50:
                positive = ("✅" in verdict) or ("موثوق" in verdict and "غير" not in verdict[:70])
                if positive:
                    status = "verified"
                    print(f"[RAG] Status: VERIFIED (medium sim + positive LLM)")
                else:
                    status = "unverified"
                    print(f"[RAG] Status: UNVERIFIED (medium sim, no positive)")
            else:
                status = "unverified"
                print(f"[RAG] Status: UNVERIFIED (low sim {best_sim:.3f})")
        else:
            status = "unverified"
            print("[RAG] Status: UNVERIFIED (no relevant context)")
        
        # --- Build source info ---
        source_info = None
        if status in ("verified", "answered") and contexts:
            url = contexts[0].get("url", "")
            source_label = self._humanize_source(url)
            source_info = {"url": url, "label": source_label}
        
        # --- Normalize verdict ---
        final_verdict = self._normalize_verdict(status, verdict, source_info)
        
        return {
            "verdict": final_verdict,
            "source": source_info,
            "status": status
        }
    
    def _humanize_source(self, url: str) -> str:
        """Convert URL to human-readable source label"""
        if not url:
            return "مصدر خارجي"
        
        if "t.me" in url:
            parts = url.split("/")
            if len(parts) > 3 and parts[3] and parts[3] != "c":
                return f"قناة @{parts[3]}"
            return "قناة تليجرام"
        
        domain = urlparse(url).netloc.lower().replace("www.", "")
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
    
    def _normalize_verdict(self, status: str, raw_text: str, source_info: dict) -> str:
        """Normalize verdict text to match status"""
        try:
            if status == "verified":
                src_label = source_info.get("label") if source_info else "المصادر"
                src_url = source_info.get("url") if source_info else ""
                
                line1 = "✅ الخبر موثوق"
                line2 = f"تم التحقق من الخبر بمقارنته مع المحتوى الموجود في قاعدة البيانات من {src_label}، باستخدام تقنية الاسترجاع المعزز بالذكاء الاصطناعي (RAG)."
                line3 = f"المصدر: {src_url}" if src_url else ""
                
                return "\n".join([l for l in [line1, line2, line3] if l])
            
            elif status == "unverified":
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


# For direct testing
if __name__ == "__main__":
    rag = RAGPipeline()
    
    # Test verification
    test_query = "السوداني: الحكومة ورثت 131 تريليون"
    result = rag.verify_news(test_query)
    
    print("\n=== Test Result ===")
    print(f"Status: {result['status']}")
    print(f"Verdict: {result['verdict'][:200]}...")
    if result['source']:
        print(f"Source: {result['source']}")
