from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

# =========================
# Paths
# =========================

READ_PATH = "data/processed/cleaned_data.csv"
WRITE_PATH = "data/processed/models/per_rendered_object_no_release_year.csv"
SUMMARY_WRITE_PATH = (
    "data/processed/models/per_rendered_object_no_release_year_summary.csv"
)


def run_model_comparison() -> None:
    # =========================
    # 1. Load data
    # =========================

    df = pd.read_csv(READ_PATH)

    target = "renderTime"
    object_col = "renderedObject"

    # Remove invalid render times
    df = df[df[target] > 0].copy()

    # =========================
    # 2. Feature sets
    # =========================
    # renderedObject is not included because we train one model per renderedObject.
    # gpuName is excluded.
    # releaseYear is excluded.

    feature_sets = {
        "numerical_only": [
            "baseClock",
            "boostClock",
            "textureRate",
            "pixelRate",
            "rtCores",
            "tensorCores",
        ],
        "mixed_no_gpu_name": [
            "gpuBackend",
            "baseClock",
            "boostClock",
            "textureRate",
            "pixelRate",
            "architecture",
            "memoryType",
            "generation",
            "busInterface",
            "rtCores",
            "tensorCores",
        ],
    }

    all_numerical_features = [
        "baseClock",
        "boostClock",
        "textureRate",
        "pixelRate",
        "rtCores",
        "tensorCores",
    ]

    all_categorical_features = [
        "gpuBackend",
        "architecture",
        "memoryType",
        "generation",
        "busInterface",
    ]

    # =========================
    # 3. Validation
    # =========================

    required_columns = sorted(
        set(
            [target, object_col]
            + [col for feature_list in feature_sets.values() for col in feature_list]
        )
    )

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing columns in dataset: {missing_columns}")

    if df[required_columns].isnull().any().any():
        raise ValueError("Dataset contains missing values in selected columns.")

    print("Rows used:", len(df))
    print()
    print("Rendered object counts:")
    print(df[object_col].value_counts())
    print()

    # =========================
    # 4. Helper functions
    # =========================

    def split_feature_types(selected_features):
        selected_numerical = [
            col for col in selected_features if col in all_numerical_features
        ]

        selected_categorical = [
            col for col in selected_features if col in all_categorical_features
        ]

        return selected_numerical, selected_categorical

    def make_onehot_preprocessor(selected_features):
        selected_numerical, selected_categorical = split_feature_types(
            selected_features
        )

        transformers = []

        if selected_numerical:
            transformers.append(("num", StandardScaler(), selected_numerical))

        if selected_categorical:
            transformers.append((
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                selected_categorical,
            ))

        return ColumnTransformer(
            transformers=transformers,
            remainder="drop",
        )

    def make_hgb_preprocessor_and_mask(selected_features):
        selected_numerical, selected_categorical = split_feature_types(
            selected_features
        )

        transformers = []

        if selected_numerical:
            transformers.append(("num", "passthrough", selected_numerical))

        if selected_categorical:
            transformers.append((
                "cat",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=np.nan,
                    encoded_missing_value=np.nan,
                    max_categories=254,
                    dtype=np.float64,
                ),
                selected_categorical,
            ))

        categorical_mask = [False] * len(selected_numerical) + [True] * len(
            selected_categorical
        )

        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="drop",
        )

        return preprocessor, categorical_mask

    def make_log_target_model(regressor):
        return TransformedTargetRegressor(
            regressor=regressor,
            func=np.log1p,
            inverse_func=np.expm1,
        )

    # =========================
    # 5. Cross-validation setup
    # =========================

    cv = KFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    )

    scoring = {
        "MAE": "neg_mean_absolute_error",
        "RMSE": "neg_root_mean_squared_error",
        "R2": "r2",
    }

    # =========================
    # 6. Train/test one model per renderedObject
    # =========================

    MIN_ROWS_PER_OBJECT = 500

    results = []

    for rendered_object, object_df in df.groupby(object_col):
        object_row_count = len(object_df)

        if object_row_count < MIN_ROWS_PER_OBJECT:
            print(
                f"Skipping {rendered_object}: only {object_row_count} rows "
                f"(minimum is {MIN_ROWS_PER_OBJECT})"
            )
            continue

        print()
        print("======================================")
        print(f"Rendered object: {rendered_object}")
        print(f"Rows: {object_row_count}")
        print("======================================")

        y = object_df[target]

        for feature_set_name, selected_features in feature_sets.items():
            print()
            print(f"Feature set: {feature_set_name}")

            X = object_df[selected_features]

            onehot_preprocessor = make_onehot_preprocessor(selected_features)
            hgb_preprocessor, hgb_categorical_mask = make_hgb_preprocessor_and_mask(
                selected_features
            )

            models = {
                "Dummy Median Baseline": {
                    "preprocessor": onehot_preprocessor,
                    "regressor": DummyRegressor(strategy="median"),
                },
                "Ridge Regression Log Target": {
                    "preprocessor": onehot_preprocessor,
                    "regressor": make_log_target_model(Ridge(alpha=1.0)),
                },
                "Random Forest Log Target": {
                    "preprocessor": onehot_preprocessor,
                    "regressor": make_log_target_model(
                        RandomForestRegressor(
                            n_estimators=100,
                            max_depth=25,
                            max_samples=0.7,
                            random_state=42,
                            n_jobs=4,
                        )
                    ),
                },
                "Hist Gradient Boosting Log Target": {
                    "preprocessor": hgb_preprocessor,
                    "regressor": make_log_target_model(
                        HistGradientBoostingRegressor(
                            max_iter=300,
                            learning_rate=0.08,
                            max_leaf_nodes=31,
                            categorical_features=hgb_categorical_mask,
                            random_state=42,
                        )
                    ),
                },
            }

            for model_name, config in models.items():
                print(f"Testing {model_name}...")

                model = Pipeline(
                    steps=[
                        ("preprocessor", config["preprocessor"]),
                        ("regressor", config["regressor"]),
                    ]
                )

                scores = cross_validate(
                    model,
                    X,
                    y,
                    cv=cv,
                    scoring=scoring,
                    n_jobs=1,
                    error_score="raise",
                )

                mae = -scores["test_MAE"].mean()
                rmse = -scores["test_RMSE"].mean()
                r2 = scores["test_R2"].mean()

                results.append({
                    "renderedObject": rendered_object,
                    "object_rows": object_row_count,
                    "feature_set": feature_set_name,
                    "model": model_name,
                    "num_features": len(selected_features),
                    "features": ", ".join(selected_features),
                    "MAE": mae,
                    "RMSE": rmse,
                    "R2": r2,
                })

                print(f"  MAE:  {mae:.4f}")
                print(f"  RMSE: {rmse:.4f}")
                print(f"  R2:   {r2:.4f}")

    # =========================
    # 7. Save detailed results
    # =========================

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by=["renderedObject", "MAE", "RMSE"],
        ascending=[True, True, True],
    )

    Path(WRITE_PATH).parent.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(WRITE_PATH, index=False)

    print()
    print("Detailed per-object results:")
    print(results_df)
    print()
    print(f"Saved detailed results to {WRITE_PATH}")

    # =========================
    # 8. Save best model per renderedObject
    # =========================

    best_per_object_df = (
        results_df
        .sort_values(
            by=["renderedObject", "MAE", "RMSE"],
            ascending=[True, True, True],
        )
        .groupby("renderedObject", as_index=False)
        .first()
    )

    best_per_object_df.to_csv(SUMMARY_WRITE_PATH, index=False)

    print()
    print("Best model per renderedObject:")
    print(
        best_per_object_df[
            [
                "renderedObject",
                "object_rows",
                "feature_set",
                "model",
                "MAE",
                "RMSE",
                "R2",
            ]
        ]
    )
    print()
    print(f"Saved summary to {SUMMARY_WRITE_PATH}")
