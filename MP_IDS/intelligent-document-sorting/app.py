"""
Локальний вебзастосунок Streamlit для інтелектуального сортування коротких українських документів.
Навчальний мініпроєкт: «Інтелектуальне сортування документів».
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MINILM_LOCAL_DIR = MODELS_DIR / "paraphrase-multilingual-MiniLM-L12-v2"
CLASSIFIER_PATH = MODELS_DIR / "logistic_regression_clf.joblib"
DEMO_PATH = BASE_DIR / "data" / "demo_examples.csv"

MODEL_HF_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MAX_TOKEN_LIMIT = 128
APPROX_WORD_WARNING_LIMIT = 85

CATEGORY_DESCRIPTIONS = {
    "Інформаційне повідомлення": (
        "Повідомляє про факт, подію, результат або поточний стан справ без розгорнутого аналізу, "
        "пояснення причин чи розпорядчих вимог."
    ),
    "Аналітична довідка": (
        "Містить зіставлення даних, пояснення причин, оцінювання тенденцій, узагальнення, "
        "висновки або обґрунтовані припущення."
    ),
    "Організаційний документ": (
        "Визначає порядок дій, завдання, строки виконання, відповідальних осіб, правила "
        "або порядок організації роботи."
    ),
}


@st.cache_resource(show_spinner="Завантаження моделі Sentence Transformers (MiniLM) на CPU...")
def load_embedding_model() -> SentenceTransformer:
    """Кешоване завантаження локальної копії MiniLM або завантаження з Hugging Face при першому старті."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if MINILM_LOCAL_DIR.exists() and any(MINILM_LOCAL_DIR.iterdir()):
        return SentenceTransformer(str(MINILM_LOCAL_DIR), device="cpu")
    model = SentenceTransformer(MODEL_HF_ID, device="cpu")
    model.save(str(MINILM_LOCAL_DIR))
    return model


@st.cache_resource(show_spinner="Завантаження навченого класифікатора LogisticRegression...")
def load_classifier(clf_path_str: str):
    """Кешоване завантаження збереженого класифікатора."""
    return joblib.load(clf_path_str)


def count_tokens_safe(embedder: SentenceTransformer, text: str) -> int:
    """Обчислює точну кількість subword-токенів за допомогою токенізатора MiniLM або наближену оцінку."""
    try:
        tokenizer = embedder.tokenizer
        tokens = tokenizer.encode(text, add_special_tokens=True, truncation=False)
        return len(tokens)
    except Exception:
        return int(len(text.split()) * 1.5)


