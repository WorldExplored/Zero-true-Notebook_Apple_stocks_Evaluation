import zero_true as zt
from zero_true import PlotlyComponent, RangeSlider, Button, Text, Layout, Row, Column
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("Ammok/apple_stock_price_from_1980-2021", split='train')
df = pd.DataFrame(dataset)
df['Date'] = pd.to_datetime(df['Date'])

# Assuming you've got a minimal and maximal year from your dataset
min_year = df['Date'].dt.year.min()
max_year = df['Date'].dt.year.max()

min_mon = df['Close'].min()
max_mon = 12 #Value is hard coded because dataset goes well over 100, which is unneed in the scope of the data.
# Define sliders for start and end year
year_slider = zt.RangeSlider(id='start_year', min=min_year, max=max_year, step=1, label='Year Slider')
price_slider = zt.RangeSlider(id='price', min=min_mon, max=max_mon, step=1, label='Price Slider')

def filter_df_by_year(df, start_year, end_year):
    # Filter the DataFrame based on the year range
    filtered_df = df[(df['Date'].dt.year >= start_year) & (df['Date'].dt.year <= end_year)]
    return filtered_df

def filter_df_by_money(df, start_mon, end_mon):
    # Filter the DataFrame based on the year range
    filtered_df = df[(df['Close'] >= start_mon) & (df['Close'] <= end_mon)]
    return filtered_df

def create_stock_price_plot(df):
    # Create the Plotly figure
    fig = go.Figure(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
    fig.update_layout(title="Apple Stock Price from 1980 to 2021", xaxis_title="Year", yaxis_title="Stock Price (USD)", template="plotly_dark")
    
    # Return the PlotlyComponent
    plotly_component = PlotlyComponent.from_figure(figure=fig, id="apple_stock_price_plot")
    return plotly_component

# Initially, display the plot for the full dataset
filtered_df = filter_df_by_year(df, year_slider.value[0], year_slider.value[1])
money_df = filter_df_by_money(filtered_df, price_slider.value[0], price_slider.value[1])

fig = px.scatter(money_df, x='Date', y='Close')

fig.update_layout(
    title='Apple Stock Price from 1980 to 2021',
    xaxis_title='Year',
    yaxis_title='Stock Price (USD)'
)
zt.PlotlyComponent.from_figure(id='graph', figure=fig)



from prophet import Prophet
import plotly
import plotly.graph_objects as go
import json

df_prophet = money_df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

m = Prophet()
m.fit(df_prophet)

future = m.make_future_dataframe(periods=365)
forecast = m.predict(future)

layout = {
    "title": "Forecasted Stock Prices",
    "xaxis": {"title": "Date"},
    "yaxis": {"title": "Stock Price"}
}

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name='Historical Close'))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Upper Confidence Interval', line=dict(width=0)))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Lower Confidence Interval', line=dict(width=0), fill='tonexty'))
fig.update_layout(layout)

# Convert the Plotly figure to JSON
figure_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Create a PlotlyComponent with the serialized figure
plotly_component = zt.PlotlyComponent(
    id="forecast_plot",
    figure_json=figure_json
)

# Assuming you have a method to add the component to your UI, such as adding it to a layout
layout = zt.Layout(components=[plotly_component])