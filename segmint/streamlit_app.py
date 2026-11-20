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

def render_page_header(title, subtitle):
    st.markdown(
        f'<div class="page-header"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

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

def predict_uploaded_dataset(uploaded_file):
    data = pd.read_csv(uploaded_file)
    if data.empty:
        raise ValueError('The uploaded CSV has no customer rows.')

    missing = [feature for feature in FEATS if feature not in data.columns]
    if missing:
        raise ValueError(f'Missing required columns: {", ".join(missing)}')

    features = data[FEATS].apply(pd.to_numeric, errors='coerce')
    features = features.replace([float('inf'), float('-inf')], float('nan'))
    invalid = features.isna()
    if invalid.any().any():
        bad_columns = [f'{column} ({int(invalid[column].sum())} invalid)' for column in FEATS if invalid[column].any()]
        bad_rows = (invalid.any(axis=1).to_numpy().nonzero()[0][:5] + 2).tolist()
        raise ValueError(f'Invalid or blank values in {", ".join(bad_columns)}. Check CSV rows {bad_rows}.')

    clusters = model.predict(features)
    if any(int(cluster) < 0 or int(cluster) >= len(SEG) for cluster in clusters):
        raise ValueError('The model returned an unknown segment number.')

    data['Predicted Cluster'] = clusters.astype(int)
    data['Predicted Segment'] = data['Predicted Cluster'].map(lambda cluster: SEG[cluster]['name'])
    return data

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
    page = st.radio('Navigation', ['Overview', 'Segments', 'Insights', 'New Customer', 'Upload Dataset'], label_visibility='collapsed')
    st.divider()

if page == 'Overview':
    render_page_header('Customer Segmentation', 'Understand your customers better with data-driven insights.')

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

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('#### Customer Count by Segment')
            dist = df['Cluster'].value_counts().sort_index().reset_index()
            dist.columns = ['Cluster', 'Customers']
            dist['Segment Name'] = dist['Cluster'].map(lambda cluster: SEG[int(cluster)]['name'])
            segment_order = [segment['name'] for segment in SEG]
            segment_color_map = {segment['name']: segment_colors[index] for index, segment in enumerate(SEG)}
            wrapped_names = ['Budget-Conscious<br>Families', 'Value-Seeking<br>Established Families',
                             'Affluent Premium<br>Buyers']
            label_map = dict(zip(segment_order, wrapped_names))
            dist['Segment Label'] = dist['Segment Name'].map(label_map)
            fig = px.bar(dist, x='Segment Label', y='Customers', color='Segment Name', text='Customers',
                         custom_data=['Segment Name'], color_discrete_map=segment_color_map,
                         category_orders={'Segment Label': wrapped_names})
            fig.update_traces(
                textposition='outside',
                cliponaxis=False,
                hovertemplate='%{customdata[0]}<br>Customers: %{y:,}<extra></extra>',
            )
            fig.update_xaxes(title='', tickangle=0, automargin=True, tickfont=dict(size=10))
            fig.update_yaxes(title='Customers', automargin=True, rangemode='tozero')
            fig.update_layout(showlegend=False, height=400, **PLOT_LAYOUT)
            fig.update_layout(margin=dict(l=40, r=20, t=35, b=75))
            st.plotly_chart(fig, use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown('#### Customer Share by Segment')
            fig = px.pie(dist, names='Segment Name', values='Customers', hole=.58,
                         color='Segment Name', color_discrete_map=segment_color_map,
                         category_orders={'Segment Name': segment_order})
            fig.update_traces(textinfo='percent', textposition='inside', insidetextorientation='horizontal')
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=16, b=100),
                legend=dict(orientation='h', yanchor='bottom', y=-0.22, xanchor='center', x=0.5,
                            font=dict(size=10)),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family='Inter, sans-serif', color='#0f2a3d'),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader('Customer Segment Profiles')
    cols = st.columns(3)
    for i, col in enumerate(cols):
        segment = SEG[i]
        customer_count = int((df.Cluster == i).sum())
        share = customer_count / len(df) * 100
        col.markdown(
            f"""
            <article class="segment-profile-card" style="--segment-color: {segment_colors[i]};">
                <div class="segment-profile-top">
                    <span class="segment-profile-icon">{segment['icon']}</span>
                    <span class="segment-profile-label">SEGMENT {i}</span>
                </div>
                <h3>{segment['name']}</h3>
                <div class="segment-profile-stats">
                    <strong>{customer_count:,}</strong>
                    <span>customers</span>
                    <b>{share:.0f}%</b>
                </div>
                <div class="segment-profile-track"><span style="width: {share:.1f}%;"></span></div>
                <p>{segment['blurb']}</p>
            </article>
            """,
            unsafe_allow_html=True,
        )

