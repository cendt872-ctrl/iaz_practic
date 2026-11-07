"""
Скрипт перевірки даних, отримання ембеддингів, навчання та оцінювання класифікатора.
Навчальний мініпроєкт: «Інтелектуальне сортування документів».
"""

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

# Шляхи та базові константи
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "documents.csv"
DEMO_PATH = BASE_DIR / "data" / "demo_examples.csv"
MODELS_DIR = BASE_DIR / "models"
MINILM_LOCAL_DIR = MODELS_DIR / "paraphrase-multilingual-MiniLM-L12-v2"
CLASSIFIER_PATH = MODELS_DIR / "logistic_regression_clf.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
RESULTS_DIR = BASE_DIR / "results"

MODEL_HF_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EXPECTED_LABELS = [
    "Інформаційне повідомлення",
    "Аналітична довідка",
    "Організаційний документ",
]
RANDOM_STATE = 42
TEST_SIZE = 0.25

# Діагностичний набір складних текстів зі змішаними ознаками категорій
# Формується окремо та НЕ змінює тестові метрики основної вибірки
DIAGNOSTIC_EXAMPLES = [
    {
        "id": "diag_1",
        "text": (
            "Зіставлення темпів опрацювання звітності свідчить про затримки через ручне "
            "введення номерів накладних. У зв'язку з цим керівникам підгруп до п'ятниці "
            "подати пропозиції щодо переходу на автоматизовані шаблони обліку."
        ),
        "expected_label": "Організаційний документ",
        "note": "Поєднання аналітичного висновку у першому реченні та прямої розпорядчої вимоги у другому.",
    },
    {
        "id": "diag_2",
        "text": (
            "Станом на середу всі двадцять робочих станцій підключено до локального сервера "
            "кафедри. Така конфігурація мережі дозволила скоротити час завантаження навчальних "
            "корпусів даних майже вдвічі порівняно з попереднім семестром."
        ),
        "expected_label": "Аналітична довідка",
        "note": "Починається як інформаційне повідомлення про факт, але переходить у порівняльне оцінювання ефективності.",
    },
    {
        "id": "diag_3",
        "text": (
            "Відповідно до затвердженого регламенту черговий інженер щоранку о дев'ятій годині "
            "проводить перевірку серверів резервного копіювання. За підсумками тижня жодних "
            "відхилень у роботі обладнання не зафіксовано."
        ),
        "expected_label": "Інформаційне повідомлення",
        "note": "Містить лексику регламентних вимог, проте комунікативна мета — повідомити про фактичний стан справ за тиждень.",
    },
]


def validate_dataset(df: pd.DataFrame) -> None:
    """Перевіряє коректність синтетичного набору даних за всіма критеріями."""
    print("1. Перевірка структури та якості набору даних data/documents.csv...")
    required_cols = {"id", "text", "label"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"У CSV відсутні обов'язкові стовпці: {required_cols - set(df.columns)}")

    if len(df) != 60:
        raise ValueError(f"Очікувалося рівно 60 записів, знайдено: {len(df)}")

    if df.isnull().any().any():
        raise ValueError("У наборі даних виявлено порожні (NaN/null) значення.")

    if (df["text"].str.strip() == "").any():
        raise ValueError("У наборі даних виявлено порожні текстові рядки.")

    dup_count = int(df["text"].duplicated().sum())
    if dup_count > 0:
        raise ValueError(f"Виявлено точні дублікати текстів: {dup_count}")

    invalid_labels = set(df["label"].unique()) - set(EXPECTED_LABELS)
    if invalid_labels:
        raise ValueError(f"Виявлено некоректні мітки класів: {invalid_labels}")

    class_counts = df["label"].value_counts()
    for label in EXPECTED_LABELS:
        count = int(class_counts.get(label, 0))
        if count != 20:
            raise ValueError(f"Для класу '{label}' очікувалося 20 прикладів, знайдено: {count}")

    # Перевірка на надто схожі між собою приклади за допомогою TF-IDF косинусної подібності
    vec = TfidfVectorizer()
    tfidf_matrix = vec.fit_transform(df["text"])
    sim_matrix = cosine_similarity(tfidf_matrix)
    np.fill_diagonal(sim_matrix, 0.0)
    max_sim = float(sim_matrix.max())
    print(f"   - Кількість записів: {len(df)} (по 20 на кожну з 3 категорій)")
    print("   - Порожні значення та дублікати: відсутні")
    print(f"   - Максимальна попарна лексична подібність (TF-IDF cosine): {max_sim:.4f}")
    if max_sim > 0.75:
        raise ValueError(f"Виявлено надто близькі перефразування (max similarity = {max_sim:.4f})")


