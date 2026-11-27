
# 🚀 Segmint – Customer Segmentation Dashboard

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=36BCF7&center=true&vCenter=true&width=600&lines=Customer+Segmentation+Dashboard;Machine+Learning+Project;Understand+Customers+Better" alt="Segmint" />
</p>

<p align="center">
  An interactive Machine Learning dashboard for customer segmentation, behavioral analysis, and customer group prediction.
</p>

<p align="center">
  <a href="https://3pw3xiyxwchnjhdvuvburu.streamlit.app/">
    <img src="https://img.shields.io/badge/Live%20Demo-Open%20Website-brightgreen?style=for-the-badge&logo=streamlit" />
  </a>
</p>

---

## 🌐 Live Application

**Explore the deployed application here:**

👉 [Open Segmint – Customer Segmentation Dashboard](https://3pw3xiyxwchnjhdvuvburu.streamlit.app/)

---

## 📖 About The Project

**Segmint** is a Customer Segmentation Dashboard developed using Python, Machine Learning, and Streamlit.

The project helps businesses understand customer behavior by grouping customers into different segments based on their purchasing patterns, income, spending habits, and other characteristics.

The dashboard provides interactive visualizations, customer insights, individual customer predictions, and batch predictions through CSV uploads.

The project also includes a Flask application with a dashboard interface and prediction API.

---

## 🎯 Project Objectives

- Analyze customer purchasing behavior.
- Identify meaningful customer groups.
- Understand income and spending patterns.
- Predict customer segments using a trained Machine Learning model.
- Provide useful insights for customer-focused business decisions.
- Support predictions for individual customers and uploaded datasets.

---

## ✨ Key Features

### 1. 📊 Overview Dashboard

- Total customer count.
- Income and purchase summaries.
- Customer segment distribution.
- Customer share percentages.
- Segment profile cards.

### 2. 👥 Customer Segments

- Compare different customer groups.
- Analyze average income and spending.
- Review segment-level recommendations.
- Understand customer characteristics.

### 3. 📈 Insights & Analytics

- Spending versus income visualization.
- Normalized segment profile comparisons.
- Interactive metric charts.
- Important customer insights.

### 4. 🔍 New Customer Prediction

- Enter individual customer details.
- Submit customer feature values.
- Predict the customer's segment.
- Display the predicted customer group.

### 5. 📂 Upload Customer Dataset

- Upload customer datasets in CSV format.
- Validate required input columns.
- Predict customer segments in bulk.
- Preview prediction results.
- Download the complete dataset with predictions.

---

## 👨‍👩‍👧 Customer Segments

The trained Machine Learning model produces three cluster IDs, which are displayed using the following descriptive names:

| Cluster | Segment Name |
|---|---|
| Cluster 0 | Budget-Conscious Families |
| Cluster 1 | Value-Seeking Established Families |
| Cluster 2 | Affluent Premium Buyers |

*Note: Cluster IDs are model outputs. Segment names and recommendations are descriptive interpretations, not independently validated business classifications.*

---

## 🛠️ Technologies Used

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,mysql,html,css,git,github,vscode" />
</p>

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Interactive dashboard |
| Flask | Web application and prediction API |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Scikit-learn | Machine Learning and clustering |
| Matplotlib | Data visualization |
| Joblib / Pickle | Model artifact loading |

---

## 📸 Project Screenshots

Add your actual screenshots in the `screenshots` folder and use the following image paths.

### Dashboard Overview

![Segmint Dashboard](./screenshots/Screenshot(406).png)

### Customer Segments

![Customer Segments](./screenshots/segments.png)

### Insights & Analytics

![Customer Insights](./screenshots/insights.png)

### New Customer Prediction

![New Customer Prediction](./screenshots/new-customer.png)

### Upload Customer Dataset

![Upload Dataset](./screenshots/upload-dataset.png)

---

## 📁 Project Structure

```text
Segmint/
│
├── segmint/
│   ├── streamlit_app.py
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   ├── customer_segmentation_model.pkl
│   ├── customers_with_segments.csv
│   └── requirements.txt
│
├── screenshots/
│   ├── overview.png
│   ├── segments.png
│   ├── insights.png
│   ├── new-customer.png
│   └── upload-dataset.png
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10 or later.
- VS Code or another Python editor.
- Git.
- Required model and customer data files.

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

```bash
cd Segmint
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install -r requirements.txt
```

### Step 5: Run Streamlit Application

```bash
python -m streamlit run segmint/streamlit_app.py
```

Open the following URL in your browser:

```text
http://localhost:8501
```

---

## 📤 Upload Customer Dataset

The application supports uploading customer data in CSV format.

The uploaded CSV must contain the following 12 numeric feature columns:

| Column | Description |
|---|---|
| Age | Customer age |
| Income | Annual income |
| Recency | Days since last purchase |
| NumDealsPurchases | Number of discount purchases |
| NumWebVisitsMonth | Website visits per month |
| Total_Spending | Total customer spending |
| Total_Purchases | Total purchases |
| Total_Children | Children at home |
| Total_Campaign_Accepted | Accepted campaign count |
| Customer_Tenure_Days | Customer tenure in days |
| Education_Level | Encoded education category |
| Is_Partner | Partner status |

The application:

1. Validates the uploaded dataset.
2. Checks the required feature columns.
3. Predicts customer clusters using the saved model.
4. Displays prediction results.
5. Provides a downloadable CSV containing predicted clusters and segment names.

**Important:** The uploaded dataset does not retrain the model. It uses the existing trained model to predict customer segments.

---

## 🚀 Deployment

The Streamlit application is deployed using **Streamlit Community Cloud**.

**Live Application:**

👉 https://3pw3xiyxwchnjhdvuvburu.streamlit.app/

To deploy your own version:

1. Push the project repository to GitHub.
2. Open Streamlit Community Cloud.
3. Connect your GitHub account.
4. Select your repository.
5. Set the main file path to:

```text
segmint/streamlit_app.py
```

6. Deploy the application.

Ensure that the required model and customer data files are available to the deployed application.

---

## 🔒 Model & Data Security

The project loads a trained model using Joblib/Pickle.

- Only load trusted model files.
- Keep the scikit-learn version compatible with the saved model.
- The root `requirements.txt` pins scikit-learn to version `1.7.2`.
- Do not upload sensitive customer information to a public repository.

---

## 🔧 Troubleshooting

**1. Model file not found**

Check whether `customer_segmentation_model.pkl` exists inside the `segmint/` directory.

**2. Missing dependencies**

Run:

```bash
pip install -r requirements.txt
```

**3. Missing CSV columns**

Use the CSV template provided in the application and ensure all required column names match exactly.

**4. Invalid customer values**

Check for missing, non-numeric, or infinite feature values.

**5. Model version compatibility**

Use scikit-learn version `1.7.2`, as specified in the root requirements file.

---

## 🔮 Future Enhancements

- Add advanced customer behavior analytics.
- Improve dashboard visualization.
- Add customer-specific recommendations.
- Explore additional clustering algorithms.
- Enhance model evaluation and segment validation.
- Improve deployment and data management.

---

## 👩‍💻 Developed By

**Komal Gulve**

Computer Engineering | Python | Machine Learning | Data Science

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ Star!

<p align="center">
  <b>Thank you for visiting Segmint!</b>
  <br/>
  Turning Customer Data into Meaningful Insights 🚀
</p>
