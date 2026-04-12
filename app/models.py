from .extensions import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    distrito = db.Column(db.String(120), nullable=False)
    velocidad_contratada_mbps = db.Column(db.Float, nullable=False)
    distancia_central_km = db.Column(db.Float, nullable=False)
    potencia_rx_dbm = db.Column(db.Float, nullable=False)
    latencia_ms = db.Column(db.Float, nullable=False)
    perdida_paquetes_pct = db.Column(db.Float, nullable=False)
    jitter_ms = db.Column(db.Float, nullable=False)
    uso_ancho_banda_pct = db.Column(db.Float, nullable=False)
    quejas_recientes = db.Column(db.Integer, nullable=False)
    antiguedad_meses = db.Column(db.Integer, nullable=False)
    predicted_class = db.Column(db.Integer, nullable=False)
    predicted_probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "distrito": self.distrito,
            "velocidad_contratada_mbps": self.velocidad_contratada_mbps,
            "distancia_central_km": self.distancia_central_km,
            "potencia_rx_dbm": self.potencia_rx_dbm,
            "latencia_ms": self.latencia_ms,
            "perdida_paquetes_pct": self.perdida_paquetes_pct,
            "jitter_ms": self.jitter_ms,
            "uso_ancho_banda_pct": self.uso_ancho_banda_pct,
            "quejas_recientes": self.quejas_recientes,
            "antiguedad_meses": self.antiguedad_meses,
            "predicted_class": self.predicted_class,
            "predicted_probability": self.predicted_probability,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
