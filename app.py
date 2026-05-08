import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import warnings
import os
warnings.filterwarnings('ignore')
 
# ── 1. Load Cleaned Data ──────────────────────────────────────────────────────
df = pd.read_csv('C:\\Users\\User\\Desktop\\DV\\DV_project\\Phase2\\Melbourne_Housing_Cleaned.csv')
df['Date']         = pd.to_datetime(df['Date'])
df['YearMonth']    = df['Date'].dt.to_period('M').astype(str)
type_map           = {'h': 'House', 't': 'Townhouse', 'u': 'Unit'}
df['PropertyType'] = df['Type'].map(type_map)
df['Price_M']      = df['Price'] / 1e6
 
COLORS = {
    'House':     '#2E86AB',
    'Townhouse': '#A23B72',
    'Unit':      '#F18F01',
    'All':       '#3B1F2B'
}
BG = '#F8F9FA'
 
# ── 2. App Layout ─────────────────────────────────────────────────────────────
app = Dash(__name__)
app.title = "Melbourne Housing Dashboard"
 
app.layout = html.Div(
    style={'backgroundColor': BG, 'fontFamily': 'Arial, sans-serif',
           'minHeight': '100vh', 'padding': '0 0 40px 0'},
    children=[
 
        # Header
        html.Div(
            style={'backgroundColor': '#2E86AB', 'padding': '24px 40px',
                   'marginBottom': '30px'},
            children=[
                html.H1("Melbourne Housing Market Dashboard",
                        style={'color': 'white', 'margin': 0,
                               'fontSize': '26px', 'fontWeight': 'bold'}),
                html.P("Interactive exploration of the Melbourne Housing Dataset (2016-2017)",
                       style={'color': '#d0eaf7', 'margin': '6px 0 0 0',
                              'fontSize': '14px'})
            ]
        ),
 
        # Controls
        html.Div(
            style={'display': 'flex', 'gap': '40px', 'alignItems': 'flex-end',
                   'padding': '0 40px', 'marginBottom': '30px', 'flexWrap': 'wrap'},
            children=[
                html.Div([
                    html.Label("Property Type",
                               style={'fontWeight': 'bold', 'fontSize': '13px',
                                      'color': '#333', 'marginBottom': '6px',
                                      'display': 'block'}),
                    dcc.Dropdown(
                        id='type-dropdown',
                        options=[{'label': 'All Types', 'value': 'All'}] +
                                [{'label': t, 'value': t}
                                 for t in ['House', 'Townhouse', 'Unit']],
                        value='All', clearable=False,
                        style={'width': '200px', 'fontSize': '13px'}
                    )
                ]),
                html.Div([
                    html.Label(id='slider-label',
                               style={'fontWeight': 'bold', 'fontSize': '13px',
                                      'color': '#333', 'marginBottom': '6px',
                                      'display': 'block'}),
                    dcc.Slider(
                        id='price-slider', min=0, max=5, step=0.5, value=5,
                        marks={i: f'${i}M' for i in range(0, 6)},
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    )
                ], style={'width': '340px'}),
                html.Div([
                    html.Label("Scatter Opacity",
                               style={'fontWeight': 'bold', 'fontSize': '13px',
                                      'color': '#333', 'marginBottom': '6px',
                                      'display': 'block'}),
                    dcc.RadioItems(
                        id='opacity-radio',
                        options=[
                            {'label': ' Light',  'value': 0.3},
                            {'label': ' Medium', 'value': 0.6},
                            {'label': ' Full',   'value': 1.0},
                        ],
                        value=0.6, inline=True,
                        style={'fontSize': '13px', 'gap': '16px'}
                    )
                ]),
            ]
        ),
 
        # Charts Row
        html.Div(
            style={'display': 'flex', 'gap': '24px', 'padding': '0 40px',
                   'flexWrap': 'wrap'},
            children=[
                html.Div(
                    style={'flex': '1', 'minWidth': '420px',
                           'backgroundColor': 'white', 'borderRadius': '10px',
                           'padding': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'},
                    children=[
                        html.H3("Building Area vs. Sale Price",
                                style={'margin': '0 0 4px 0', 'fontSize': '15px',
                                       'color': '#222', 'fontWeight': 'bold'}),
                        html.P("Filtered by property type and max price",
                               style={'margin': '0 0 12px 0', 'fontSize': '12px',
                                      'color': '#888'}),
                        dcc.Graph(id='scatter-chart', config={'displayModeBar': False})
                    ]
                ),
                html.Div(
                    style={'flex': '1', 'minWidth': '420px',
                           'backgroundColor': 'white', 'borderRadius': '10px',
                           'padding': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'},
                    children=[
                        html.H3("Average Price Over Time",
                                style={'margin': '0 0 4px 0', 'fontSize': '15px',
                                       'color': '#222', 'fontWeight': 'bold'}),
                        html.P("Monthly average sale price by property type",
                               style={'margin': '0 0 12px 0', 'fontSize': '12px',
                                      'color': '#888'}),
                        dcc.Graph(id='line-chart', config={'displayModeBar': False})
                    ]
                ),
            ]
        ),
 
        # KPI Cards
        html.Div(id='kpi-row',
                 style={'display': 'flex', 'gap': '20px',
                        'padding': '24px 40px 0 40px', 'flexWrap': 'wrap'}),
    ]
)
 
 
# ── 3. Callbacks ──────────────────────────────────────────────────────────────
 
@app.callback(
    Output('slider-label', 'children'),
    Input('price-slider', 'value')
)
def update_slider_label(max_price):
    return f"Max Price: ${max_price}M"
 
 
@app.callback(
    Output('scatter-chart', 'figure'),
    Input('type-dropdown', 'value'),
    Input('price-slider', 'value'),
    Input('opacity-radio', 'value')
)
def update_scatter(selected_type, max_price, opacity):
    dff = df[df['Price_M'] <= max_price].copy()
    dff = dff[dff['BuildingArea'] < 600]
    if selected_type != 'All':
        dff = dff[dff['PropertyType'] == selected_type]
 
    fig = px.scatter(
        dff, x='BuildingArea', y='Price_M',
        color='PropertyType', color_discrete_map=COLORS,
        opacity=opacity, trendline='ols', trendline_scope='overall',
        labels={'BuildingArea': 'Building Area (m2)',
                'Price_M': 'Sale Price (AUD Millions)',
                'PropertyType': 'Type'},
        hover_data={'Suburb': True, 'Rooms': True,
                    'Price_M': ':.2f', 'BuildingArea': True}
    )
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1, title=''),
        font=dict(family='Arial', size=12), height=340
    )
    fig.update_xaxes(gridcolor='#ECECEC', title_font_size=12)
    fig.update_yaxes(gridcolor='#ECECEC', tickprefix='$', ticksuffix='M',
                     title_font_size=12)
    return fig
 
 
