import os
from datetime import datetime, timedelta
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
EXAM_DATE = datetime.strptime('2025-06-05', '%Y-%m-%d')

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

app.layout = html.Div([
    html.H1(children='Personal Study Tracker Table'),
    html.Hr(),
    dcc.Dropdown(options=['date', 'difficulty', 'correct'], value='date', id='dropdown'),
    dash_table.DataTable(id='table', data=[], page_size=5),
    dcc.Graph(figure={}, id='graph'),
    dcc.Interval(id='interval', interval=60*1000, n_intervals=0)
])

@callback(
    Output(component_id='graph', component_property='figure'),
    Output(component_id='table', component_property='data'),
    Input(component_id='dropdown', component_property='value'),
    Input(component_id='interval', component_property='n_intervals')
)
def update(col_chosen, n):
    df = fetch_data()

    table_data = df.to_dict('records')

    if col_chosen == "date":
        date_count = df.groupby('date').size().reset_index(name='count')
        today = datetime.now()
        days_remaining = (EXAM_DATE - today).days
        questions_done = date_count['count'].sum()
        questions_remaining = 500 - questions_done
        daily_avg_needed = questions_remaining / days_remaining
        fig = px.scatter(date_count, x='date', y='count',
                         title=f'Countdown: {days_remaining} days.\n'
                         f'Questions: {questions_done} done, {questions_remaining} left.')
        fig.add_vline(x=EXAM_DATE, line_color='red', line_width=3)
        fig.add_vrect(x0="2025-05-23", x1=str(EXAM_DATE), 
              annotation_text="2 weeks to go", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
        fig.add_hline(y=daily_avg_needed, line_dash='dash', line_color='green', 
                      annotation_text=f'Avg. Questions Needed per day: {daily_avg_needed:.2f}', 
                      annotation_position='bottom left')
        fig.update_layout(xaxis=dict(range=[datetime.strptime('2025-01-01', '%Y-%m-%d'), EXAM_DATE + timedelta(hours=6)]),
                          yaxis=dict(range=[0,None]))
    if col_chosen == "difficulty":
        difficulty_count = df[df['difficulty'] > 0].groupby('difficulty').size().reset_index(name='count')
        fig = px.bar(difficulty_count, x='difficulty', y='count', title='Difficulty of Question')
        fig.update_traces(width=0.95)
    if col_chosen == "correct":
        correct_count = df['correct'].value_counts().reset_index()
        correct_count.columns = ['correct', 'count']
        fig = px.pie(correct_count, values='count', names='correct', title='Proportion of Correct Answers')

    return fig, table_data

if __name__ == '__main__':
    app.run_server(debug=True)