def main() -> None:
    st.set_page_config(
        page_title="Інтелектуальне сортування документів",
        page_icon="📄",
        layout="centered",
    )

    st.title("📄 Інтелектуальне сортування документів")
    st.caption(
        "Дисципліна: «Методологія інформаційно-аналітичного забезпечення в системі органів військового управління» | "
        "Локальна класифікація на CPU без передачі даних до зовнішніх API"
    )

    st.info(
        "**Методичне застереження:** Це спрощена навчальна класифікація за домінантним комунікативним "
        "призначенням. Короткий уривок тексту не завжди дозволяє достовірно визначити функціональне "
        "призначення повного документа. Усі обчислення виконуються локально на вашому комп'ютері."
    )

    with st.expander("Довідка про категорії класифікації та архітектуру рішення"):
        for cat_name, cat_desc in CATEGORY_DESCRIPTIONS.items():
            st.markdown(f"- **{cat_name}:** {cat_desc}")
        st.markdown("---")
        st.markdown(
            "**Схема обробки:** `Український текст → Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2) "
            "→ 384-вимірний ембеддинг → LogisticRegression → Категорія документа`"
        )

    # Перевірка наявності навченого класифікатора (без автоматичного запуску навчання)
    if not CLASSIFIER_PATH.exists():
        st.error(
            "⚠️ **Класифікатор ще не навчений!** Файл `models/logistic_regression_clf.joblib` не знайдено."
        )
        st.markdown(
            "Навчання не запускається автоматично під час відкриття вебсторінки. "
            "Спочатку виконайте навчання моделі в терміналі PowerShell командою:
"
            "```powershell
python train.py
```
"
            "Після успішного виконання `train.py` оновіть цю сторінку."
        )
        st.stop()

    # Завантаження моделей із обробкою типових помилок
    try:
        embedder = load_embedding_model()
        clf = load_classifier(str(CLASSIFIER_PATH))
    except Exception as exc:
        st.error(
            f"❌ Помилка під час завантаження файлів моделі: `{exc}`.

"
            "Перевірте цілісність каталогів `models/` або повторно запустіть `python train.py`."
        )
        st.stop()

    # Допоміжний вибір демонстраційного прикладу з data/demo_examples.csv
    default_text = ""
    if DEMO_PATH.exists():
        try:
            demo_df = pd.read_csv(DEMO_PATH, encoding="utf-8")
            options = ["— Ввести власний текст вручну —"] + [
                f"Приклад #{row['id']} ({row['expected_label']})"
                for _, row in demo_df.iterrows()
            ]
            selected_opt = st.selectbox(
                "Швидке завантаження демонстраційного прикладу (з `data/demo_examples.csv`):",
                options=options,
            )
            if selected_opt != "— Ввести власний текст вручну —":
                idx = options.index(selected_opt) - 1
                default_text = str(demo_df.iloc[idx]["text"])
                st.caption(
                    f"**Очікувана категорія:** `{demo_df.iloc[idx]['expected_label']}` | "
                    f"**Обґрунтування:** {demo_df.iloc[idx]['justification']}"
                )
        except Exception:
            pass

    user_text = st.text_area(
        "Вставте короткий текст українською мовою (1–3 речення):",
        value=default_text,
        height=140,
        placeholder="Наприклад: Станом на ранок п'ятниці облік навчально-матеріальних активів лабораторії завершено...",
    )

    if st.button("Класифікувати", type="primary"):
        cleaned_text = user_text.strip()
        if not cleaned_text:
            st.warning("⚠️ Поле введення порожнє. Будь ласка, введіть або вставте текст українською мовою.")
            st.stop()

        # Перевірка довжини тексту відносно обмеження моделі MiniLM (128 токенів)
        word_count = len(cleaned_text.split())
        token_count = count_tokens_safe(embedder, cleaned_text)
        max_seq_len = getattr(embedder, "max_seq_length", MAX_TOKEN_LIMIT)

        if token_count > max_seq_len or word_count > APPROX_WORD_WARNING_LIMIT:
            st.warning(
                f"⚠️ **Увага: перевищено максимальну довжину вхідної послідовності моделі!** "
                f"Введений текст містить близько **{token_count} токенів** ({word_count} слів), "
                f"тоді як модель `paraphrase-multilingual-MiniLM-L12-v2` має обмеження `max_seq_length = {max_seq_len}` токенів. "
                f"Хвіст тексту понад {max_seq_len} токенів буде автоматично обрізано під час векторизації, "
                f"що може вплинути на точність класифікації."
            )

        # Локальне обчислення ембеддингу та прогнозування
        embedding = embedder.encode([cleaned_text], convert_to_numpy=True, show_progress_bar=False)
        predicted_label = str(clf.predict(embedding)[0])
        probabilities = clf.predict_proba(embedding)[0]
        classes = list(clf.classes_)

        st.subheader("Результат класифікації")
        st.success(f"**Визначена категорія:** {predicted_label}")
        if predicted_label in CATEGORY_DESCRIPTIONS:
            st.write(f"*{CATEGORY_DESCRIPTIONS[predicted_label]}*")

        st.markdown("#### Оцінки класифікатора (`predict_proba`) за категоріями:")
        prob_rows = []
        for cls_name, prob_val in zip(classes, probabilities):
            prob_rows.append(
                {
                    "Категорія документа": cls_name,
                    "Частка (у %)": round(float(prob_val) * 100, 2),
                }
            )
        prob_df = pd.DataFrame(prob_rows).sort_values(by="Частка (у %)", ascending=False)

        for _, row in prob_df.iterrows():
            pct = row["Частка (у %)"]
            st.write(f"**{row['Категорія документа']}** — `{pct:.2f}%`")
            st.progress(min(max(int(round(pct)), 0), 100))

        st.dataframe(prob_df, use_container_width=True, hide_index=True)

        st.caption(
            "📌 **Важливе пояснення щодо оцінок `predict_proba`:** Наведені відсотки є внутрішніми "
            "математичними оцінками логістичної регресії (softmax/логістичної функції), а **не гарантованою "
            "ймовірністю правильності прогнозу**. Оскільки класифікатор навчено на малому синтетичному "
            "наборі даних (45 навчальних прикладів), ці оцінки можуть бути некаліброваними."
        )


if __name__ == "__main__":
    main()
