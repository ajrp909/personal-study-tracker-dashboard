import os
import psycopg2
from psycopg2 import sql
import pandas as pd
from dotenv import load_dotenv
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px

load_dotenv()

TABLE_NAME = "question"
DATABASE_URL = os.environ['DATABASE_URL']
DB_CONN = f"{DATABASE_URL}"

def fetch_data():
    table_name = TABLE_NAME
    query = "select * from {} order by question_id;"
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute(sql.SQL(query).format(sql.Identifier(table_name)))
    columns = [column[0] for column in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=columns)

app = Dash()

server = app.server

app.layout = [
    html.Div(children='Personal Study Tracker Table'),
    html.Hr(),
    dcc.Dropdown(options=['difficulty','correct', 'date'], value='difficulty', id='controls-and-radio-item'),
    dash_table.DataTable(id='table', data=fetch_data().to_dict('records'), page_size=5),
    dcc.Graph(figure={}, id='controls-and-graph'),
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)]

@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Output(component_id='table', component_property='data'),
    Input(component_id='controls-and-radio-item', component_property='value'),
    Input(component_id='interval-component', component_property='n_intervals')
)
def update(col_chosen, n):
    df = fetch_data()

    scatter = df[df['difficulty'] > 0]

    if col_chosen == "date":
        fig = px.bar(scatter, x=col_chosen, y='question_id')
    else:
        fig = px.scatter(scatter, x='question_id', y=col_chosen)
    return fig, df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)