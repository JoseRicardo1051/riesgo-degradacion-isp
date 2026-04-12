from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


TARGET_COL = "riesgo_degradacion_servicio"
ID_COL = "cliente_id"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def format_pct(value: float) -> str:
    return f"{value:.2f}%"


def quality_report(df: pd.DataFrame) -> dict:
    null_count = df.isna().sum().sort_values(ascending=False)
    null_pct = (df.isna().mean() * 100).sort_values(ascending=False)
    duplicates = int(df.duplicated().sum())
    duplicate_ids = int(df[ID_COL].duplicated().sum()) if ID_COL in df.columns else 0
    constant_cols = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]

    return {
        "shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_count": {col: int(value) for col, value in null_count.items()},
        "null_pct": {col: round(float(value), 4) for col, value in null_pct.items()},
        "duplicate_rows": duplicates,
        "duplicate_cliente_id": duplicate_ids,
        "constant_columns": constant_cols,
    }


def outlier_report(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    rows = []
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        rows.append(
            {
                "variable": col,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower,
                "upper_bound": upper,
                "outlier_count": int(mask.sum()),
                "outlier_pct": round(float(mask.mean() * 100), 4),
            }
        )
    return pd.DataFrame(rows).sort_values(["outlier_pct", "variable"], ascending=[False, True])


def build_markdown_summary(
    df: pd.DataFrame,
    quality: dict,
    target_distribution: pd.DataFrame,
    corr_with_target: pd.Series,
    district_risk: pd.DataFrame,
    outliers: pd.DataFrame,
) -> str:
    lines = []
    lines.append("# Resumen EDA ISP")
    lines.append("")
    lines.append("## Calidad del dataset")
    lines.append(f"- Filas: {quality['shape']['rows']}")
    lines.append(f"- Columnas: {quality['shape']['cols']}")
    lines.append(f"- Filas duplicadas: {quality['duplicate_rows']}")
    lines.append(f"- `cliente_id` duplicado: {quality['duplicate_cliente_id']}")
    lines.append(
        "- Columnas constantes: "
        + (", ".join(quality["constant_columns"]) if quality["constant_columns"] else "ninguna")
    )
    lines.append("")
    lines.append("## Variable objetivo")
    for _, row in target_distribution.iterrows():
        lines.append(
            f"- Clase {int(row[TARGET_COL])}: {int(row['count'])} registros ({format_pct(row['pct'])})"
        )
    lines.append("")
    lines.append("## Variables numéricas más relacionadas con la variable objetivo")
    for col, value in corr_with_target.items():
        lines.append(f"- `{col}`: {value:.4f}")
    lines.append("")
    lines.append("## Riesgo promedio por distrito")
    for _, row in district_risk.iterrows():
        lines.append(
            f"- `{row['distrito']}`: {row['risk_rate']:.4f} con {int(row['count'])} registros"
        )
    lines.append("")
    lines.append("## Revisión de outliers (IQR)")
    for _, row in outliers.head(8).iterrows():
        lines.append(
            f"- `{row['variable']}`: {int(row['outlier_count'])} outliers ({format_pct(row['outlier_pct'])})"
        )
    lines.append("")
    lines.append("## Reglas de limpieza aplicadas")
    lines.append("- Se elimina `cliente_id` por ser identificador.")
    lines.append("- Se elimina `tecnologia` por ser constante y no aportar señal predictiva.")
    lines.append("- Se aplica one-hot encoding a `distrito`.")
    lines.append("- Se conserva la variable objetivo al final del dataset limpio.")
    lines.append("")
    lines.append("## Recomendaciones para modelado")
    lines.append("- Usar división estratificada por el desbalance de la clase objetivo.")
    lines.append("- Evaluar con `precision`, `recall`, `f1` y `roc_auc`, no solo accuracy.")
    lines.append("- Escalar variables si pruebas modelos sensibles a escala.")
    return "\n".join(lines)


def create_plots(
    df: pd.DataFrame,
    output_dir: Path,
    corr_with_target: pd.Series,
    district_risk: pd.DataFrame,
) -> None:
    ensure_dir(output_dir)
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x=TARGET_COL)
    plt.title("Distribución de la variable objetivo")
    plt.xlabel("Riesgo de degradación")
    plt.ylabel("Número de registros")
    plt.tight_layout()
    plt.savefig(output_dir / "target_distribution.png", dpi=160)
    plt.close()

    numeric_cols = [
        col for col in df.select_dtypes(include=["number"]).columns.tolist() if col not in [ID_COL, TARGET_COL]
    ]
    for col in numeric_cols:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        sns.histplot(df[col], kde=True, ax=axes[0], color="#3b82f6")
        axes[0].set_title(f"Distribución de {col}")
        sns.boxplot(data=df, x=TARGET_COL, y=col, ax=axes[1], color="#22c55e")
        axes[1].set_title(f"{col} vs {TARGET_COL}")
        plt.tight_layout()
        plt.savefig(output_dir / f"{col}.png", dpi=160)
        plt.close(fig)

    plt.figure(figsize=(10, 8))
    corr = df.select_dtypes(include=["number"]).drop(columns=[ID_COL], errors="ignore").corr()
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=True, fmt=".2f")
    plt.title("Matriz de correlación")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_matrix.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.barplot(x=corr_with_target.values, y=corr_with_target.index, color="#f59e0b")
    plt.title("Correlación con la variable objetivo")
    plt.xlabel("Correlación")
    plt.ylabel("Variable")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_with_target.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(data=district_risk, x="distrito", y="risk_rate", color="#8b5cf6")
    plt.title("Riesgo promedio por distrito")
    plt.xlabel("Distrito")
    plt.ylabel("Tasa de riesgo")
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.savefig(output_dir / "district_risk.png", dpi=160)
    plt.close()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    model_df = df.copy()

    drop_cols = [col for col in [ID_COL, "tecnologia"] if col in model_df.columns]
    model_df = model_df.drop(columns=drop_cols)

    if "distrito" in model_df.columns:
        model_df = pd.get_dummies(model_df, columns=["distrito"], drop_first=True, dtype=int)

    feature_cols = [col for col in model_df.columns if col != TARGET_COL]
    ordered_cols = feature_cols + [TARGET_COL]
    return model_df[ordered_cols]


