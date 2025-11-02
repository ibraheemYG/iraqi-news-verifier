import streamlit as st
import requests
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Iraqi News Verifier | مُتحقق الأخبار العراقي",
    page_icon="🔎",
    layout="wide"
)

# --- API Configuration ---
API_URL = "http://127.0.0.1:8001/verify"
POPULATE_TG_URL = "http://127.0.0.1:8001/populate-from-telegram"
POPULATE_NEWS_URL = "http://127.0.0.1:8001/populate-from-news"

# --- Sidebar ---
with st.sidebar:
    st.title("Admin Panel")
    st.info("تحديث قاعدة البيانات من تيليجرام والمصادر الإخبارية.")
    
    if st.button("جلب من تليجرام"):
        with st.spinner("يتم بدء عملية الجلب بالخلفية..."):
            try:
                r = requests.post(POPULATE_TG_URL)
                if r.status_code == 200:
                    st.success(r.json().get("message", "تم البدء بالخلفية"))
                else:
                    st.error(f"فشل الطلب: {r.text}")
            except Exception as e:
                st.error(f"تعذر الاتصال بالخادم: {e}")

    if st.button("جلب من NewsAPI/NewsData"):
        with st.spinner("يتم جلب الأخبار بالخلفية..."):
            try:
                r = requests.post(POPULATE_NEWS_URL)
                if r.status_code == 200:
                    st.success(r.json().get("message", "تم البدء بالخلفية"))
                else:
                    st.error(f"فشل الطلب: {r.text}")
            except Exception as e:
                st.error(f"تعذر الاتصال بالخادم: {e}")

    st.markdown("---")
    
    # Health Check
    try:
        response = requests.get("http://127.0.0.1:8001/health")
        if response.status_code == 200:
            st.success("✅ الخادم متصل")
        else:
            st.error("❌ مشكلة في الاتصال بالخادم")
    except:
        st.error("❌ الخادم غير متصل")
        
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
                payload = {"query_text": query_text}
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    verdict = result.get("verdict", "")
                    source_info = result.get("source")
                    status = result.get("status", "unverified")

                    # Display results in a new container
                    with st.container(border=True):
                        # Use the status field returned from the API
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
                else:
                    st.error(f"حدث خطأ في الخادم: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("لا يمكن الاتصال بالخادم. هل قمت بتشغيل `api.py`؟")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
