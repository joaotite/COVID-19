# -*- coding: utf-8 -*-
"""update_plotly_new.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11Unlfpu7y-UrvJwcUI6EYtrt2N90j8PW
"""

! pip install plotly==4.8.1

if os.path.isdir('COVID-19-master'): rmtree('COVID-19-master')
print("Starting Brazil data")
import requests, zipfile, io

csse_path = "https://github.com/joaotite/COVID-19/archive/master.zip"

r = requests.get(csse_path, stream=True)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

import pandas as pd
import numpy as np
import os, math
from shutil import rmtree

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from datetime import datetime
from datetime import timedelta

pd.options.plotting.backend = "plotly"

root_path = os.path.join(os.getcwd(), "COVID-19-master/data/")
save_path = os.path.join(os.getcwd())#, "COVID-19-master/imagens/")
save_path = os.getcwd()
casos_br_path = os.path.join(os.getcwd(), root_path+"casos-br-total.csv")
df = pd.read_csv(casos_br_path)

df.tail()

def plot_acumulado(column, filename, title, color, dias_projecao):

  ## Prever os próximos sete dias ##
  conf7 = list(df[column].to_numpy()[-7:])
  tc = [conf7[i+1]/conf7[i] for i in range(len(conf7)-1)]
  tc = np.array(tc).mean()
  for i in range(dias_projecao):
    conf7.append(conf7[-1]*tc)
  
  df_pred = pd.DataFrame(columns=df.columns)
  df_pred[column] = conf7[-dias_projecao:]
  ultima_data = df['Data'].to_numpy()[-1]

  ultima_data = datetime.strptime(ultima_data+'/2020', '%d/%m/%Y')
  futuro = [ultima_data + timedelta(days=i) for i in range(1, dias_projecao+1) ]
  df_pred['Data'] = [f.strftime("%d/%m") for f in futuro]
  #############################

  # fig = df.plot.bar(x='Data', y=column)
  fig = go.Figure([go.Bar(x=df['Data'], y=df[column], name=filename.capitalize())])
  fig.update_traces(marker_color=color)
  fig.update_xaxes(tickangle=-90)
  
  fig_pred = go.Figure([go.Bar(x=df_pred['Data'], y=df_pred[column], name='Projeção para os próximos 7 dias')])
  fig_pred.update_traces(marker_color='silver')
  fig.add_trace(fig_pred.data[0])

  fig.update_layout(title=title, title_x=0.5,title_y=0.85, width=850, height=500, 
                    showlegend=True, legend_orientation="h", legend=dict(x=0.25, y=1.01))

  fig.write_html(os.path.join(save_path, filename+'.html'))
  fig.show()

plot_acumulado("Confirmados", 'casos', "Casos acumulados no Brasil", 'royalblue', 7)
plot_acumulado("Mortes", 'obitos', "Óbitos acumulados no Brasil", 'darkred', 7)

df['Casos por dia'] = df['Confirmados'].diff()
df['Mortes por dia'] = df['Mortes'].diff()

def plot_pordia(column, filename, color):
  fig = df.plot.bar(x='Data', y=column)
  fig.update_traces(marker_color=color)
  fig.update_xaxes(tickangle=-90)

  fig.update_layout(title=column, title_x=0.5,title_y=0.92, width=800, height=450)

  fig.write_html(os.path.join(save_path, filename+'.html'))
  fig.show()

plot_pordia('Mortes por dia', 'obitos-por-dia', 'darkred')
plot_pordia('Casos por dia', 'casos-por-dia', 'royalblue')

"""# Estados"""

print("Starting Brazil per state")
pop_estado = {
    'Rondônia': 1749000,
    'Acre': 790101,
    'Amazonas': 3874000,
    'Roraima': 496936,
    'Pará': 8074000,
    'Amapá': 751000,
    'Tocantins': 1497000,
    'Maranhão': 6851000,
    'Piauí': 3195000,
    'Ceará': 8843000,
    'Rio Grande do Norte': 3409000,
    'Paraíba': 3944000,
    'Pernambuco': 9278000,
    'Alagoas': 3322000,
    'Sergipe': 2220000,
    'Bahia': 15130000,
    'Minas Gerais': 20870000,
    'Espírito Santo': 3885000,
    'Rio de Janeiro': 16460000,
    'São Paulo': 44040000,
    'Paraná': 11080000,
    'Santa Catarina': 6727000,
    'Rio Grande do Sul': 11290000,
    'Mato Grosso do Sul': 2620000,
    'Mato Grosso': 3224000,
    'Goiás': 6523000,
    'Distrito Federal': 2570000,
}

