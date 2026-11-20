# Segmint

Segmint is a customer segmentation dashboard for exploring customer groups, reviewing segment-level behavior, and assigning segments to individual customers or uploaded customer datasets. The primary interface is built with Streamlit. A Flask application is also included.

## Features

- **Overview:** customer totals, income and purchase summaries, segment counts, customer shares, and segment profile cards.
- **Segments:** compare customer groups and review their average income, spending, and segment recommendations.
- **Insights:** explore spending versus income, compare normalized segment profiles, and review metric charts and key insights.
- **New Customer:** enter one customer's feature values and predict a segment.
- **Upload Dataset:** upload a CSV of customers, validate its required features, predict segments in a batch, and download the results.

The dashboard uses three model cluster IDs. Their displayed names are Budget-Conscious Families, Value-Seeking Established Families, and Affluent Premium Buyers. Cluster IDs are model outputs; segment descriptions and recommendations are descriptive guidance and should be validated before operational use.

## Requirements

- Python 3.10 or later is recommended.
- Install the root `requirements.txt` for the Streamlit app. It pins scikit-learn to `1.7.2`, the version used to save the model artifact.
- Keep `customer_segmentation_model.pkl` from a trusted source. Joblib/pickle model files can execute code when loaded; do not load untrusted files.

## Run the Streamlit app

From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run segmint/streamlit_app.py
```

Open `http://localhost:8501` in a browser. Stop the local server with `Ctrl+C` in the terminal.

The app expects these files inside the `segmint/` directory:

- `customer_segmentation_model.pkl` - trained segmentation pipeline.
- `customers_with_segments.csv` - dashboard data, or `customers_with_segments.xls` containing CSV-formatted text as a fallback.

The `.xls` fallback is read with `pandas.read_csv`; it must contain CSV text, not a binary Excel workbook. Prefer the `.csv` filename.

## Upload a customer dataset

Choose **Upload Dataset** in the sidebar. The upload must be a CSV with one row per customer and all of the following numeric columns:

| Column | Meaning |
| --- | --- |
| `Age` | Customer age in years |
| `Income` | Annual income |
| `Recency` | Days since last purchase |
| `NumDealsPurchases` | Number of discount purchases |
| `NumWebVisitsMonth` | Website visits per month |
| `Total_Spending` | Total customer spending |
| `Total_Purchases` | Total purchases |
| `Total_Children` | Children at home |
| `Total_Campaign_Accepted` | Accepted campaign count |
| `Customer_Tenure_Days` | Days as a customer |
| `Education_Level` | Encoded education category: `0` Basic, `1` Graduate, `2` Postgraduate |
| `Is_Partner` | Partner status: `0` No, `1` Yes |

Use the **Download CSV template** button in the app to get a header-only template. Required values must be numeric and cannot be blank or infinite. Additional input columns are preserved in the downloaded output. The result adds `Predicted Cluster` and `Predicted Segment` columns. The preview shows up to the first 100 rows; the download contains the full uploaded dataset with predictions.

The uploader assigns new customers using the existing saved model. It does not retrain the model or redefine segment groups. To use different features or redefine the segments, retrain and save a compatible model and update the app's feature schema and segment descriptions.

## Run the Flask app

The Flask app has a separate dependency file that includes Flask and Gunicorn. From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r segmint/requirements.txt
python segmint/app.py
```

Open `http://127.0.0.1:5000`. The Flask app also expects the model and customer data files inside `segmint/`. Its `/api/predict` endpoint accepts JSON containing the same 12 feature fields listed above.

## Deploy on Streamlit Community Cloud

1. Push the repository to GitHub, including the root `requirements.txt` and the required model/data artifacts in `segmint/`.
2. Create a Streamlit Community Cloud app from the repository.
3. Set the main file path to `segmint/streamlit_app.py`.
4. Deploy and open the URL provided by Streamlit.

Keep the model and data files available to the deployed app. If deployment rejects large artifacts, store them in an appropriate artifact service and update the app's loading configuration.

## Troubleshooting

- **Model or data file not found:** verify that the expected files are present in `segmint/` and that their names match the paths above.
- **Model loading or scikit-learn warning:** install dependencies from the root `requirements.txt` so scikit-learn matches the model's saved version (`1.7.2`). Models saved with a different scikit-learn version may fail or produce unreliable results.
- **Upload reports missing columns:** use the built-in CSV template and keep the required column names exactly as listed.
- **Upload reports invalid values:** check the reported columns and CSV row numbers for blank or non-numeric feature values.
- **Excel upload:** the batch uploader currently accepts CSV files only. Export Excel data to CSV before uploading.

## Project files

- `segmint/streamlit_app.py` - primary Streamlit dashboard and batch upload workflow.
- `segmint/app.py` - Flask dashboard and JSON API.
- `segmint/templates/index.html` - Flask dashboard interface.
- `segmint/customer_segmentation_model.pkl` - trained model artifact required by both apps.
- `segmint/customers_with_segments.xls` - bundled customer data; this file is CSV-formatted text and is loaded with `pandas.read_csv`. You may replace it with a real `.csv` file named `customers_with_segments.csv`.
- `requirements.txt` - Streamlit app dependencies, including the model's scikit-learn version pin.
- `segmint/requirements.txt` - dependencies for running the Flask app.
