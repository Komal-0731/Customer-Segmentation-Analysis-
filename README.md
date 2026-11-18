# Segmint

A customer segmentation dashboard built with Streamlit and Flask.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run segmint/streamlit_app.py
```

Open `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open https://share.streamlit.io.
3. Select the repository.
4. Set the main file path to `segmint/streamlit_app.py`.
5. Deploy.

## Files

- `segmint/streamlit_app.py` - Streamlit dashboard
- `segmint/app.py` - Flask dashboard
- `segmint/customer_segmentation_model.pkl` - trained segmentation model
- `segmint/customers_with_segments.xls` - customer data