df = pd.DataFrame(columns=['Data', 'Estado', 'Ministério', 'Óbitos'])

for csv in sorted(os.listdir(root_path))[6:-1]:

  df_dia = pd.read_csv(os.path.join(root_path, csv))
  df_dia.columns = df_dia.iloc[2]
  df_dia.drop([0,1,2, 30], inplace=True)
  df_dia.drop('Secretarias', axis=1, inplace=True)

  df_dia['Data'] = [csv.split('.')[0]] * len(pop_estado)

  if 'Óbitos' not in df_dia.columns:
    df_dia['Óbitos'] = [np.nan] * len(pop_estado)

  df = df.append(df_dia)

display(df.tail())

def fill_df(column):
  df = pd.DataFrame()
  datas = []
  for csv in sorted(os.listdir(root_path))[6:-1]:
    
    datas.append(csv.split('.')[0])
    df_dia = pd.read_csv(os.path.join(root_path, csv))
    df_dia = df_dia.T
    df_dia.index = df_dia.iloc[:, 2]
    df_dia.drop([0,1,2, 30], axis=1, inplace=True)
    df_dia.columns = df_dia.loc['Estado']
    df_dia.drop('Estado', inplace=True)
    
    if column not in df_dia.index:
      row=pd.DataFrame([[np.nan] * 27], columns=df_dia.columns)

    else:    
      row = df_dia.loc[column]

    df = df.append(row)


  df['Data'] = datas
  return df

df_casos = fill_df('Ministério')
df_obitos = fill_df('Óbitos')
display(df_casos.tail())
display(df_obitos.tail())

# Remover quando atualizar dias 5 e 6
# verificar se é necessário manter o to_numeric
# df_casos = df_casos.iloc[:-4]
# df_obitos = df_obitos.iloc[:-4]
df_casos_diff = df_casos.copy()
df_obitos_diff = df_obitos.copy()

for estado in df_casos.columns[:-1]:
  df_casos.loc[:,estado] = pd.to_numeric(df_casos[estado])
  df_obitos.loc[:,estado] = pd.to_numeric(df_obitos[estado])

  df_casos_diff[estado] = df_casos[estado].diff()
  df_obitos_diff[estado] = df_obitos[estado].diff()

buttons_list = []
for estado in df_casos.columns[:-1]:
  button_dict = {}
  button_dict['args'] = [{'y': [df_casos[estado], df_obitos[estado], df_casos_diff[estado],df_obitos_diff[estado]]}, 
                          ]
  button_dict['label'] = estado.split('(')[0].rstrip()
  button_dict['method'] = 'update'
  buttons_list.append(button_dict)

fig = make_subplots(rows=2, cols=2)

fig1 = df_casos.plot(x='Data', y='Acre (AC)')
fig1.update_traces(mode="markers+lines", hovertemplate=None,
                   marker=dict(size=3, color='white'), line=dict(width=5, color='royalblue'))
fig.add_trace(fig1.data[0],row=1,col=1)

fig2 = df_obitos.plot(x='Data', y='Acre (AC)')
fig2.update_traces(mode="markers+lines", hovertemplate=None, 
                   marker=dict(size=3, color='white'), line=dict(width=5, color='orangered'))
fig.add_trace(fig2.data[0],row=1,col=2)

fig3 = df_casos_diff.plot(x='Data', y='Acre (AC)')
fig3.update_traces(mode="markers+lines", hovertemplate=None,
                  marker=dict(size=3, color='white'), line=dict(width=4, color='dodgerblue'))
fig.add_trace(fig3.data[0],row=2,col=1)

