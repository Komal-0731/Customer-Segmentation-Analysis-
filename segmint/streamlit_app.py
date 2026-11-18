import os
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Customer Segmentation", page_icon="◆", layout="wide")

BASE = os.path.dirname(os.path.abspath(__file__))
FEATS = ['Age', 'Income', 'Recency', 'NumDealsPurchases', 'NumWebVisitsMonth',
         'Total_Spending', 'Total_Purchases', 'Total_Children',
         'Total_Campaign_Accepted', 'Customer_Tenure_Days',
         'Education_Level', 'Is_Partner']

SEG = [
    dict(name='Budget-Conscious Families', icon='🛍️', blurb='Price-sensitive shoppers who look for value.',
         insight='Low income and low spend. They browse the website often but rarely buy.',
         strategy='Use low-cost channels (email, web). Promote family essentials and targeted web offers.'),
    dict(name='Value-Seeking Established Families', icon='👨‍👩‍👧', blurb='Families who balance quality and price.',
         insight='Deal-driven parents and the longest-standing customers. Most potential to grow.',
         strategy='Offer discounts, bundles and loyalty rewards, mainly through the website.'),
    dict(name='Affluent Premium Buyers', icon='💎', blurb='High-value customers who prefer premium products.',
         insight='High income, high spend, few children. Most responsive to campaigns.',
         strategy='Focus on retention: premium programmes, personalised catalogue offers, early access.'),
]

PLOT_LAYOUT = dict(paper_bgcolor='white', plot_bgcolor='white', font=dict(family='Inter, sans-serif', color='#0f2a3d'),
                   margin=dict(l=40, r=20, t=35, b=40), legend=dict(orientation='h', y=-0.18))

@st.cache_resource
def load_model():
    return joblib.load(os.path.join(BASE, 'customer_segmentation_model.pkl'))

@st.cache_data
def load_data():
    csv_path = os.path.join(BASE, 'customers_with_segments.csv')
    xls_path = os.path.join(BASE, 'customers_with_segments.xls')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    if os.path.exists(xls_path):
        return pd.read_csv(xls_path)
    raise FileNotFoundError('customers_with_segments.csv or .xls was not found')

try:
    model = load_model()
    df = load_data()
except Exception as exc:
    st.error(f'Model files could not be loaded: {exc}')
    st.stop()

segment_colors = ['#2fc4b2', '#1e3f73', '#a78bfa']
df['Segment Name'] = df['Cluster'].map(lambda c: SEG[int(c)]['name'])

with st.sidebar:
    st.title('◆ Customer Segmentation')
    page = st.radio('Navigation', ['Overview', 'Segments', 'Insights', 'New Customer'], label_visibility='collapsed')
    st.divider()
    st.caption('Komal Gulve')
    st.caption('Data Scientist')

if page == 'Overview':
    st.title('Customer Segmentation')
    st.caption('Understand your customers better with data-driven insights.')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Customers', f'{len(df):,}')
    col2.metric('Segments', 3)
    col3.metric('Avg. Annual Income', f'${df.Income.mean()/1000:.1f}K')
    col4.metric('Avg. Purchases', f'{df.Total_Purchases.mean():.1f}')

    counts = df['Segment Name'].value_counts()
    largest = counts.index[0]
    spending = df.groupby('Segment Name')['Total_Spending'].sum()
    top_spender = spending.idxmax()

    st.info(f"**Executive Summary:** {largest} is the largest segment at **{counts.iloc[0]/len(df)*100:.0f}%**. "
            f"{top_spender} contributes **{spending[top_spender]/spending.sum()*100:.0f}%** of total spending. "
            f"The portfolio has **{len(df):,}** customers with average annual income of **${df.Income.mean()/1000:.1f}K** and average age of **{df.Age.mean():.1f}**.")

    left, right = st.columns([1.3, 1])
    with left:
        dist = df['Cluster'].value_counts().sort_index().reset_index()
        dist.columns = ['Cluster', 'Customers']
        fig = px.bar(dist, x='Cluster', y='Customers', color='Cluster', text='Customers',
                     color_discrete_sequence=segment_colors)
        fig.update_layout(showlegend=False, xaxis_title='Segment', yaxis_title='Customers', **PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.pie(dist, names='Cluster', values='Customers', hole=.65,
                     color='Cluster', color_discrete_sequence=segment_colors)
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Customer Segment Profiles')
    cols = st.columns(3)
    for i, col in enumerate(cols):
        segment = SEG[i]
        share = len(df[df.Cluster == i]) / len(df) * 100
        col.markdown(f"### {segment['icon']}  Segment {i}\n**{segment['name']}**\n\n{share:.0f}% of customers\n\n{segment['blurb']}")

elif page == 'Segments':
    st.title('Customer Segments')
    st.caption('Explore and compare your customer groups.')

    all_segments = ['All segments'] + [s['name'] for s in SEG]
    selected_segment = st.selectbox('Filter by segment', all_segments)
    filtered = df if selected_segment == 'All segments' else df[df['Segment Name'] == selected_segment]

    cols = st.columns(3)
    for i, col in enumerate(cols):
        segment = SEG[i]
        segment_df = filtered[filtered.Cluster == i]
        if len(segment_df) == 0:
            continue
        col.metric(f"{segment['icon']} Segment {i}", len(segment_df))
        col.markdown(f"**{segment['name']}**\n\n{segment['blurb']}")

    rows = []
    for i, segment in enumerate(SEG):
        d = df[df.Cluster == i]
        rows.append({'Segment': f"{i} - {segment['name']}", 'Customers': len(d),
                     'Avg. Income': d.Income.mean(), 'Avg. Spend': d.Total_Spending.mean(),
                     'Share of Spend': d.Total_Spending.sum()/df.Total_Spending.sum()*100,
                     'Key Insight': segment['strategy']})
    comparison = pd.DataFrame(rows)
    st.subheader('Segment Comparison')
    st.dataframe(comparison, use_container_width=True, hide_index=True)

elif page == 'Insights':
    st.title('Insights & Analytics')
    st.caption('Discover key insights and get data-driven recommendations.')

    left, right = st.columns(2)
    with left:
        sample = df.sample(min(450, len(df)), random_state=1)
        fig = px.scatter(sample, x='Income', y='Total_Spending', color='Cluster',
                         color_discrete_sequence=segment_colors,
                         labels={'Income':'Annual Income ($)', 'Total_Spending':'Total Spending ($)'})

        fig.update_layout(showlegend=True, **PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        metrics = ['Income', 'Total_Purchases', 'Total_Campaign_Accepted', 'NumWebVisitsMonth', 'Customer_Tenure_Days']
        labels = ['Income', 'Purchases', 'Campaigns', 'Web Visits', 'Tenure']
        averages = df.groupby('Cluster')[metrics].mean()
        fig = go.Figure()
        for i in range(3):
            values = []
            for metric in metrics:
                column = averages[metric]
                values.append((averages.loc[i, metric] - column.min()) / (column.max() - column.min()) if column.max() != column.min() else 0)
            fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]],
                                          fill='toself', name=f'Segment {i}',
                                          line_color=segment_colors[i]))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    chart_metrics = [('Income', 'Average Annual Income'), ('Total_Purchases', 'Purchases per Customer'),
                     ('Total_Campaign_Accepted', 'Campaign Acceptance'), ('NumWebVisitsMonth', 'Web Visits per Month'),
                     ('NumDealsPurchases', 'Deal Purchases'), ('Recency', 'Customer Recency')]
    chart_cols = st.columns(3)
    for idx, (metric, title) in enumerate(chart_metrics):
        summary = df.groupby('Cluster')[metric].mean().reset_index()
        fig = px.bar(summary, x='Cluster', y=metric, color='Cluster', text_auto='.1f',
                     color_discrete_sequence=segment_colors)
        fig.update_layout(showlegend=False, xaxis_title='Segment', yaxis_title=title, **PLOT_LAYOUT)
        chart_cols[idx % 3].plotly_chart(fig, use_container_width=True)

    st.subheader('Key Insights')
    insight_cols = st.columns(3)
    for i, col in enumerate(insight_cols):
        segment = SEG[i]
        d = df[df.Cluster == i]
        col.markdown(f"**Segment {i} ({len(d)/len(df)*100:.0f}%)**\n\n{segment['insight']}\n\nGenerates {d.Total_Spending.sum()/df.Total_Spending.sum()*100:.0f}% of total spend.")

