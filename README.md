# ISP Risk Predictor

Aplicacion local con Flask y MySQL para predecir el riesgo de degradacion del servicio y almacenar el historial de predicciones.

## Estructura

- `app.py`: punto de entrada.
- `app/`: backend Flask.
- `artifacts/`: aqui van el modelo `.pkl` y las columnas del entrenamiento.
- `database/schema.sql`: script de creacion de base de datos.
- `templates/` y `static/`: frontend basico.

## Pasos para ejecutar

1. Crear un entorno virtual.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Copiar `.env.example` a `.env` y completar tus credenciales.
4. Colocar en `artifacts/`:
   - `isp_risk_model.pkl`
   - `isp_feature_columns.pkl`
5. Crear la base de datos con `database/schema.sql`.
6. Ejecutar:

```bash
python app.py
```

7. Abrir:

```text
http://127.0.0.1:5000
```

## Endpoints

- `GET /` interfaz web.
- `POST /api/predict` predice y guarda el resultado.
- `GET /api/history` devuelve historial en JSON.
- `GET /health` verifica estado del backend.

## Nota

La app espera que el modelo guardado sea un `Pipeline` completo de scikit-learn.