def load_or_download_minilm() -> SentenceTransformer:
    """Завантажує модель MiniLM з локальної папки або з Hugging Face Hub при першому запуску."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if MINILM_LOCAL_DIR.exists() and any(MINILM_LOCAL_DIR.iterdir()):
        print(f"2. Завантаження збереженої моделі MiniLM з локального каталогу: {MINILM_LOCAL_DIR}")
        model = SentenceTransformer(str(MINILM_LOCAL_DIR), device="cpu")
    else:
        print(f"2. Перший запуск: завантаження готової моделі {MODEL_HF_ID} з Hugging Face (CPU)...")
        model = SentenceTransformer(MODEL_HF_ID, device="cpu")
        model.save(str(MINILM_LOCAL_DIR))
        print(f"   - Модель успішно збережено локально у: {MINILM_LOCAL_DIR}")
    return model


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Файл набору даних не знайдено: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    validate_dataset(df)

    # Перевірка відсутності перетину з demo_examples.csv
    if DEMO_PATH.exists():
        demo_df = pd.read_csv(DEMO_PATH, encoding="utf-8")
        overlap = set(df["text"]).intersection(set(demo_df["text"]))
        if overlap:
            raise ValueError("Виявлено перетин між основним набором та demo_examples.csv!")
        print(f"   - Перевірено demo_examples.csv ({len(demo_df)} прикладів): перетинів з основним набором немає.")

    # Стратифікований поділ 75/25
    train_df, test_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        stratify=df["label"],
        random_state=RANDOM_STATE,
    )

    split_rows = []
    for label in EXPECTED_LABELS:
        tr_cnt = int((train_df["label"] == label).sum())
        te_cnt = int((test_df["label"] == label).sum())
        split_rows.append(
            {
                "Категорія": label,
                "Навчальна_вибірка": tr_cnt,
                "Тестова_вибірка": te_cnt,
                "Разом": tr_cnt + te_cnt,
            }
        )
    split_counts_df = pd.DataFrame(split_rows)
    split_counts_df.to_csv(RESULTS_DIR / "split_counts.csv", index=False, encoding="utf-8")

    print("\n3. Fактичний розподіл прикладів після стратифікованого поділу (75/25):")
    print(split_counts_df.to_string(index=False))

    # Завантаження готової нейромережевої моделі MiniLM (без зміни її ваг)
    embedder = load_or_download_minilm()
    max_seq_len = embedder.max_seq_length
    emb_dim = embedder.get_sentence_embedding_dimension()
    print(f"   - Параметри MiniLM: розмірність ембеддингу = {emb_dim}, max_seq_length = {max_seq_len}")

    # Отримання ембеддингів окремо для навчальної та тестової вибірок
    print("\n4. Обчислення текстових ембеддингів на CPU...")
    X_train_emb = embedder.encode(
        train_df["text"].tolist(),
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    X_test_emb = embedder.encode(
        test_df["text"].tolist(),
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    y_train = train_df["label"].tolist()
    y_test = test_df["label"].tolist()

    # Навчання та оцінювання Baseline (DummyClassifier)
    print("\n5. Навчання та оцінювання базової моделі DummyClassifier(strategy='most_frequent')...")
    dummy_clf = DummyClassifier(strategy="most_frequent")
    dummy_clf.fit(X_train_emb, y_train)
    y_pred_dummy = dummy_clf.predict(X_test_emb)

    dummy_acc = float(accuracy_score(y_test, y_pred_dummy))
    dummy_macro_f1 = float(f1_score(y_test, y_pred_dummy, average="macro", zero_division=0))
    dummy_correct = int((np.array(y_test) == np.array(y_pred_dummy)).sum())
    print(f"   - Baseline Accuracy: {dummy_acc:.4f} ({dummy_correct}/{len(y_test)})")
    print(f"   - Baseline Macro-F1: {dummy_macro_f1:.4f}")

    # Навчання та оцінювання основного класифікатора (LogisticRegression)
    print("\n6. Навчання та оцінювання основного класифікатора LogisticRegression...")
    clf = LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_STATE)
    clf.fit(X_train_emb, y_train)

    y_pred = clf.predict(X_test_emb)
    y_proba = clf.predict_proba(X_test_emb)

    main_acc = float(accuracy_score(y_test, y_pred))
    main_macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    main_correct = int((np.array(y_test) == np.array(y_pred)).sum())

    print(f"   - LogisticRegression Accuracy: {main_acc:.4f} ({main_correct}/{len(y_test)})")
    print(f"   - LogisticRegression Macro-F1: {main_macro_f1:.4f}")

    # Покласові метрики (Precision, Recall, F1-score)
    report_dict = classification_report(
        y_test,
        y_pred,
        labels=EXPECTED_LABELS,
        target_names=EXPECTED_LABELS,
        output_dict=True,
        zero_division=0,
    )
    report_df = pd.DataFrame(report_dict).transpose().reset_index()
    report_df.rename(columns={"index": "Категорія_або_метрика"}, inplace=True)
    report_df.to_csv(RESULTS_DIR / "classification_report.csv", index=False, encoding="utf-8")

    print("\n7. Покласові показники основної моделі (Classification Report):")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=EXPECTED_LABELS,
            target_names=EXPECTED_LABELS,
            digits=4,
            zero_division=0,
        )
    )

    # Матриця помилок (Confusion Matrix)
    cm = confusion_matrix(y_test, y_pred, labels=EXPECTED_LABELS)
    cm_df = pd.DataFrame(
        cm,
        index=[f"Факт: {lbl}" for lbl in EXPECTED_LABELS],
        columns=[f"Прогноз: {lbl}" for lbl in EXPECTED_LABELS],
    )
    cm_df.to_csv(RESULTS_DIR / "confusion_matrix.csv", encoding="utf-8")
    print("8. Матриця помилок (Confusion Matrix):")
    print(cm_df.to_string())

    # Візуалізація матриці помилок у PNG
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=EXPECTED_LABELS)
    disp.plot(cmap="Blues", ax=ax, values_format="d", colorbar=False)
    plt.title("Матриця помилок (LogisticRegression на ембеддингах MiniLM)")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    # Аналіз помилкових прогнозів на тестовій вибірці
    misclassified_rows = []
    class_list = list(clf.classes_)
    for idx_in_test, (_, row) in enumerate(test_df.iterrows()):
        actual_lbl = row["label"]
        pred_lbl = y_pred[idx_in_test]
        if actual_lbl != pred_lbl:
            probs = y_proba[idx_in_test]
            prob_str = "; ".join(
                f"{c}: {probs[i]*100:.1f}%" for i, c in enumerate(class_list)
            )
            misclassified_rows.append(
                {
                    "id": int(row["id"]),
                    "text": row["text"],
                    "expected_label": actual_lbl,
                    "predicted_label": pred_lbl,
                    "probabilities": prob_str,
                }
            )

    misclassified_df = pd.DataFrame(
        misclassified_rows,
        columns=["id", "text", "expected_label", "predicted_label", "probabilities"],
    )
    misclassified_df.to_csv(RESULTS_DIR / "misclassified.csv", index=False, encoding="utf-8")

    print(f"\n9. Помилково класифіковані приклади тестової вибірки: {len(misclassified_df)}")
    if not misclassified_df.empty:
        for _, mrow in misclassified_df.iterrows():
            print(f"   - [ID {mrow['id']}] Очікувалося: '{mrow['expected_label']}' | Прогноз: '{mrow['predicted_label']}'")
            print(f"     Текст: {mrow['text']}")
            print(f"     Оцінки класів: {mrow['probabilities']}")
    else:
        print("   - На 15 прикладах тестової вибірки помилок не зафіксовано.")
        print("   - Перевірка на окремому діагностичному наборі складних змішаних текстів:")

    # Оцінювання на діагностичному наборі складних текстів (не впливає на основні метрики)
    diag_texts = [item["text"] for item in DIAGNOSTIC_EXAMPLES]
    diag_emb = embedder.encode(diag_texts, convert_to_numpy=True, show_progress_bar=False)
    diag_preds = clf.predict(diag_emb)
    diag_probas = clf.predict_proba(diag_emb)

    diag_results = []
    for i, item in enumerate(DIAGNOSTIC_EXAMPLES):
        pred_lbl = diag_preds[i]
        probs = diag_probas[i]
        prob_str = "; ".join(f"{c}: {probs[j]*100:.1f}%" for j, c in enumerate(class_list))
        is_err = pred_lbl != item["expected_label"]
        diag_results.append(
            {
                "id": item["id"],
                "text": item["text"],
                "expected_label": item["expected_label"],
                "predicted_label": pred_lbl,
                "is_error": is_err,
                "probabilities": prob_str,
                "note": item["note"],
            }
        )
        status = "ПОМИЛКА" if is_err else "ЗБІГ"
        print(f"   - [{item['id']}] ({status}) Очікувалося: '{item['expected_label']}' | Прогноз: '{pred_lbl}' ({prob_str})")

    pd.DataFrame(diag_results).to_csv(
        RESULTS_DIR / "diagnostic_evaluation.csv", index=False, encoding="utf-8"
    )

    # Збереження метрик у JSON
    metrics_payload = {
        "dataset": {
            "total_samples": int(len(df)),
            "train_samples": int(len(train_df)),
            "test_samples": int(len(test_df)),
            "random_state": RANDOM_STATE,
            "test_size": TEST_SIZE,
        },
        "embedding_model": {
            "hf_id": MODEL_HF_ID,
            "embedding_dimension": int(emb_dim),
            "max_seq_length": int(max_seq_len),
        },
        "baseline_dummy_most_frequent": {
            "accuracy": dummy_acc,
            "macro_f1": dummy_macro_f1,
            "correct_predictions": dummy_correct,
            "total_test_samples": int(len(y_test)),
        },
        "logistic_regression": {
            "params": {"C": 1.0, "max_iter": 1000, "random_state": RANDOM_STATE},
            "accuracy": main_acc,
            "macro_f1": main_macro_f1,
            "correct_predictions": main_correct,
            "total_test_samples": int(len(y_test)),
            "misclassified_count": int(len(misclassified_df)),
        },
    }
    with open(RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=False, indent=2)

    # Збереження навченого класифікатора та метаданих
    joblib.dump(clf, CLASSIFIER_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_hf_id": MODEL_HF_ID,
                "classes": class_list,
                "embedding_dimension": int(emb_dim),
                "max_seq_length": int(max_seq_len),
                "train_samples": int(len(train_df)),
                "test_accuracy": main_acc,
                "test_macro_f1": main_macro_f1,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\n10. Навчений класифікатор збережено у: {CLASSIFIER_PATH}")

    # Перевірка повторного завантаження класифікатора та тестового прогнозу
    loaded_clf = joblib.load(CLASSIFIER_PATH)
    sample_text = "Учора на сервері кафедри оновлено довідкову базу даних навчальних матеріалів."
    sample_emb = embedder.encode([sample_text], convert_to_numpy=True, show_progress_bar=False)
    sample_pred = loaded_clf.predict(sample_emb)[0]
    print(f"11. Перевірка повторного завантаження класифікатора успішна. Тестовий прогноз: '{sample_pred}'")


if __name__ == "__main__":
    main()
