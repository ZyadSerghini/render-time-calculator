# Render Time Calculator

This project has been made as an Honors Assignment for the BAI 3301 Introduction to Business Analytics with professor Hayat El Asri. 

It uses machine learning to estimate the render time of 3D benchmark scenes based on GPU specifications and rendering backend information.

The GPU specification data used in this project comes from the [RightNow GPU Database](https://github.com/RightNow-AI/RightNow-GPU-Database).  
The Blender benchmark render data comes from [Blender Open Data](https://opendata.blender.org/).

## Dataset

The dataset is based on Blender benchmark-style render data.  
The original Blender benchmark file and the cleaned dataset are not included in this repository because they are too large.

The raw benchmark file should be placed in:

```text
data/raw/
````

The cleaned dataset produced by the project is:

```text
data/processed/cleaned_data.csv
```

The target variable is:

* `renderTime`

The main features used are:

* `gpuBackend`
* `baseClock`
* `boostClock`
* `textureRate`
* `pixelRate`
* `architecture`
* `memoryType`
* `generation`
* `busInterface`
* `rtCores`
* `tensorCores`

The `gpuName` feature was excluded to reduce memorization of specific GPU names.
The `releaseYear` feature was removed from the final experiment.

## Method

The final approach trains a separate model for each `renderedObject`.

For each rendered object, the project compares:

* Dummy median baseline
* Ridge Regression with log-transformed target
* Random Forest with log-transformed target
* Histogram Gradient Boosting with log-transformed target

The target variable is transformed using `log1p(renderTime)` because render times contain extreme outliers.

## Results

The best model per object was selected using 3-fold cross-validation.

Example final results:

| Rendered Object     | Best Model               |    MAE |    RMSE |    R² |
| ------------------- | ------------------------ | -----: | ------: | ----: |
| barbershop_interior | Random Forest Log Target | 969.68 | 2739.68 | 0.665 |
| bmw27               | Random Forest Log Target |  11.96 |   96.10 | 0.685 |
| classroom           | Random Forest Log Target |   8.63 |   91.28 | 0.344 |
| fishy_cat           | Random Forest Log Target |  55.60 |  407.52 | 0.603 |
| koro                | Random Forest Log Target |  56.60 |  174.31 | 0.824 |

Some objects performed poorly because the dataset contains extreme render time outliers.

## Interpretation of the Output

The results show that the Random Forest model with a log-transformed target performed best for most rendered objects. This suggests that render time is not purely linear and depends on more complex relationships between GPU specifications, rendering backend, and scene type. The MAE values are more useful than the RMSE values in this project because the dataset contains very large outliers. A few extremely high render times cause RMSE to become much larger, even when the average prediction error is more reasonable. Overall, the model is able to learn some useful patterns, but the prediction quality varies significantly depending on the rendered object.

## Suggestions for Further Improvement

The model could be improved by removing or capping extreme render time outliers, adding more detailed GPU and system information, and tuning the model hyperparameters more carefully. Another improvement would be to save the best trained model for each rendered object and create a prediction script that allows a user to input GPU specifications and receive an estimated render time. The project could also compare results with and without `gpuName` to see how much accuracy is gained by allowing the model to recognize specific GPUs.

## How to Run

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Place the Blender benchmark JSONL file in:

```text
data/raw/
```

The file must match this pattern:

```text
opendata-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}+[0-9]{4}.jsonl
```

Run the full pipeline:

```bash
python -m render_time_calculator.main all
```

To only process the raw benchmark file into a cleaned CSV:

```bash
python -m render_time_calculator.main benchmark
```

To only run the model comparison after `cleaned_data.csv` already exists:

```bash
python -m render_time_calculator.main models
```

The output files are saved to:

```text
data/processed/models/
```

## Limitations

This project is intended as a class machine learning experiment, not as a production-grade render time predictor. The dataset contains extreme render time outliers, and the model does not include every possible factor that affects rendering performance, such as CPU, RAM, driver version, operating system, Blender version, cooling, power limits, or background system load.