fig4 = df_obitos_diff.plot(x='Data', y='Acre (AC)')
fig4.update_traces(mode="markers+lines", hovertemplate=None,
                   marker=dict(size=3, color='white'), line=dict(width=4, color='salmon'))
fig.add_trace(fig4.data[0],row=2,col=2)

fig.update_layout(
    width=950,
    height=775,
    yaxis_title = 'Casos Acumulados',
    yaxis2_title = 'Óbitos Acumulados',
    yaxis3_title = 'Casos por dia',
    yaxis4_title = 'Óbitos por dia',
    hovermode = 'x unified',
    title = { 'text': 'Selecione o estado: ', 'font':{'size':16} },
    title_y = 0.93,
    # title_x = 0.5,
    updatemenus=[
          dict(
            type = "dropdown",
            buttons=buttons_list,
            direction="down",
            pad={"r": 10, "t": 10},
            x=0.16,
            xanchor="left",
            y=1.1,
            yanchor="top"
          ),
    ]
)

fig.write_html(os.path.join(save_path, 'resumo-por-estado.html'))
fig.show()

"""## Totais e por milhão"""

ultimo_dia = sorted(os.listdir(root_path))[-2]
df = pd.read_csv(os.path.join(root_path, ultimo_dia))

def por_milhao(estados, numeros):

  # print(estados, numeros)
  for k, estado in enumerate(estados):
    e = estado.split('(')[0].rstrip()

    pop = pop_estado[e]/1000000
    numeros[k] = numeros[k]/pop 

  # print(numeros)
  return numeros

columns = df.iloc[2]
df.drop([0,1,2,30], inplace=True)
df.columns = columns

ultimo_dia

def plot_estado(df, column, filename, title, colors):

  df[column] = pd.to_numeric(df[column])
  df = df.sort_values(column, ascending=True)

  numeros = df[column].to_numpy(copy=True)
  pormilhao = por_milhao(df['Estado'], numeros)
  df['Por milhão'] = pormilhao

  ticks = [estado.split('(')[-1][:2] for estado in df['Estado'].to_numpy()]
  df['Estado'] = ticks

  fig = make_subplots(rows=1, cols=2)

  fig1 = df.plot.barh(x=column, y='Estado', text=column)
  fig1.update_traces(marker_color=colors[0])
  fig.add_trace(fig1.data[0], row=1, col=1)

  fig2 = df.plot.barh(x='Por milhão', y='Estado', text='Por milhão')
  fig2.update_traces(marker_color=colors[1])
  fig.add_trace(fig2.data[0], row=1, col=2)
  
  # fig.update_traces(textposition='outside')
  fig.update_layout(width=950, height=650,margin=dict(t=50),
                    annotations=[ dict(x=0., y=1.05, text=title+' totais', showarrow=False, 
                                       xref='paper', yref='paper', font=dict(size=18)), 
                                 dict(x=0.9, y=1.05, xref='paper', yref='paper', font=dict(size=18),
                                      text=title+' por milhão de habitantes',  showarrow=False), ])
  fig.update_xaxes(nticks=10)
  fig.write_html(os.path.join(save_path, filename+'.html'))
  fig.show()

plot_estado(df, 'Secretarias', 'casos-por-estado', 'Casos', ['royalblue', 'deepskyblue'])
plot_estado(df, 'Óbitos', 'obitos-por-estado', 'Óbitos', ['darkred', 'salmon'])

from shutil import rmtree
rmtree('COVID-19-master/')

"""# Mundo"""

print("Starting world data")
import requests, zipfile, io

csse_path = "https://github.com/CSSEGISandData/COVID-19/archive/master.zip"

r = requests.get(csse_path, stream=True)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

root_path = 'COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/'

recent = sorted(os.listdir(root_path))[-2]
path = os.path.join(root_path, recent)
df = pd.read_csv(path)
# print(df.shape)
# display(df)
name = [c for c in df.columns if "Country" in c]
countries = df[name[0]].to_numpy()
countries = np.unique(countries) 
# print(np.unique(countries))

dates = []
for k, csv in enumerate(sorted(os.listdir(root_path))):
  if not csv[-3:] == 'csv': continue
  dates.append(  '/'.join(csv.split('-')[::-1][1:] ) )

