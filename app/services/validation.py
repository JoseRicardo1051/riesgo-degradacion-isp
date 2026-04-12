from .predictor import BASE_INPUT_COLUMNS, PredictorError


def validate_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise PredictorError("El cuerpo de la solicitud debe ser JSON.")

    missing = [field for field in BASE_INPUT_COLUMNS if field not in payload]
    if missing:
        raise PredictorError(f"Faltan campos obligatorios: {', '.join(missing)}")

    distrito = str(payload.get("distrito", "")).strip()
    if not distrito:
        raise PredictorError("El distrito es obligatorio.")

    return payload
