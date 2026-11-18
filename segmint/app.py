import os
import joblib
import pandas as pd
from flask import Flask, jsonify, request, render_template, Response

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))

# Exact feature order used to train the model in the notebook
FEATS = ['Age', 'Income', 'Recency', 'NumDealsPurchases', 'NumWebVisitsMonth',
         'Total_Spending', 'Total_Purchases', 'Total_Children',
         'Total_Campaign_Accepted', 'Customer_Tenure_Days',
         'Education_Level', 'Is_Partner']

# Segment text comes from the "Customer Segments - Summary" section of the notebook
SEG = [
    dict(name='Budget-Conscious Families', icon='🛍️',
         blurb='Price-sensitive shoppers who look for value.',
         insight='Low income and low spend. They browse the website often but rarely buy.',
         strategy='Use low-cost channels (email, web). Promote family essentials and targeted web offers.'),
    dict(name='Value-Seeking Established Families', icon='👨‍👩‍👧',
         blurb='Families who balance quality and price.',
         insight='Deal-driven parents and the longest-standing customers. Most potential to grow.',
         strategy='Offer discounts, bundles and loyalty rewards, mainly through the website.'),
    dict(name='Affluent Premium Buyers', icon='💎',
         blurb='High-value customers who prefer premium products.',
         insight='High income, high spend, few children. Most responsive to campaigns.',
         strategy='Focus on retention: premium programmes, personalised catalogue offers, early access.'),
]

try:
    model = joblib.load(os.path.join(BASE, 'customer_segmentation_model.pkl'))

    csv_path = os.path.join(BASE, 'customers_with_segments.csv')
    xls_path = os.path.join(BASE, 'customers_with_segments.xls')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    elif os.path.exists(xls_path):
        # The existing file is CSV-formatted despite having a .xls extension.
        df = pd.read_csv(xls_path)
    else:
        raise FileNotFoundError('customers_with_segments.csv')

    LOAD_ERROR = None
except Exception as e:  # missing files / version mismatch
    model, df, LOAD_ERROR = None, None, str(e)


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/summary')
def summary():
    if LOAD_ERROR:
        return jsonify(error=LOAD_ERROR), 500
    total = df.Total_Spending.sum()
    segs = []
    for c in range(3):
        d = df[df.Cluster == c]
        segs.append(dict(id=c, customers=len(d), share=round(len(d) / len(df) * 100),
                         income=round(d.Income.mean()), spend=round(d.Total_Spending.mean()),
                         purchases=round(d.Total_Purchases.mean(), 1),
                         deals=round(d.NumDealsPurchases.mean(), 1),
                         web_visits=round(d.NumWebVisitsMonth.mean(), 1),
                         campaigns=round(d.Total_Campaign_Accepted.mean(), 1),
                         age=round(d.Age.mean(), 1),
                         recency=round(d.Recency.mean(), 1),
                         tenure=round(d.Customer_Tenure_Days.mean()),
                         children=round(d.Total_Children.mean(), 1),
                         spend_share=round(d.Total_Spending.sum() / total * 100), **SEG[c]))
    pts = df.sample(min(450, len(df)), random_state=1)[['Income', 'Total_Spending', 'Cluster']]
    largest = max(segs, key=lambda s: s['customers'])
    top_spender = max(segs, key=lambda s: s['spend_share'])
    return jsonify(customers=len(df), income=round(df.Income.mean()),
                   total_spending=round(total), avg_age=round(df.Age.mean(), 1),
                   avg_purchases=round(df.Total_Purchases.mean(), 1),
                   largest_segment=largest['name'], largest_segment_share=largest['share'],
                   top_spending_segment=top_spender['name'], top_spending_share=top_spender['spend_share'],
                   segments=segs, points=pts.values.tolist())


@app.post('/api/predict')
def predict():
    if LOAD_ERROR:
        return jsonify(error=LOAD_ERROR), 500
    d = request.get_json(silent=True) or {}
    try:
        x = pd.DataFrame([[float(d[f]) for f in FEATS]], columns=FEATS)
    except (KeyError, ValueError, TypeError):
        return jsonify(error='Please fill every field with a number.'), 400
    c = int(model.predict(x)[0])
    return jsonify(segment=c, **SEG[c])


@app.get('/api/report')
def report():
    if LOAD_ERROR:
        return jsonify(error=LOAD_ERROR), 500
    columns = ['Age', 'Income', 'Recency', 'NumDealsPurchases', 'NumWebVisitsMonth',
               'Total_Spending', 'Total_Purchases', 'Total_Children',
               'Total_Campaign_Accepted', 'Customer_Tenure_Days',
               'Education_Level', 'Is_Partner', 'Cluster', 'Segment']
    available = [column for column in columns if column in df.columns]
    csv_data = df[available].to_csv(index=False)
    return Response(csv_data, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=segmint_customer_report.csv'})


if __name__ == '__main__':
    app.run(debug=True)
