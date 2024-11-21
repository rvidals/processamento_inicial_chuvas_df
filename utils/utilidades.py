import os 
import pandas as pd 
import plotly.express as px
from collections import defaultdict

# Caminho do arquivo
def caminho_arquivo(nome_arquivo: str):
    return os.path.join(os.getcwd(), nome_arquivo)

# Carregar dados do arquivo CSV
def carregar_dados_csv(caminho_arquivo: str, delimiter: str = ';', skiprows: int = 10):
    return pd.read_csv(caminho_arquivo, delimiter=delimiter, skiprows=skiprows)

# Contar valores nodata a partir de uma coluna de interesse
def contar_valores_nodata(df: pd.DataFrame, coluna: str):
    isna = df[coluna].isna()
    notna = df[coluna].notna()
    return f'Completo: {len(df[coluna])} | Buracos (NAN): {isna.sum()}  | Sem buracos: {notna.sum()}'

# Filtrar dados não nulos
def filtrar_dados_notNaN(df: pd.DataFrame, coluna: str):
    notna = df[coluna].notna()
    return df[notna]

# Inserir coluna com o número do mês
def inserir_mes_ano(df: pd.DataFrame, coluna: str):
    df_copy = df.copy()
    df_copy[coluna] = pd.to_datetime(df_copy[coluna]) # Converter a coluna para o formato de data
    nm_mes = df_copy[coluna].dt.strftime("%B") # Extrair o nome do mês
    ano = df_copy[coluna].dt.strftime("%Y") # Extrair o ano

    df_copy.insert(1,"MÊS",nm_mes) # Inserir na 1ª posição a coluna com o nome do mês
    df_copy.insert(2,"ANO",ano) # Inserir na 1ª posição a coluna com o ano

    return df_copy

# Inserir coluna com o número do mês e orderar
def inserir_numero_mes(df: pd.DataFrame):
    df_copy = df.copy()

    # Definir um dicionário com o número do mês
    # Definir o dicionário consolidado para mapeamento de meses
    dt_number = defaultdict(lambda: None, {
        'january': 1, 'janeiro': 1,
        'february': 2, 'fevereiro': 2,
        'march': 3, 'março': 3,
        'april': 4, 'abril': 4,
        'may': 5, 'maio': 5,
        'june': 6, 'junho': 6,
        'july': 7, 'julho': 7,
        'august': 8, 'agosto': 8,
        'september': 9, 'setembro': 9,
        'october': 10, 'outubro': 10,
        'november': 11, 'novembro': 11,
        'december': 12, 'dezembro': 12
    })

    # Relacionar o número do mês com o nome do mês e atribuir a varíavel num_mes
    num_mes = df_copy['MÊS'].apply(lambda x: dt_number[x.lower()] if pd.notna(x) else None)

    df_copy.insert(1,"NUM_MÊS",num_mes) # Inserir na 1ª posição a coluna com o número do mês

    df_copy = df_copy.sort_values(by=['NUM_MÊS']) # Ordenar os dados pela coluna NUM_MÊS

    return df_copy

# Anos que possuem menos de 360 dias de dados de temperatura média
def listar_anos_descartados(df: pd.DataFrame, coluna: str):
    df_copy = df.copy()

    qtd_dias_ano = df_copy.groupby([coluna]).count() # Contar a quantidade de dias de medição por ano
    qtd_dias_ano = qtd_dias_ano.reset_index() # Resetar o índice

    qtd_dias_ano = qtd_dias_ano.iloc[:,0:2] # Selecionar as colunas de interesse
    qtd_dias_ano = qtd_dias_ano.rename(columns={"Data Medicao": "Dias"}) # Renomear a coluna

    l_ano_maior = qtd_dias_ano[qtd_dias_ano['Dias'] > 360]['ANO'].tolist()   # Anos com mais de 360 dias de medição
    l_ano_menor = qtd_dias_ano[qtd_dias_ano['Dias'] < 360]['ANO'].tolist() # Anos com menos de 360 dias de medição
    
    return l_ano_maior, l_ano_menor

def calcular_media_mes(df: pd.DataFrame, colunas: list, coluna: str):
    df_copy = df.copy()

    # Média da Temperatural Mensal para cada ano e mês da série temporal
    temp_mes_serie = df_copy.groupby(colunas)[coluna].mean().reset_index()
    return temp_mes_serie

