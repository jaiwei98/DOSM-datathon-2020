import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from datetime import date
import gcsfs

#loading data
fs = gcsfs.GCSFileSystem(project='dosm-dashboard')
with fs.open('dosm_dashboard_project/data/v6.csv') as f:
    df = pd.read_csv(f)
with fs.open('dosm_dashboard_project/data/Important_Dates.csv') as f:
    imp_date = pd.read_csv(f)




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#filter
available_indicators = df['first_cat'].unique()
max_date =  pd.DatetimeIndex(df['dates']).max()
min_date =  pd.DatetimeIndex(df['dates']).min()

top_bar = dbc.Card([html.H2("PriLLigence",className="control_label",style=dict(display='flex', justifyContent='center')),
                    html.H6("-The Price Intelligence Tools-",className="control_label",style=dict(display='flex', justifyContent='center'))],color="dark",inverse=True, outline=False )

card_main = dbc.Card(
    [
        dbc.CardBody(
            [
                        html.H6("Filter by first product category:",className="control_label"),
                        dcc.Dropdown(
                            id="first_cat_drop", style={"fontColor": "grey","color": "black"},
                            options=[{'label': i, 'value': i} for i in available_indicators],
                            value='mother & baby',
                            className="dcc_control",
                        ),
                        html.Br(),
                        html.H6(
                            "Filter by Date:",
                            id="date_slide",
                            className="control_label",
                        ),
                        dcc.DatePickerRange(
                            id="date_slider",
                            min_date_allowed=date(min_date.year, min_date.month, min_date.day),
                            max_date_allowed=date(max_date.year, max_date.month, max_date.day),
                            initial_visible_month=date(min_date.year, min_date.month, min_date.day),
                            start_date=date(min_date.year, min_date.month, min_date.day),
                            end_date=date(max_date.year, max_date.month, max_date.day),
                            className="dcc_control",
                        ),
                        html.Br(),
                        html.Br(),
                        html.H6(
                            "Pie Chart (Can use for filter)", 
                            className="control_label"
                        ),
                        dcc.Graph(
                            id="pie_chart"
                        ),
                        html.Br(),
                        html.H6(
                            "Filter by Item Category:", 
                            className="control_label"
                        ),
                        dcc.Dropdown(
                            id="item_category_drop",
                            #options=[{'label': i, 'value': i} for i in available_indicators],
                            style={"fontColor": "grey","color": "black"},
                            multi=True,
                            #value=NULL,
                            className="dcc_control",
                        ),
            ]
        ),
    ],
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)

rec_chart = dbc.Card(
    [
        dbc.Card(
            [
                html.H4("Price's Trend"),
                dcc.Graph(id="line_chart"),
            ],body=True, color="secondary",
        ),
        dbc.Card(
            [
                html.H4("Average Price by Weeks and Days"),
                dcc.Graph(id="bar_chart"),
            ],body=True, color="secondary",
        )
     
    ],
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,
)

sq_chart1 = dbc.Card(
    [
       dbc.Card(
            [
                html.H4("3-Dimension Relationship of Price"),
                dcc.Graph(id="3d_graph"),
            ],body=True, color="secondary",
        ),
    ],
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,
)
sq_chart2 = dbc.Card(
    [
       dbc.Card(
            [
                html.H4("Best Price Range"),
                dcc.Graph(id="boxplot"),
            ],body=True, color="secondary",
        ),
    ],
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,
)
sq_chart3 = dbc.Card(
    [
       dbc.Card(
            [
                html.H4("Top 10 Seller"),
                dcc.Graph(id="seller"),
            ],body=True, color="secondary",
        ),
    ],
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,
)

app.layout = html.Div([
    html.Br(),
    dbc.Row([dbc.Col([top_bar],)], justify="around"),
    html.Br(),
    dbc.Row([
            dbc.Col([card_main],width=5),
            dbc.Col([rec_chart],width=7)
             ], justify="around"), 
    html.Br(),  
    dbc.Row([
            dbc.Col([sq_chart1],width=6),
            dbc.Col([sq_chart2],width=3),
            dbc.Col([sq_chart3],width=3)
             ], justify="around"), 

])

@app.callback(
    Output('pie_chart', 'figure'),
    [Input('first_cat_drop', 'value')])

def update_graph(first_cat_drop):
    dff = df[df['first_cat'] == first_cat_drop]
    fig = px.sunburst(dff, path=['first_cat', 'second_cat', 'item_category'],color='rating',color_continuous_midpoint=np.average(df['rating'], weights=df['rating']),
                      labels={'rating':'Rating'})
    return fig


@app.callback(
    [Output('item_category_drop', 'options'),
     Output('item_category_drop', 'value')],
    [Input('first_cat_drop', 'value'),
     Input('pie_chart', 'clickData')])