def run(input_csv: Path, output_dir: Path) -> None:
    ensure_dir(output_dir)
    charts_dir = output_dir / "charts"
    ensure_dir(charts_dir)

    df = pd.read_csv(input_csv)
    quality = quality_report(df)

    target_distribution = (
        df[TARGET_COL]
        .value_counts(dropna=False)
        .rename_axis(TARGET_COL)
        .reset_index(name="count")
        .sort_values(TARGET_COL)
    )
    target_distribution["pct"] = target_distribution["count"] / len(df) * 100

    corr_with_target = (
        df.select_dtypes(include=["number"])
        .drop(columns=[ID_COL], errors="ignore")
        .corr(numeric_only=True)[TARGET_COL]
        .drop(labels=[TARGET_COL])
        .sort_values(key=lambda s: s.abs(), ascending=False)
    )

    district_risk = (
        df.groupby("distrito")[TARGET_COL]
        .agg(risk_rate="mean", count="size")
        .reset_index()
        .sort_values("risk_rate", ascending=False)
    )

    outliers = outlier_report(df.drop(columns=[ID_COL], errors="ignore"))
    cleaned_df = clean_dataset(df)

    create_plots(df, charts_dir, corr_with_target.head(10), district_risk)

    save_text(output_dir / "eda_summary.md", build_markdown_summary(
        df=df,
        quality=quality,
        target_distribution=target_distribution,
        corr_with_target=corr_with_target.head(10),
        district_risk=district_risk,
        outliers=outliers,
    ))
    save_text(output_dir / "quality_report.json", json.dumps(quality, indent=2, ensure_ascii=False))
    target_distribution.to_csv(output_dir / "target_distribution.csv", index=False)
    corr_with_target.rename("correlation").to_csv(output_dir / "correlation_with_target.csv")
    district_risk.to_csv(output_dir / "district_risk.csv", index=False)
    outliers.to_csv(output_dir / "outlier_report.csv", index=False)
    cleaned_df.to_csv(output_dir / "data_isp_model_ready.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EDA completo y limpieza para el dataset ISP.")
    parser.add_argument(
        "--input",
        default=r"C:\Users\User\Downloads\data_isp.csv",
        help="Ruta del CSV original.",
    )
    parser.add_argument(
        "--output-dir",
        default="eda_outputs",
        help="Directorio donde se guardarán reportes, gráficos y dataset limpio.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(Path(args.input), Path(args.output_dir))
