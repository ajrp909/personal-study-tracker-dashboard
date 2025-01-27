import os
import psycopg2
from psycopg2 import sql
import pandas as pd
from dotenv import load_dotenv
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px

app = Dash()

server = app.server

load_dotenv()

TABLE_NAME = "question"
DATABASE_URL = os.environ['DATABASE_URL']
DB_CONN = f"{DATABASE_URL}"

table_name = TABLE_NAME
query = "select * from {} order by question_id;"
conn = psycopg2.connect(DB_CONN)
cur = conn.cursor()
cur.execute(sql.SQL(query).format(sql.Identifier(table_name)))
columns = [column[0] for column in cur.description]
rows = cur.fetchall()
cur.close()
conn.close()

df = pd.DataFrame(rows, columns=columns)

scatter = df[df['difficulty'] > 0]

app.layout = [
    html.Div(children='My First App with Data'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
]

app.layout = [
    html.Div(children='Personal Study Tracker Table'),
    html.Hr(),
    dcc.Dropdown(options=['difficulty','correct', 'date'], value='difficulty', id='controls-and-radio-item'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=5),
    dcc.Graph(figure={}, id='controls-and-graph')]

@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    if col_chosen == "date":
        fig = px.bar(scatter, x=col_chosen, y='question_id')
    else:
        fig = px.scatter(scatter, x='question_id', y=col_chosen)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)