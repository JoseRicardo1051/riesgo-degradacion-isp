import os
from functools import lru_cache

import joblib
import pandas as pd


BASE_INPUT_COLUMNS = [
    "velocidad_contratada_mbps",
    "distancia_central_km",
    "potencia_rx_dbm",
    "latencia_ms",
    "perdida_paquetes_pct",
    "jitter_ms",
    "uso_ancho_banda_pct",
    "quejas_recientes",
    "antiguedad_meses",
    "distrito",
]


class PredictorError(Exception):
    pass


def _risk_level(probability: float) -> str:
    if probability >= 0.7:
        return "alto"
    if probability >= 0.4:
        return "medio"
    return "bajo"


@lru_cache(maxsize=1)
def load_model_assets():
    model_path = os.getenv("MODEL_PATH", "artifacts/isp_risk_model.pkl")
    columns_path = os.getenv("FEATURE_COLUMNS_PATH", "artifacts/isp_feature_columns.pkl")

    if not os.path.exists(model_path):
        raise PredictorError(f"No se encontro el modelo en {model_path}")
    if not os.path.exists(columns_path):
        raise PredictorError(f"No se encontraron las columnas en {columns_path}")

    model = joblib.load(model_path)
    feature_columns = joblib.load(columns_path)
    return model, feature_columns


def _to_feature_row(payload: dict) -> pd.DataFrame:
    distrito = payload.get("distrito", "").strip()
    row = {
        "velocidad_contratada_mbps": float(payload["velocidad_contratada_mbps"]),
        "distancia_central_km": float(payload["distancia_central_km"]),
        "potencia_rx_dbm": float(payload["potencia_rx_dbm"]),
        "latencia_ms": float(payload["latencia_ms"]),
        "perdida_paquetes_pct": float(payload["perdida_paquetes_pct"]),
        "jitter_ms": float(payload["jitter_ms"]),
        "uso_ancho_banda_pct": float(payload["uso_ancho_banda_pct"]),
        "quejas_recientes": int(payload["quejas_recientes"]),
        "antiguedad_meses": int(payload["antiguedad_meses"]),
        "distrito": distrito,
    }
    return pd.DataFrame([row])


def predict(payload: dict) -> dict:
    model, feature_columns = load_model_assets()
    input_df = _to_feature_row(payload)
    distrito = input_df.loc[0, "distrito"]
    encoded_df = input_df.drop(columns=["distrito"]).copy()

    # Reproduce the same one-hot layout expected by the training dataset.
    for column in feature_columns:
        if column.startswith("distrito_"):
            district_name = column.replace("distrito_", "", 1)
            encoded_df[column] = int(distrito == district_name)

    encoded_df = encoded_df.reindex(columns=feature_columns, fill_value=0)

    predicted_class = int(model.predict(encoded_df)[0])

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(encoded_df)[0][1])
    else:
        probability = float(predicted_class)

    return {
        "predicted_class": predicted_class,
        "predicted_probability": probability,
        "risk_level": _risk_level(probability),
        "features_used": encoded_df.to_dict(orient="records")[0],
    }