def calcular_precipitacao_acumulada_mes(df: pd.DataFrame, colunas: list, coluna: str):
    df_copy = df.copy()

    # Média da Temperatural Mensal para cada ano e mês da série temporal
    precipitacao_soma_mes = df_copy.groupby(colunas)[coluna].sum().reset_index()
    return precipitacao_soma_mes

def calcular_media_ano_completo(df: pd.DataFrame, colunas: list, coluna: str):
    df_copy = df.copy()

    # Média da Temperatural Mensal para cada ano e mês da série temporal
    temp_mes = df_copy.groupby(colunas)[coluna].mean()

    df2 = pd.DataFrame(temp_mes)
    df2 = df2.reset_index()
    return df2

def create_gantt_chart(df):
    """
    Cria um gráfico de Gantt a partir de um DataFrame.
    Esse Gantt tem como característica a divisão de períodos contínuos de uma mesma estação. Ou seja, se houver um intervalo 
    de mais de um dia entre as datas, um novo período é criado. 
    
    OBS: Não gostei de usar esse gante, pois ele não é muito intuitivo.
    

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados de precipitação com as colunas 'EstacaoCodigo' e 'Data'.

    Retorna:
    None
    """
    # Passo 1: Identificar os períodos contínuos por estação
    df = df.sort_values(by=["EstacaoCodigo", "Data"])  # Ordenar por estação e data
    df['EstacaoCodigo'] = df['EstacaoCodigo'].astype(str)  # Converter a coluna de estação para string
    df['Data'] = pd.to_datetime(df['Data'])  # Converter a coluna de data para datetime
    df["Diff"] = (df["Data"] - df["Data"].shift()).dt.days  # Diferença em dias
    df["Grupo"] = (df["Diff"] > 1).cumsum()  # Novo grupo se a diferença for maior que 1 dia

    # Passo 2: Criar a tabela de início e fim
    gantt_df = df.groupby(["EstacaoCodigo", "Grupo"]).agg(
        Inicio=("Data", "min"),
        Fim=("Data", "max")
    ).reset_index()

    # Passo 3: Criar o gráfico de Gantt
    fig = px.timeline(
        gantt_df,
        x_start="Inicio",
        x_end="Fim",
        y="EstacaoCodigo",
        title="Gráfico de Gantt por Estação",
        labels={"EstacaoCodigo": "Código da Estação", "Inicio": "Início", "Fim": "Fim"}
    )

    # Ajustar o layout
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Estações",
        autosize=False,
        width=1200,
        height=600
    )

    # Exibir o gráfico
    fig.show()
    
    


def gantt_serie_gap_overlap(df, codigo_estacao, data): 
    """
    Cria um gráfico de Gantt a partir de um DataFrame para identificar os períodos contínuos de uma mesma estação.
    Além disso, é possível identificar os períodos de sobreposição e de lacunas entre os períodos contínuos ao analisar as barras.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados de precipitação.
    codigo_estacao (str): Nome da coluna que contém o código da estação.
    data (str): Nome da coluna que contém a data.

    Retorna:
    None
    """
    # Passo 1: Identificar os períodos contínuos por estação
    df = df.sort_values(by=[codigo_estacao, data])  # Ordenar por estação e data
    
    # Verificar se é uma string
    if df[codigo_estacao].dtype != 'object':
        df[codigo_estacao] = df[codigo_estacao].astype(str)
    
    # Verificar se é uma data
    if df[data].dtype != 'datetime64[ns]':
        df[data] = pd.to_datetime(df[data])
    
    # Passo 2: Criar a tabela de início e fim geral por estação
    gantt_df = df.groupby(codigo_estacao).agg(
        Inicio=(data, "min"),
        Fim=(data, "max")
    ).reset_index()

    # Passo 3: Criar o gráfico de Gantt
    fig = px.timeline(
        gantt_df,
        x_start="Inicio",
        x_end="Fim",
        y=codigo_estacao,
        title="Gráfico de Gantt por Estação",
        labels={codigo_estacao: "Código da Estação", "Inicio": "Início", "Fim": "Fim"}
    )

    # Ajustar o layout
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Estações",
        autosize=False,
        width=1200,
        height=600
    )

    # Exibir o gráfico
    fig.show()