elif page == 'Segments':
    render_page_header('Customer Segments', 'Explore and compare your customer groups.')

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
    render_page_header('Insights & Analytics', 'Discover key insights and get data-driven recommendations.')

    segment_names = [segment['name'] for segment in SEG]
    segment_color_map = {segment['name']: segment_colors[index] for index, segment in enumerate(SEG)}
    segment_fill_colors = ['rgba(47,196,178,0.12)', 'rgba(30,63,115,0.12)', 'rgba(167,139,250,0.12)']

    st.subheader('Spending vs. Income by Segment')
    sample = df.sample(min(450, len(df)), random_state=1)
    fig = px.scatter(sample, x='Total_Spending', y='Income', color='Segment Name',
                     color_discrete_map=segment_color_map,
                     category_orders={'Segment Name': segment_names},
                     labels={'Total_Spending':'Total Spending ($)', 'Income':'Annual Income ($)'})
    fig.update_layout(
        height=470,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.22, xanchor='center', x=0.5,
                    font=dict(size=11)),
        margin=dict(l=60, r=25, t=20, b=100),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter, sans-serif', color='#0f2a3d'),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Customer Profiles by Segment')
    metrics = ['Income', 'Total_Purchases', 'Total_Campaign_Accepted', 'NumWebVisitsMonth', 'Customer_Tenure_Days']
    labels = ['Income', 'Purchases', 'Campaigns', 'Web Visits', 'Tenure']
    averages = df.groupby('Segment Name')[metrics].mean().reindex(segment_names)
    fig = go.Figure()
    for index in reversed(range(len(segment_names))):
        segment_name = segment_names[index]
        values = []
        for metric in metrics:
            column = averages[metric]
            metric_range = column.max() - column.min()
            values.append((averages.loc[segment_name, metric] - column.min()) / metric_range if metric_range else 0)
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            mode='lines+markers',
            fill='toself',
            fillcolor=segment_fill_colors[index],
            name=segment_name,
            legendrank=index,
            line=dict(color=segment_colors[index], width=3),
            marker=dict(color=segment_colors[index], size=7),
        ))
    fig.update_layout(
        height=560,
        polar=dict(
            domain=dict(x=[0.12, 0.88], y=[0.18, 0.96]),
            radialaxis=dict(visible=True, range=[0, 1]),
            angularaxis=dict(tickfont=dict(size=12)),
        ),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5,
                    font=dict(size=11)),
        margin=dict(l=75, r=75, t=25, b=105),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter, sans-serif', color='#0f2a3d'),
    )
    st.plotly_chart(fig, use_container_width=True)

    chart_metrics = [('Income', 'Average Annual Income'), ('Total_Purchases', 'Purchases per Customer'),
                     ('Total_Campaign_Accepted', 'Campaign Acceptance'), ('NumWebVisitsMonth', 'Web Visits per Month'),
                     ('NumDealsPurchases', 'Deal Purchases'), ('Recency', 'Customer Recency')]
    chart_cols = st.columns(2)
    wrapped_segment_names = ['Budget-Conscious<br>Families', 'Value-Seeking<br>Established Families',
                             'Affluent Premium<br>Buyers']
    segment_label_map = dict(zip(segment_names, wrapped_segment_names))
    for idx, (metric, title) in enumerate(chart_metrics):
        summary = df.groupby('Segment Name')[metric].mean().reindex(segment_names).rename_axis('Segment Name').reset_index()
        summary['Segment Label'] = summary['Segment Name'].map(segment_label_map)
        fig = px.bar(summary, x='Segment Label', y=metric, color='Segment Name', text_auto='.1f',
                     custom_data=['Segment Name'], color_discrete_map=segment_color_map,
                     category_orders={'Segment Label': wrapped_segment_names})
        fig.update_traces(
            textposition='outside',
            cliponaxis=False,
            hovertemplate=f'%{{customdata[0]}}<br>{title}: %{{y:,.1f}}<extra></extra>',
        )
        fig.update_xaxes(title='', tickangle=0, automargin=True, tickfont=dict(size=9))
        fig.update_yaxes(title=title, automargin=True, rangemode='tozero')
        fig.update_layout(
            height=340,
            showlegend=False,
            margin=dict(l=65, r=35, t=25, b=85),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Inter, sans-serif', color='#0f2a3d'),
        )
        chart_cols[idx % 2].plotly_chart(fig, use_container_width=True)

    st.subheader('Key Insights')
    insight_cols = st.columns(3)
    for i, col in enumerate(insight_cols):
        segment = SEG[i]
        d = df[df.Cluster == i]
        spend_share = d.Total_Spending.sum() / df.Total_Spending.sum() * 100
        col.markdown(
            f"""
            <article class="segment-insight-card" style="--segment-color: {segment_colors[i]};">
                <div class="segment-profile-top">
                    <span class="segment-profile-icon">{segment['icon']}</span>
                    <span class="segment-profile-label">SEGMENT {i} INSIGHT</span>
                </div>
                <h3>{segment['name']}</h3>
                <p class="segment-insight-copy">{segment['insight']}</p>
                <div class="segment-insight-spend">
                    <span>Share of total spend</span>
                    <strong>{spend_share:.0f}%</strong>
                </div>
            </article>
            """,
            unsafe_allow_html=True,
        )