def get_options(first_cat_drop, clickData):
    dff = df[df['first_cat'] == first_cat_drop]
    indicators = dff['item_category'].unique()
    retn = [{'label': i, 'value': i} for i in indicators]
    
    if clickData:        
        if len(clickData['points'][0]["id"].split('/')) == 3:
            indicators = (clickData['points'][0]["id"].split('/')[2])
            retn = [{'label': indicators, 'value': indicators}]
        if len(clickData['points'][0]["id"].split('/')) == 2:
            temp = clickData['points'][0]["label"]
            dff = dff[dff['second_cat'] == temp]
            indicators = dff['item_category'].unique()
            retn = [{'label': i, 'value': i} for i in indicators]
        if clickData['points'][0]["id"] == '':
            dff = df[df['first_cat'] == first_cat_drop]
            indicators = dff['item_category'].unique()
            retn = [{'label': i, 'value': i} for i in indicators]
            
    return retn, indicators


"""
JaiWei
"""
@app.callback(
    Output('line_chart', 'figure'),
    [Input('first_cat_drop', 'value'),
     Input('item_category_drop', 'value'),
     Input('pie_chart', 'clickData'),
     Input('date_slider', 'start_date'),
     Input('date_slider', 'end_date')])

def update_graph_line(first_cat_drop,item_category_drop,clickData,start_date,end_date):
    dff = df[df['first_cat'] == first_cat_drop] 
    dff = dff[dff['dates'] >= str(start_date)]
    dff = dff[dff['dates'] <= str(end_date)] 
    if clickData:
        if len(clickData['points'][0]["id"].split('/')) == 2:
            temp = clickData['points'][0]["label"]
            dff = dff[dff['second_cat'] == temp]
        
        if len(clickData['points'][0]["id"].split('/')) == 3:
            indicators = clickData['points'][0]["label"]
            dff = dff[dff['item_category'] == indicators]
        else:
            dff = dff[dff['item_category'].isin(item_category_drop)]

    dff= dff.groupby(['dates']).agg(max_price = pd.NamedAgg(column='price_actual', aggfunc=np.max),
                                   min_price = pd.NamedAgg(column='price_actual', aggfunc=np.min),
                                   mean_price = pd.NamedAgg(column='price_actual', aggfunc=np.mean))
    dff = dff.reset_index()
    fig = px.line(dff, x="dates", y=dff.columns)
    
    imp_date_fil = imp_date[imp_date['Date1'] >= str(start_date)]
    imp_date_fil = imp_date_fil[imp_date_fil['Date1'] <= str(end_date)]
    
    i = 0
    for dat in imp_date_fil['Date1']:
        if i % 2 == 0:
            fig = fig.add_vrect(x0=imp_date_fil['Date1'][i], x1=imp_date_fil['Date1'][i],annotation_text = imp_date_fil['Event'][i], annotation_position='top left')
        else:
            fig = fig.add_vrect(x0=imp_date_fil['Date1'][i], x1=imp_date_fil['Date1'][i],annotation_text = imp_date_fil['Event'][i], annotation_position='bottom left')
        i = i + 1
    return fig

@app.callback(
    Output('boxplot', 'figure'),
    [Input('first_cat_drop', 'value'),
     Input('item_category_drop', 'value'),
     Input('pie_chart', 'clickData'),
     Input('date_slider', 'start_date'),
     Input('date_slider', 'end_date')])

def update_graph_boxplot(first_cat_drop,item_category_drop,clickData,start_date,end_date):
    dff = df[df['first_cat'] == first_cat_drop] 
    dff = dff[dff['dates'] >= str(start_date)]
    dff = dff[dff['dates'] <= str(end_date)] 
    if clickData:
        if len(clickData['points'][0]["id"].split('/')) == 2:
            temp = clickData['points'][0]["label"]
            dff = dff[dff['second_cat'] == temp]
        
        if len(clickData['points'][0]["id"].split('/')) == 3:
            indicators = clickData['points'][0]["label"]
            dff = dff[dff['item_category'] == indicators]
        else:
            dff = dff[dff['item_category'].isin(item_category_drop)]
            
    dff= dff.groupby(['sellerID']).agg(item_marketed = pd.NamedAgg(column='item_category', aggfunc='count'),
                                   Rating = pd.NamedAgg(column='rating', aggfunc=np.mean),
                                   mean_price = pd.NamedAgg(column='price_actual', aggfunc=np.mean))
    dff = dff.reset_index()
    dff = dff.sort_values(['Rating','item_marketed'], ascending=False).head(10)

    fig = px.box(dff, y="mean_price",labels={'mean_price':'Best Price Range'})
    return fig

@app.callback(
    Output('seller', 'figure'),
    [Input('first_cat_drop', 'value'),
     Input('item_category_drop', 'value'),
     Input('pie_chart', 'clickData'),
     Input('date_slider', 'start_date'),
     Input('date_slider', 'end_date')])

