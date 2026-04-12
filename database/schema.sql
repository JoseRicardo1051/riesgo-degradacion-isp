CREATE DATABASE IF NOT EXISTS isp_risk_db;
USE isp_risk_db;

CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    distrito VARCHAR(120) NOT NULL,
    velocidad_contratada_mbps FLOAT NOT NULL,
    distancia_central_km FLOAT NOT NULL,
    potencia_rx_dbm FLOAT NOT NULL,
    latencia_ms FLOAT NOT NULL,
    perdida_paquetes_pct FLOAT NOT NULL,
    jitter_ms FLOAT NOT NULL,
    uso_ancho_banda_pct FLOAT NOT NULL,
    quejas_recientes INT NOT NULL,
    antiguedad_meses INT NOT NULL,
    predicted_class TINYINT NOT NULL,
    predicted_probability FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
USE isp_risk_db;
SELECT * FROM predictions ORDER BY id DESC;