elif page == 'Upload Dataset':
    st.markdown("""
    <style>
    [data-testid="stFileUploaderDropzone"] {
        background: var(--app-soft);
        border: 2px dashed var(--app-accent);
        border-radius: 8px;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        background: #d9f1ec;
        border-color: var(--app-accent-hover);
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--app-accent);
        border: 0;
        color: #ffffff;
    }
    [data-testid="stDownloadButton"] button {
        background: var(--app-accent);
        border: 0;
        color: #ffffff;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: var(--app-accent-hover);
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)
    render_page_header('Segment a Dataset', 'Upload a customer CSV to assign segments in one batch.')
    st.write(f'Required numeric columns: {", ".join(FEATS)}')
    st.caption('Use Education_Level values 0=Basic, 1=Graduate, 2=Postgraduate and Is_Partner values 0=No, 1=Yes.')

    template = pd.DataFrame(columns=FEATS)
    st.download_button('Download CSV template', template.to_csv(index=False), 'customer_features_template.csv', 'text/csv')
    uploaded_file = st.file_uploader('Choose a customer CSV', type=['csv'])

    if uploaded_file is not None:
        try:
            segmented = predict_uploaded_dataset(uploaded_file)
            st.success(f'Assigned segments to {len(segmented):,} customers.')

            counts = segmented['Predicted Segment'].value_counts()
            count_cols = st.columns(len(SEG))
            for index, segment in enumerate(SEG):
                count_cols[index].metric(segment['name'], int(counts.get(segment['name'], 0)))

            st.dataframe(segmented.head(100), use_container_width=True, hide_index=True)
            st.download_button(
                'Download segmented CSV',
                segmented.to_csv(index=False),
                'customers_with_predicted_segments.csv',
                'text/csv',
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f'Could not segment this dataset: {exc}')

elif page == 'New Customer':
    st.markdown("""
    <style>
    [data-testid="stNumberInput"] input {
        background: var(--app-soft);
    }
    [data-testid="stNumberInput"]:focus-within input,
    [data-testid="stSelectbox"]:focus-within [data-baseweb="select"] > div {
        border-color: var(--app-accent);
        box-shadow: 0 0 0 1px var(--app-accent);
    }
    [data-testid="stButton"] button {
        background: var(--app-accent);
        border: 0;
        color: #ffffff;
    }
    [data-testid="stButton"] button:hover {
        background: var(--app-accent-hover);
        border: 0;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)
    render_page_header('Segment a Customer', 'Enter customer details to find their segment.')

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
:root {--app-page-bg: #f2f7f9; --app-text: #0f2a3d; --app-muted: #5d7384; --app-deep: #0d2f45; --app-accent: #16b5a8; --app-accent-hover: #0b8d84; --app-soft: #e7f7f4; --app-border: #dfe8ed;}
.page-header {background: var(--app-deep); border-left: 6px solid var(--app-accent); border-radius: 8px; margin-bottom: 20px; padding: 20px 24px;}
.page-header h1 {color: #ffffff !important; font-size: 30px; margin: 0;}
.page-header p {color: #d4e4ea; margin: 4px 0 0;}
.segment-profile-card {background: #ffffff; border: 1px solid var(--app-border); border-top: 4px solid var(--segment-color); border-radius: 8px; box-shadow: 0 2px 8px rgba(11,42,63,.06); box-sizing: border-box; display: flex; flex-direction: column; height: 300px; padding: 18px;}
.segment-profile-top {align-items: center; display: flex; gap: 10px; margin-bottom: 14px;}
.segment-profile-icon {align-items: center; background: color-mix(in srgb, var(--segment-color) 12%, white); border-radius: 8px; display: inline-flex; font-size: 20px; height: 38px; justify-content: center; width: 38px;}
.segment-profile-label {color: var(--segment-color); font-size: 11px; font-weight: 700; letter-spacing: .06em;}
.segment-profile-card h3 {color: var(--app-text); font-size: 17px; min-height: 81px; line-height: 1.35; margin: 0 0 10px; overflow: visible;}
.segment-profile-stats {align-items: baseline; color: var(--app-muted); display: flex; gap: 6px;}
.segment-profile-stats strong {color: var(--app-text); font-size: 23px;}
.segment-profile-stats span {font-size: 12px;}
.segment-profile-stats b {color: var(--segment-color); font-size: 14px; margin-left: auto;}
.segment-profile-track {background: #edf2f5; border-radius: 99px; height: 6px; margin: 10px 0 12px; overflow: hidden;}
.segment-profile-track span {background: var(--segment-color); border-radius: inherit; display: block; height: 100%;}
.segment-profile-card p {color: var(--app-muted); font-size: 13px; line-height: 1.5; margin: auto 0 0; min-height: 39px;}
.segment-insight-card {background: #ffffff; border: 1px solid var(--app-border); border-top: 4px solid var(--segment-color); border-radius: 8px; box-shadow: 0 2px 8px rgba(11,42,63,.06); box-sizing: border-box; display: flex; flex-direction: column; height: 300px; padding: 18px;}
.segment-insight-card h3 {color: var(--app-text); font-size: 17px; line-height: 1.35; margin: 0 0 12px; min-height: 81px;}
.segment-insight-copy {color: var(--app-muted); font-size: 13px; line-height: 1.55; margin: 0;}
.segment-insight-spend {align-items: center; border-top: 1px solid var(--app-border); color: var(--app-muted); display: flex; font-size: 12px; justify-content: space-between; margin-top: auto; padding-top: 13px;}
.segment-insight-spend strong {color: var(--segment-color); font-size: 20px;}
[data-testid="stAppViewContainer"] {background: var(--app-page-bg);}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #0b2a3f, #0f4457 60%, #0b2a3f);}
[data-testid="stSidebar"] * {color: #e8f3f6 !important;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding: 8px 10px; border-radius: 8px;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background: var(--app-accent);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {color: white !important;}
[data-testid="stSidebar"] hr {border-color: rgba(255,255,255,.12);}
.sidebar-footer {position: fixed; bottom: 1.4rem; left: 4.25rem; z-index: 20; color: #e8f3f6; font-size: 12px;}
[data-testid="stMain"] .block-container {padding-top: 2rem; max-width: 1100px;}
[data-testid="stMetric"] {background: white; border-radius: 12px; padding: 16px; box-shadow: 0 1px 6px rgba(11,42,63,.08);}
[data-testid="stMetric"] label, [data-testid="stMetric"] [data-testid="stMetricDelta"] {color: var(--app-muted) !important;}
[data-testid="stMetric"] [data-testid="stMetricValue"] {color: var(--app-text) !important;}
[data-testid="stAlert"] {background: white; border: 1px solid var(--app-border); color: var(--app-text); border-radius: 12px;}
[data-testid="stDataFrame"] {border-radius: 12px; overflow: hidden;}
button[kind="primary"] {background: var(--app-accent); border: none; border-radius: 8px;}
[data-testid="stSidebarCollapseButton"] {color: white !important;}
#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.divider()
st.markdown('<div class="sidebar-footer">Komal</div>', unsafe_allow_html=True)
st.caption('Data note: Insights are descriptive and should be validated before operational use.')
