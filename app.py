
import os
import pandas as pd
import psycopg2
import os
from pathlib import Path

import pandas as pd
import psycopg2
import dash
from dash import html, dash_table, dcc
import plotly.express as px
from dotenv import load_dotenv

caminho_env = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=caminho_env,
    override=True
)

senha = os.getenv("DB_PASSWORD")

print("Arquivo .env encontrado:", caminho_env.exists())
print("Senha carregada:", bool(senha))
print("Tamanho da senha:", len(senha) if senha else 0)

variaveis_necessarias = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD"
]

faltando = [
    variavel
    for variavel in variaveis_necessarias
    if not os.getenv(variavel)
]

if faltando:
    raise ValueError(
        "Faltam configurações no arquivo .env: "
        + ", ".join(faltando)
    )



conexao = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=senha,
    sslmode="require"
)


consulta = """
SELECT
    nu_inscricao AS candidato,
    nota_mt_matematica AS nota_matematica
FROM public.inep_enem_2025_amostra_perfeita
WHERE nota_mt_matematica > 700
ORDER BY nota_mt_matematica DESC;
"""

try:
    df = pd.read_sql_query(consulta, conexao)
finally:
    conexao.close()

df["candidato"] = df["candidato"].astype(str).str.strip()


grafico = px.histogram(
    df,
    x="nota_matematica",
    nbins=10,
    title="Distribuição das notas de Matemática acima de 700",
    labels={
        "nota_matematica": "Nota de Matemática",
        "count": "Quantidade de candidatos"
    }
)

grafico.update_layout(
    xaxis_title="Nota de Matemática",
    yaxis_title="Quantidade de candidatos",
    title_x=0.5
)


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.H1(
            "Candidatos com mais de 700 pontos em Matemática",
            style={
                "textAlign": "center",
                "marginBottom": "30px"
            }
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.H3("Quantidade de candidatos"),
                        html.P(
                            f"{len(df)}",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "bold"
                            }
                        )
                    ]
                ),

                html.Div(
                    [
                        html.H3("Maior nota"),
                        html.P(
                            f"{df['nota_matematica'].max():.1f}",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "bold"
                            }
                        )
                    ]
                ),

                html.Div(
                    [
                        html.H3("Menor nota"),
                        html.P(
                            f"{df['nota_matematica'].min():.1f}",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "bold"
                            }
                        )
                    ]
                )
            ],
            style={
                "display": "flex",
                "justifyContent": "space-around",
                "textAlign": "center",
                "flexWrap": "wrap",
                "marginBottom": "30px"
            }
        ),

        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[
                {
                    "name": "Candidato",
                    "id": "candidato"
                },
                {
                    "name": "Nota de Matemática",
                    "id": "nota_matematica"
                }
            ],
            page_size=35,
            sort_action="native",
            style_table={
                "overflowX": "auto",
                "margin": "20px"
            },
            style_cell={
                "textAlign": "center",
                "padding": "10px",
                "fontSize": "16px"
            },
            style_header={
                "fontWeight": "bold",
                "fontSize": "17px"
            }
        ),

        dcc.Graph(
            figure=grafico,
            style={
                "marginTop": "40px",
                "marginLeft": "20px",
                "marginRight": "20px"
            }
        )
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "padding": "20px"
    }
)


if __name__ == "__main__":
    app.run(debug=False)
