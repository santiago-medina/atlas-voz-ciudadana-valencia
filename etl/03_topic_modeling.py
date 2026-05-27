"""
03_topic_modeling.py — Topic modeling de los títulos de propuestas Decidim.

Pasos:
  1. Cargar los títulos limpios.
  2. Embeddings semánticos con paraphrase-multilingual-MiniLM-L12-v2
     de sentence-transformers (modelo MiniLM, 118M parámetros, 50+ idiomas
     soportados oficialmente, entre ellos castellano (es) y catalán (ca),
     este último cubre el valenciano como variedad del catalán).
     Model card: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  3. Reducción de dimensión con UMAP.
  4. Clustering con HDBSCAN (no necesita fijar k a priori).
  5. Para cada cluster, top palabras representativas vía c-TF-IDF.
  6. Output: data/processed/topics.csv (cluster_id, top_words, n)
            data/processed/decidim_topics.csv (propuesta_id, cluster_id)

Este script NO etiqueta los clusters; eso se hace en 04_label_topics.py
(con un modelo o a mano).
"""

import re
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CACHE = PROC / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
EMBED_CACHE = CACHE / "embeddings.npy"
TITLE_CACHE = CACHE / "titles.csv"


# ---------------------------------------------------------------------------
# Spanish/Catalan stopwords (compact, in-line)
# ---------------------------------------------------------------------------
STOPWORDS = set("""
a al ante bajo con contra de del desde durante en entre hacia hasta
mediante para por según sin sobre tras y o u e ni que como cuando
donde quien cual cuyos cuyas le les la las el los lo se su sus mi mis
tu tus nos os me te este esta esto estos estas ese esa eso esos esas
aquel aquella aquello aquellos aquellas otro otra otros otras todo toda
todos todas mucho mucha muchos muchas poco poca pocos pocas más menos
muy muyo tanto tanta tantos tantas alguno alguna algunos algunas
ninguno ninguna ningunos ningunas cada qué cuál cuáles si no es son
era eran ser sido siendo está están estaba estaban estado estando ha
han había habían haber tiene tienen tenia tenian tener para por con
sin sobre entre hacia desde una uno unos unas
i a la del en de el als amb sobre per pels les el els un una uns
unes el la els les a de del per al pel pels això aquest aquesta dels
aix ais aquests aquestes
propuesta propuestas proposta propostes mejora mejoras millora millores
""".split())


def load_titles() -> pd.DataFrame:
    df = pd.read_csv(PROC / "decidim.csv")
    df = df[df["Titulo"].notna() & (df["Titulo"] != "NA")].copy()
    df["titulo_clean"] = (
        df["Titulo"]
        .astype(str)
        .str.lower()
        .str.replace(r"[^\w\sáéíóúñçàèìòùü\-]", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df = df[df["titulo_clean"].str.len() > 3].copy()
    return df.reset_index(drop=True)


def compute_embeddings(texts: list[str]) -> np.ndarray:
    if EMBED_CACHE.exists():
        cached_titles = pd.read_csv(TITLE_CACHE)["titulo_clean"].tolist()
        if cached_titles == texts:
            print(f"   embeddings desde cache ({EMBED_CACHE})")
            return np.load(EMBED_CACHE)
    from sentence_transformers import SentenceTransformer

    print(f"   cargando modelo {EMBEDDING_MODEL}…")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"   generando embeddings de {len(texts)} títulos…")
    emb = model.encode(texts, show_progress_bar=True, batch_size=64, normalize_embeddings=True)
    np.save(EMBED_CACHE, emb)
    pd.DataFrame({"titulo_clean": texts}).to_csv(TITLE_CACHE, index=False)
    return emb


def reduce_and_cluster(emb: np.ndarray) -> np.ndarray:
    try:
        import umap
    except ImportError:
        from sklearn.decomposition import PCA
        print("   UMAP no disponible, usando PCA (50d)")
        reduced = PCA(n_components=50, random_state=42).fit_transform(emb)
    else:
        print("   reduciendo dimensión con UMAP…")
        reduced = umap.UMAP(
            n_components=10,
            n_neighbors=15,
            min_dist=0.0,
            metric="cosine",
            random_state=42,
        ).fit_transform(emb)

    import hdbscan
    print("   clustering con HDBSCAN…")
    cluster = hdbscan.HDBSCAN(
        min_cluster_size=25,
        min_samples=5,
        metric="euclidean",
        cluster_selection_method="eom",
    )
    labels = cluster.fit_predict(reduced)
    return labels


def top_words_per_cluster(df: pd.DataFrame, labels: np.ndarray, n_words: int = 12) -> pd.DataFrame:
    df = df.copy()
    df["cluster_id"] = labels

    # c-TF-IDF: stack titles per cluster, then TF-IDF across clusters
    cluster_docs: dict[int, str] = {}
    for cid in sorted(df["cluster_id"].unique()):
        if cid == -1:
            continue
        cluster_docs[cid] = " ".join(df[df["cluster_id"] == cid]["titulo_clean"].tolist())

    cluster_ids = list(cluster_docs.keys())
    docs = [cluster_docs[c] for c in cluster_ids]

    vec = CountVectorizer(
        stop_words=list(STOPWORDS),
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
    )
    counts = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())

    # Class-based TF-IDF: tf in this class * log(N_total_terms / sum_over_classes)
    counts_a = counts.toarray()
    tf = counts_a / counts_a.sum(axis=1, keepdims=True).clip(min=1)
    df_term = (counts_a > 0).sum(axis=0)
    idf = np.log((len(cluster_ids) + 1) / (df_term + 1)) + 1
    score = tf * idf

    rows = []
    for i, cid in enumerate(cluster_ids):
        top_idx = score[i].argsort()[::-1][:n_words]
        top = vocab[top_idx].tolist()
        rows.append(
            {
                "cluster_id": cid,
                "n_propuestas": int((labels == cid).sum()),
                "top_words": ", ".join(top),
            }
        )
    return pd.DataFrame(rows).sort_values("n_propuestas", ascending=False).reset_index(drop=True)


def main() -> None:
    print("→ Cargando títulos de propuestas Decidim…")
    df = load_titles()
    print(f"   {len(df)} propuestas con título legible")

    print("→ Generando embeddings…")
    emb = compute_embeddings(df["titulo_clean"].tolist())
    print(f"   shape={emb.shape}")

    print("→ Reduciendo y clusterizando…")
    labels = reduce_and_cluster(emb)
    n_clusters = int(labels.max() + 1) if labels.max() >= 0 else 0
    n_noise = int((labels == -1).sum())
    print(f"   {n_clusters} clusters, {n_noise} en ruido")

    print("→ Calculando top palabras por cluster (c-TF-IDF)…")
    topics = top_words_per_cluster(df, labels)
    topics.to_csv(PROC / "topics.csv", index=False)
    print(f"   topics → {PROC/'topics.csv'}")
    print()
    print("Top 15 clusters:")
    for _, r in topics.head(15).iterrows():
        print(f"  [{r['cluster_id']:3}] n={r['n_propuestas']:4}  {r['top_words']}")

    df_out = df[["id", "Edicion", "Id_Propuesta", "Titulo", "id_distrito", "nombre_distrito", "Numero_Apoyos", "Seleccionada"]].copy()
    df_out["cluster_id"] = labels
    df_out.to_csv(PROC / "decidim_topics.csv", index=False)
    print(f"\n   asignaciones → {PROC/'decidim_topics.csv'}")


if __name__ == "__main__":
    main()