@app.callback(
    Output('line-chart', 'figure'),
    Input('type-dropdown', 'value'),
    Input('price-slider', 'value')
)
def update_line(selected_type, max_price):
    dff = df[df['Price_M'] <= max_price].copy()
    types_to_show = ([selected_type] if selected_type != 'All'
                     else ['House', 'Townhouse', 'Unit'])
 
    fig = go.Figure()
    for ptype in types_to_show:
        sub = dff[dff['PropertyType'] == ptype]
        line_data = (sub.groupby('YearMonth')['Price_M']
                       .mean().reset_index()
                       .sort_values('YearMonth'))
        fig.add_trace(go.Scatter(
            x=line_data['YearMonth'], y=line_data['Price_M'],
            mode='lines+markers', name=ptype,
            line=dict(color=COLORS[ptype], width=2.5),
            marker=dict(size=5),
            hovertemplate=(
                f"<b>{ptype}</b><br>"
                "Month: %{x}<br>"
                "Avg Price: $%{y:.2f}M<extra></extra>"
            )
        ))
 
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=60),
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1, title=''),
        font=dict(family='Arial', size=12), height=340,
        xaxis=dict(tickangle=45, gridcolor='#ECECEC', title='Sale Month'),
        yaxis=dict(gridcolor='#ECECEC', tickprefix='$', ticksuffix='M',
                   title='Avg Price (AUD M)')
    )
    return fig
 
 
@app.callback(
    Output('kpi-row', 'children'),
    Input('type-dropdown', 'value'),
    Input('price-slider', 'value')
)
def update_kpis(selected_type, max_price):
    dff = df[df['Price_M'] <= max_price].copy()
    if selected_type != 'All':
        dff = dff[dff['PropertyType'] == selected_type]
 
    kpis = [
        ("Total Properties", f"{len(dff):,}",                    "#2E86AB"),
        ("Median Price",     f"${dff['Price_M'].median():.2f}M", "#A23B72"),
        ("Average Price",    f"${dff['Price_M'].mean():.2f}M",   "#F18F01"),
        ("Avg Rooms",        f"{dff['Rooms'].mean():.1f}",        "#3B1F2B"),
    ]
 
    cards = []
    for label, value, color in kpis:
        cards.append(html.Div(
            style={'flex': '1', 'minWidth': '140px',
                   'backgroundColor': 'white', 'borderRadius': '10px',
                   'padding': '16px 20px',
                   'borderLeft': f'5px solid {color}',
                   'boxShadow': '0 2px 8px rgba(0,0,0,0.07)'},
            children=[
                html.P(label, style={'margin': '0 0 4px 0', 'fontSize': '12px',
                                     'color': '#888', 'fontWeight': 'bold',
                                     'textTransform': 'uppercase',
                                     'letterSpacing': '0.5px'}),
                html.H2(value, style={'margin': 0, 'fontSize': '22px',
                                      'color': color, 'fontWeight': 'bold'})
            ]
        ))
    return cards
 
 
# ── 4. Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))