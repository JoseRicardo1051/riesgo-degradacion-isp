from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Prediction
from ..services.predictor import PredictorError, predict
from ..services.validation import validate_payload


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/history")
def history():
    rows = Prediction.query.order_by(Prediction.created_at.desc()).limit(50).all()
    return jsonify([row.to_dict() for row in rows])


@api_bp.post("/predict")
def predict_route():
    try:
        payload = validate_payload(request.get_json(silent=True) or {})
        result = predict(payload)

        row = Prediction(
            distrito=payload["distrito"],
            velocidad_contratada_mbps=payload["velocidad_contratada_mbps"],
            distancia_central_km=payload["distancia_central_km"],
            potencia_rx_dbm=payload["potencia_rx_dbm"],
            latencia_ms=payload["latencia_ms"],
            perdida_paquetes_pct=payload["perdida_paquetes_pct"],
            jitter_ms=payload["jitter_ms"],
            uso_ancho_banda_pct=payload["uso_ancho_banda_pct"],
            quejas_recientes=payload["quejas_recientes"],
            antiguedad_meses=payload["antiguedad_meses"],
            predicted_class=result["predicted_class"],
            predicted_probability=result["predicted_probability"],
            risk_level=result["risk_level"],
        )
        db.session.add(row)
        db.session.commit()

        response = row.to_dict()
        response["message"] = "Prediccion generada y guardada correctamente."
        return jsonify(response), 201

    except PredictorError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Error interno: {exc}"}), 500
