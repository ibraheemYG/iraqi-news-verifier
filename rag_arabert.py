import os
from typing import List, Dict

import ollama
try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
except Exception as e:
    genai = None
    print(f"⚠ Failed to import google.generativeai: {e}")

# Always prioritize environment variables for API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        from config import GEMINI_API_KEY as CONFIG_KEY
        GEMINI_API_KEY = CONFIG_KEY
    except Exception:
        pass

# Debug: Check if key is loaded (show only first/last 4 chars for security)
if GEMINI_API_KEY:
    key_preview = f"{GEMINI_API_KEY[:4]}...{GEMINI_API_KEY[-4:]}" if len(GEMINI_API_KEY) > 8 else "***"
    print(f"✓ GEMINI_API_KEY loaded: {key_preview}")
else:
    print("⚠ GEMINI_API_KEY not found!")

def build_context_block(retrieved_context: List[Dict]) -> str:
    blocks = []
    for ctx in retrieved_context:
        blocks.append(
            f"المصدر: {ctx['url']}\nالعنوان: {ctx['title']}\nالمحتوى المختصر: {ctx['body']}\nدرجة التشابه: {ctx.get('similarity', 0):.2f}"
        )
    return "\n\n".join(blocks)


def generate_response(user_query: str, retrieved_context: List[Dict], is_relevant: bool) -> tuple[str, bool]:
    """
    Generates a response using Gemini based on the user query and retrieved context.
    Returns the response string and a boolean indicating if the query was a question.
    """
    # --- Intent Detection: Is the user asking a question? ---
    question_words = ["هل", "ماذا", "متى", "أين", "لماذا", "كيف", "من", "بكم", "كم"]
    # A simple check to see if any of the question words are in the query
    is_question = any(word in user_query.strip().split() for word in question_words)

    # --- Prompt Engineering ---
    kb = build_context_block(retrieved_context)

    if is_question:
        # Prompt for answering questions based on provided context
        prompt = f"""
        أنت مساعد باحث متخصص في الشأن العراقي. اقرأ فقط النصوص التالية وأجب عن سؤال المستخدم اعتماداً عليها فقط.
        ---
        {kb}
        ---
        سؤال المستخدم: "{user_query}"

        إرشادات صارمة:
        1) استخدم المعلومات الموجودة فقط في النصوص أعلاه. لا تضف أي معلومات خارجية.
        2) إذا كانت النصوص تحتوي صراحةً على إجابة، ابدأ السطر الأول بجملة موجزة ثم قدّم جملة واحدة تشرح أي نص يدعم الإجابة واذكر الرابط الأكثر صلة.
        3) إذا لم تحتوي النصوص على إجابة كافية، اكتب بدقة: "لا توجد معلومات كافية في المصادر للإجابة على هذا السؤال." ثم اقترح مصدرًا أو مصطلح بحث يُحسّن النتائج.
        4) كن موجزًا (سطر إلى سطرين إضافيين كحد أقصى). اللغة: العربية.
        """
    elif is_relevant:
        # Prompt for verifying a news claim that has relevant context
        prompt = f"""
        أنت نظام تحقق أخبار متحفظ ومحايد وذكي. لديك هذه النصوص فقط:
        ---
        {kb}
        ---
        ادعاء المستخدم: "{user_query}"

        إرشادات صارمة لكتابة الحكم:
        1) استند فقط إلى النصوص المعطاة. لا تضف أو تخمن معلومات خارجية.
        2) كن ذكياً: قد يستخدم المستخدم اختصارات أو أسماء مختلفة (مثل "فيتي" لـ"فينيسيوس"، "الريال" لـ"ريال مدريد"، "جزاء" لـ"ركلة جزاء"). إذا وجدت تطابقاً في المعنى مع الأسماء المختلفة، اعتبره تطابقاً صحيحاً.
        3) ابدأ السطر الأول إما بـ "✅ الخبر موثوق" أو "⚠️ الخبر غير مؤكد" بحيث يتوافق هذا العنوان بدقة مع الشرح التفصيلي الذي يلي.
        4) إذا أكدت (✅): اذكر في سطر واحد أي جملة/مقطع من النصوص يدعم الادعاء ولماذا. إذا كان المستخدم استخدم اسماً مختصراً، اذكر ذلك بشكل واضح (مثال: "فيتي هو الاسم المختصر لفينيسيوس").
        5) إذا لم تتمكن من التأكيد (⚠️): اشرح بإيجاز سبب عدم التأكيد (تضارب في النصوص، غياب التفاصيل، مجرد تكهن).
        6) طول الإجابة: إجمالي 2-4 جمل بعد السطر الأول. لا تتكرر.
        7) اللغة: العربية. التزم بالصياغة والنبرة المهنية والمحايدة.
        """
    else:
        # Prompt for a claim with no relevant context found
        prompt = f"""
        أنت نظام تحقق أخبار. لقد بحثت في قاعدة البيانات ولم تجد أي نصوص ذات صلة.
        ادعاء المستخدم: "{user_query}"

        إرشادات:
        1) ابدأ السطر الأول بـ "⚠️ الخبر غير مؤكد".
        2) اشرح باختصار (1-2 جمل) أن قاعدة المصادر لا تحتوي على معلومات تدعم الادعاء، واذكر أنك استندت فقط إلى النصوص الموجودة.
        3) اقترح خطوة عملية للمستخدم (مثل: ذكر تاريخ/مكان أدق، أو رابط منشور، أو كلمات مفتاحية).
        4) اللغة: العربية.
        """

    print(f"--- Sending prompt to LLM (Intent: {'Question' if is_question else 'Verification'}) ---")

    # --- LLM Invocation (Gemini Primary, Ollama fallback for local only) ---
    last_err = None
    
    # 1) Try Gemini first (required for cloud deployment)
    gemini_errors = []
    if GEMINI_API_KEY and genai is not None:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # Use CORRECT model names for Gemini API v1beta
            # Reference: https://ai.google.dev/gemini-api/docs/models/gemini
            gemini_models = [
                os.getenv("GEMINI_MODEL"),  # Custom if provided
                "models/gemini-1.5-flash",
                "models/gemini-1.5-pro",
                "models/gemini-pro",
            ]
            
            for gemini_model in gemini_models:
                if not gemini_model:
                    continue
                try:
                    print(f"🔄 Trying Gemini model: {gemini_model}")
                    model = genai.GenerativeModel(gemini_model)
                    resp = model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.1,
                            "top_p": 0.8,
                            "top_k": 40,
                            "max_output_tokens": 500,
                        }
                    )
                    content = getattr(resp, "text", None)
                    if not content and getattr(resp, "candidates", None):
                        parts = []
                        for c in resp.candidates:
                            for p in getattr(c, "content", {}).get("parts", []):
                                parts.append(str(p.get("text", "")))
                        content = "\n".join(parts)
                    if content:
                        print(f"✓ Response generated successfully via Gemini ({gemini_model})")
                        return content.strip(), is_question
                    else:
                        err_msg = f"Empty response from {gemini_model}"
                        print(f"⚠ {err_msg}")
                        gemini_errors.append(err_msg)
                except Exception as model_err:
                    err_msg = f"{gemini_model}: {str(model_err)[:150]}"
                    print(f"⚠ Gemini model failed: {err_msg}")
                    gemini_errors.append(err_msg)
                    continue
            
            last_err = f"All Gemini models failed:\n" + "\n".join(f"  - {e}" for e in gemini_errors[-3:])
        except Exception as e:
            last_err = f"Gemini configuration error: {e}"
            print(f"⚠ Gemini failed: {e}")
    else:
        last_err = "Gemini API key not configured"
        print("⚠ Gemini not available (no API key)")

    # 2) Fallback to Ollama (local development only)
    try:
        forced = os.getenv("OLLAMA_MODEL")
        preferred_models = [
            forced if forced else "deepseek-v3.1:671b-cloud",
            "gpt-oss:120b-cloud",
            "llama3.2:1b",
            "phi3:mini",
        ]

        for m in preferred_models:
            try:
                resp = ollama.chat(
                    model=m,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.1, "num_predict": 300},
                )
                print(f"✓ Response generated via Ollama ({m})")
                return resp["message"]["content"], is_question
            except Exception as e:
                continue
    except Exception:
        pass

    # 3) If both failed, return clear error message
    error_msg = f"""⚠️ خطأ في النظام

لم يتمكن النظام من الاتصال بخدمة الذكاء الاصطناعي.

السبب المحتمل: {last_err}

الحل:
- تأكد من إضافة GEMINI_API_KEY في Secrets (Streamlit Cloud)
- أو تأكد من وجود المفتاح في ملف .env محلياً

يمكنك الحصول على مفتاح مجاني من: https://makersuite.google.com/app/apikey"""
    
    return error_msg, is_question