ts = {'Deaths': {}, 'Confirmed': {}}
for country in np.unique(countries):
  ts['Deaths'][country] = []
  ts['Confirmed'][country] = []

for k, csv in enumerate(sorted(os.listdir(root_path))):
  print('\r{0}/{1}'.format(k, len(os.listdir(root_path))), end='', flush=True )
  if not csv[-3:] == 'csv': continue

  path = os.path.join(root_path, csv)
  df = pd.read_csv(path)

  for country in np.unique(countries):
    try:
      name = [c for c in df.columns if "Country" in c]
      ts['Deaths'][country].append(df[df[name[0]].str.contains(country)].sum()['Deaths'])
      ts['Confirmed'][country].append(df[df[name[0]].str.contains(country)].sum()['Confirmed'])
    except:
      ts['Deaths'][country].append(0)
      ts['Confirmed'][country].append(0)

df_deaths = pd.DataFrame.from_dict(ts['Deaths'])
df_deaths = df_deaths.sort_values(df_deaths.shape[0]-1, axis=1, ascending=False)

df_confirmed = pd.DataFrame.from_dict(ts['Confirmed'])
df_confirmed = df_confirmed.sort_values(df_confirmed.shape[0]-1, axis=1, ascending=False)

def plot_world(df, column, title, filename):
  df = df.loc[:, df.columns[:10]]
  df['Date'] = dates
  df = df.loc[30:]
  df = df.melt('Date', var_name='Country', value_name=column)

  fig = df.plot(x='Date', y=column, color='Country',)
  for data in fig.data:
    color = data.line.color
    data.update(mode='markers+lines', marker=dict(size=4, color='white'), line=dict(width=5), hoverlabel=dict(bgcolor=color))
  
  fig.update_layout(title=title, title_x=0.5, width=950, height=550,
                    )

  fig.update_layout(
    updatemenus=[
        dict( buttons=list([
            dict(label="Linear",  
                method="relayout", 
                args=[{"yaxis.type": "linear"}]),
            dict(label="Log", 
                method="relayout", 
                args=[{"yaxis.type": "log"}]),
        ]),
        x=0.13,
        y=0.98
        )
        
    ])

  fig.write_html(os.path.join(save_path, filename+'.html'))
  fig.show()

plot_world(df_deaths, 'Deaths', 'Óbitos acumulados nos 10 países mais afetados', 'obitos-mundo')
plot_world(df_confirmed, 'Confirmed', 'Casos acumulados nos 10 países mais afetados', 'casos-mundo')

def plot_mundo_pordia(df, column, title, filename):
  countries_confirmed = df.columns[:10] #['Italy','Germany', 'United Kingdom','India','US', 'Brazil']
  df_ = pd.DataFrame(columns=countries_confirmed)

  for k, country in enumerate(countries_confirmed):
    df_[country] = df[country].diff()
    df_[country] = df_[country].rolling(8).mean()

  df_['Data'] = dates
  df_ = df_.iloc[30:]
  # if 'Spain' in df.columns: df_.drop('Spain', axis=1, inplace=True)
  # if 'France' in df.columns: df_.drop('France', axis=1, inplace=True)
  
  dfm = df_.melt('Data', var_name='Country', value_name=column)
  
  fig = dfm.plot(x='Data', y=column, color='Country',)

  for data in fig.data:
    color = data.line.color
    data.update(mode='markers+lines', marker=dict(size=3, color='white'), line=dict(width=5), hoverlabel=dict(bgcolor=color))
  
  fig.update_layout(title=title, title_x=0.5, width=950, height=550,)

  fig.write_html(os.path.join(save_path, filename+'.html'))
  fig.show()


plot_mundo_pordia(df_confirmed, 'Casos por dia', 'Casos por dia nos países mais afetados', 'casos-mundo-por-dia')
plot_mundo_pordia(df_deaths, 'Óbitos por dia', 'Óbitos por dia nos países mais afetados','obitos-mundo-por-dia')

rmtree("COVID-19-master")

!zip includes.zip *.html
