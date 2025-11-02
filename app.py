import streamlit as st
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import RAG modules directly
from rag_pipeline import RAGPipeline

# --- Page Configuration ---
st.set_page_config(
    page_title="Iraqi News Verifier | مُتحقق الأخبار العراقي",
    page_icon="🔎",
    layout="wide"
)

# --- Initialize RAG Pipeline ---
@st.cache_resource
def get_rag_pipeline():
    """Initialize RAG pipeline once and cache it"""
    return RAGPipeline()

rag = get_rag_pipeline()

# --- Sidebar ---
with st.sidebar:
    st.title("Admin Panel")
    st.info("تحديث قاعدة البيانات من تيليجرام والمصادر الإخبارية.")
    
    if st.button("جلب من تليجرام"):
        with st.spinner("جاري جلب الأخبار من تيليجرام..."):
            try:
                import asyncio
                from telegram_reader import get_telegram_messages
                from vector_store import upsert_articles
                
                # Run async function
                articles = asyncio.run(get_telegram_messages(limit_per_channel=10))
                
                if articles:
                    # Store in vector database
                    upsert_articles(articles)
                    st.success(f"✅ تم جلب وحفظ {len(articles)} خبر من تليجرام")
                else:
                    st.warning("⚠️ لم يتم العثور على أخبار جديدة")
            except Exception as e:
                st.error(f"❌ خطأ في الجلب: {e}")

    if st.button("جلب من NewsAPI/NewsData"):
        with st.spinner("جاري جلب الأخبار من المصادر..."):
            try:
                from news_fetchers import fetch_all_external
                from vector_store import upsert_articles
                
                articles = fetch_all_external(limit_each=50)
                
                if articles:
                    upsert_articles(articles)
                    st.success(f"✅ تم جلب وحفظ {len(articles)} خبر من المصادر")
                else:
                    st.warning("⚠️ لم يتم العثور على أخبار جديدة")
            except Exception as e:
                st.error(f"❌ خطأ في الجلب: {e}")

    st.markdown("---")
    
    # Status Check
    try:
        # Check if RAG is loaded
        if rag:
            st.success("✅ النظام جاهز")
        else:
            st.error("❌ خطأ في تحميل النظام")
    except:
        st.error("❌ خطأ في النظام")
        
    st.markdown("---")
    st.markdown("Powered by RAG (AraBERT + Gemini), and Telethon.")

# --- Main Page ---
st.title("🔎 مُتحقق الأخبار العراقي")
st.warning("⚠️ **ملاحظة:** هذا المشروع هو جزء من بحث ماجستير وقد لا تكون النتائج دقيقة دائمًا. يُستخدم لأغراض البحث والتجربة.")

# Input Area
with st.container(border=True):
    query_text = st.text_area(
        "ادخل النص هنا:",
        height=150,
        placeholder="مثال: البنك المركزي العراقي يطلق عملة رقمية جديدة..."
    )
    
    verify_button = st.button("تحقق الآن (Verify Now)", type="primary")

# Verification Logic
if verify_button:
    if not query_text.strip():
        st.warning("الرجاء إدخال نص للتحقق منه.")
    else:
        with st.spinner("...جاري التحقق من الخبر"):
            try:
                # Call RAG pipeline directly (no API needed)
                result = rag.verify_news(query_text)
                
                verdict = result.get("verdict", "")
                source_info = result.get("source")
                status = result.get("status", "unverified")

                # Display results in a new container
                with st.container(border=True):
                    # Use the status field returned from RAG
                    if status == "verified":
                        st.success("#### ✅ الخبر موثوق")
                        if isinstance(source_info, dict) and source_info.get("url"):
                            label = source_info.get("label", "المصدر")
                            url = source_info.get("url")
                            st.markdown(f"**المصدر:** [{label}]({url})")
                    elif status == "answered":
                        st.info("#### 📖 إجابة السؤال")
                        if isinstance(source_info, dict) and source_info.get("url"):
                            label = source_info.get("label", "المصدر")
                            url = source_info.get("url")
                            st.markdown(f"**المصدر الأقرب:** [{label}]({url})")
                    elif status == "casual":
                        st.info("#### 💬 رسالة عابرة")
                    else:
                        st.error("#### ⚠️ الخبر غير مؤكد")
                    
                    # Show details directly, but remove the first line if it contains emoji
                    st.markdown("---")
                    # Remove the redundant first line with emoji from verdict for cleaner UI
                    verdict_lines = verdict.split('\n')
                    if verdict_lines and ('✅' in verdict_lines[0] or '⚠️' in verdict_lines[0] or '📖' in verdict_lines[0]):
                        verdict_clean = '\n'.join(verdict_lines[1:]).strip()
                    else:
                        verdict_clean = verdict
                    
                    if verdict_clean:
                        st.write(verdict_clean)

            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