def update_graph_seller(first_cat_drop,item_category_drop,clickData,start_date,end_date):
    dff = df[df['first_cat'] == first_cat_drop] 
    dff = dff[dff['dates'] >= str(start_date)]
    dff = dff[dff['dates'] <= str(end_date)] 
    if clickData:
        if len(clickData['points'][0]["id"].split('/')) == 2:
            temp = clickData['points'][0]["label"]
            dff = dff[dff['second_cat'] == temp]
        
        if len(clickData['points'][0]["id"].split('/')) == 3:
            indicators = clickData['points'][0]["label"]
            dff = dff[dff['item_category'] == indicators]
        else:
            dff = dff[dff['item_category'].isin(item_category_drop)]
            
    dff= dff.groupby(['sellerID']).agg(item_marketed = pd.NamedAgg(column='item_category', aggfunc='count'),
                                   Rating = pd.NamedAgg(column='rating', aggfunc=np.mean))
    dff = dff.reset_index()
    dff = dff.sort_values(['Rating','item_marketed'], ascending=False).head(10)
    fig = px.bar(dff, y="sellerID", x='item_marketed', color='Rating',color_continuous_midpoint=(0.5),
                 labels={'sellerID':'Seller ID', 'item_marketed':'Total Item Marketed'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

"""
WenKhang
"""
@app.callback(
    Output('bar_chart', 'figure'),
    [Input('first_cat_drop', 'value'),
     Input('item_category_drop', 'value'),
     Input('pie_chart', 'clickData'),
     Input('date_slider', 'start_date'),
     Input('date_slider', 'end_date')])
  
def update_graph_bar(first_cat_drop,item_category_drop,clickData,start_date,end_date):
    dff = df[df['first_cat'] == first_cat_drop] 
    dff = dff[dff['dates'] >= str(start_date)]
    dff = dff[dff['dates'] <= str(end_date)]
    if clickData:
        if len(clickData['points'][0]["id"].split('/')) == 2:
            temp = clickData['points'][0]["label"]
            dff = dff[dff['second_cat'] == temp]
        
        if len(clickData['points'][0]["id"].split('/')) == 3:
            indicators = clickData['points'][0]["label"]
            dff = dff[dff['item_category'] == indicators]
        else:
            dff = dff[dff['item_category'].isin(item_category_drop)]
     
    dff['week_in_month'] = dff['week_in_month'].astype(str)
    dff= dff.groupby(['week_in_month','day_in_week']).agg(Mean_Price = pd.NamedAgg(column='price_actual', aggfunc=np.mean))
    dff.reset_index(inplace=True)
    fig = px.bar(dff,color='day_in_week', y='Mean_Price',x='week_in_month', barmode="group",
                  category_orders={'week_in_month':['1','2','3','4','5'], 
                                   'day_in_week':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']},
                  labels={'Mean_Price':'Average Price', 'week_in_month':'Week of Month', 'day_in_week':'Day of Week'})
    fig.update_layout(transition_duration=500)    
    return fig


"""
JingYi
"""
@app.callback(
    Output('3d_graph', 'figure'),
    [Input('first_cat_drop', 'value'),
     Input('item_category_drop', 'value'),
     Input('pie_chart', 'clickData'),
     Input('date_slider', 'start_date'),
     Input('date_slider', 'end_date')])

def update_graph_scatter(first_cat_drop,item_category_drop,clickData,start_date,end_date):
    dff = df[df['first_cat'] == first_cat_drop] 
    dff = dff[dff['dates'] >= str(start_date)]
    dff = dff[dff['dates'] <= str(end_date)]
    if clickData:
        if len(clickData['points'][0]["id"].split('/')) == 2:
            temp = clickData['points'][0]["label"]
            dff = dff[dff['second_cat'] == temp]
        
        if len(clickData['points'][0]["id"].split('/')) == 3:
            indicators = clickData['points'][0]["label"]
            dff = dff[dff['item_category'] == indicators]
        else:
            dff = dff[dff['item_category'].isin(item_category_drop)]
            
    productMinMax = dff.groupby(['item_category', 'price_ori']).agg(MinPriceActual = pd.NamedAgg(column='price_actual', aggfunc=min), 
                                                                    MaxPriceActual = pd.NamedAgg(column='price_actual', aggfunc=max),
                                                                    mean_rating = pd.NamedAgg(column='rating', aggfunc=np.mean))
    productMinMax.reset_index(inplace=True)                                                     

    fig = px.scatter_3d(productMinMax, x='price_ori', y='MinPriceActual', z='MaxPriceActual', color='mean_rating',
                        labels={'mean_rating':'Rating'})
    fig.update_layout(scene=dict(xaxis_title='Original Price', 
                                 yaxis_title='Minimum Actual Price',
                                 zaxis_title='Maximum Actual Price'),
                      width=700, margin=dict(r=10,b=10,l=10,t=10))
    fig.update_layout(scene=dict(xaxis=dict(backgroundcolor="rgb(200,200,230)", gridcolor="white", showbackground=True, zerolinecolor="white"),
                                 yaxis=dict(backgroundcolor="rgb(230,200,230)", gridcolor="white", showbackground=True, zerolinecolor="white"),
                                 zaxis=dict(backgroundcolor="rgb(230,230,200)", gridcolor="white", showbackground=True, zerolinecolor="white")))
    #fig.update(layout_showlegend=False)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050, dev_tools_ui=True)