else:
    st.title('Segment a Customer')
    st.caption('Enter customer details to find their segment.')

    col1, col2 = st.columns(2)
    values = {}
    fields = [
        ('Age', 'Age', 45), ('Income', 'Annual Income ($)', 52000),
        ('Recency', 'Days since last purchase', 49), ('NumDealsPurchases', 'Discount purchases', 2),
        ('NumWebVisitsMonth', 'Web visits / month', 5), ('Total_Spending', 'Total spending (2 yrs)', 600),
        ('Total_Purchases', 'Total purchases', 14), ('Total_Children', 'Children at home', 1),
        ('Total_Campaign_Accepted', 'Campaigns accepted', 0), ('Customer_Tenure_Days', 'Days as customer', 350),
    ]
    for i, (key, label, default) in enumerate(fields):
        target = col1 if i % 2 == 0 else col2
        values[key] = target.number_input(label, min_value=0, value=default)

    values['Education_Level'] = col1.selectbox('Education', [0, 1, 2], format_func=lambda x: ['Basic','Graduate','Postgraduate'][x])
    values['Is_Partner'] = col2.selectbox('Living with partner', [0, 1], format_func=lambda x: ['No','Yes'][x])

    if st.button('Find Segment', use_container_width=True):
        try:
            x = pd.DataFrame([[float(values[f]) for f in FEATS]], columns=FEATS)
            cluster = int(model.predict(x)[0])
            segment = SEG[cluster]
            st.success(f"### {segment['icon']} Assigned Segment {cluster}: {segment['name']}")
            st.markdown(f"**Key Insight:** {segment['insight']}\n\n**Recommended Strategy:** {segment['strategy']}")
        except Exception as exc:
            st.error(f'Prediction failed: {exc}')

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: #f2f7f9;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #0b2a3f, #0f4457 60%, #0b2a3f);}
[data-testid="stSidebar"] * {color: #e8f3f6 !important;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding: 8px 10px; border-radius: 8px;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background: #16b5a8;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {color: white !important;}
[data-testid="stSidebar"] hr {border-color: rgba(255,255,255,.12);}
[data-testid="stMain"] .block-container {padding-top: 2rem; max-width: 1100px;}
[data-testid="stMetric"] {background: white; border-radius: 12px; padding: 16px; box-shadow: 0 1px 6px rgba(11,42,63,.08);}
[data-testid="stMetric"] label, [data-testid="stMetric"] [data-testid="stMetricDelta"] {color: #5d7384 !important;}
[data-testid="stMetric"] [data-testid="stMetricValue"] {color: #0f2a3d !important;}
[data-testid="stAlert"] {background: white; border: 1px solid #dfe8ed; color: #0f2a3d; border-radius: 12px;}
[data-testid="stDataFrame"] {border-radius: 12px; overflow: hidden;}
button[kind="primary"] {background: #16b5a8; border: none; border-radius: 8px;}
[data-testid="stSidebarCollapseButton"] {color: white !important;}
#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.divider()
st.caption('Data note: Insights are descriptive and should be validated before operational use.')
