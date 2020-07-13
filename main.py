'''

Tutorial sobre como usar Pyhton para analisar uma base de dados de jogadores do FIFA 2018

Criado em 12/05/2018

'''

import pandas as pd
import re
from bokeh.charts import Histogram, show
import seaborn as sns
import numpy as np

#fonte: https://www.kaggle.com/thec03u5/fifa-18-demo-player-dataset
data = pd.read_csv('C:\\Users\\Gabriel Luz\\Desktop\\DataScience\\Projetos\\03\\fifa-18-demo-player-dataset\\CompleteDataset.csv', sep=',', encoding='utf-8')

#excluindo algumas colunas que não são de interesse
data.drop(['Unnamed: 0','Photo','Flag','Club Logo'], axis = 1, inplace = True)

#renomeando a coluna Wage para salario e alterando-a para ser do tipo numérico
data['salario'] = data['Wage'].map(lambda x : re.sub('[^0-9]+', '', x)).astype('float64')

data.Agility.astype(int)

#colocando colunas estranhas para o formato desejado
def transform(value):
   out = str(value)
   if '+' in out:
      a,b = out.split('+')
      out = int(a)+int(b)
   elif '-' in out:
      a,b = out.split('-')
     if len(a)== 0: out = -1
     else: out = int(a)-int(b)
  elif out == '':
      out = 0
return float(out)

#quantidade total de países
#a função nunique retorna a quantidade de valores únicos em um objeto
data.Nationality.nunique()

#países com maior número de jogadores
#1
data['Nationality'].value_counts()
#2
pd.value_counts(data['Nationality'])

#media de idades
data.Age.mean()

#quantidade de jogadores por idade
data['Age'].value_counts()

#media de idade por club
mediaPorClub = data.groupby('Club').Age.mean()

#media de salario/semana
data.salario.mean()

#média de salário por clube
mediaSalarioPorClub = data.groupby('Club').salario.mean()

#quanto cada clube gasta com salarios
#o sort_values foi usado para ordenar os valores do maior para o menor
gastoComSalario = data.groupby('Club').salario.sum().sort_values(ascending = False)

#overall por idade
RatingPorIdade = data.groupby('Age').Overall.agg(['min','max','mean'])

#potencial por idade
potencialPorIdade = data.groupby('Age').Potential.agg(['min','max','mean'])

#Quais clubes possuem as melhores médias de Overall?
mediaOverallPorClub = data.groupby('Club').Overall.mean().sort_values(ascending = False)

#Quais os jogadores com maior precisão de cabeceio?
cabeceio = data.sort_values(by='Heading accuracy',ascending = False)

#Goleiros com melhores reflexos
data['posicao'] = data['Preferred Positions']
goleiros = data[data.posicao.str.contains('GK')== True]
reflexosMelhoresGoleiros = goleiros.sort_values(by='GK reflexes',ascending = False )

#Quais os jogadores com maior potencia de chute?
potenciaChute = data.sort_values(by='Shot power',ascending = False )

#Quais os jogadores mais rápidos?
velocidade = data.sort_values(by='Sprint speed',ascending = False )

#Qual é o melhor time?
data['Preferred Position'] = data['Preferred Positions'].str.split().str[0]

def get_best_squad(position):
    data_copy = data.copy()
    store = []
    for i in position:
       store.append([i,data_copy.loc[[data_copy[data_copy['Preferred  Position']    == i]['Overall'].idxmax()]]['Name'].to_string(index = False),       data_copy[data_copy['Preferred Position'] == i]['Overall'].max()])
       data_copy.drop(data_copy[data_copy['Preferred Position'] == i]['Overall'].idxmax(), inplace = True)
    #return store
    return pd.DataFrame(np.array(store).reshape(11,3), columns = ['Position', 'Player', 'Overall']).to_string(index = False)

# 4-3-3
squad_433 = ['GK', 'LB', 'CB', 'CB', 'RB', 'LM', 'CDM', 'RM', 'LW', 'ST', 'RW']
print ('4-3-3')
print (get_best_squad(squad_433))

#para o esquema 3-5-2
squad_352 = ['GK', 'LWB', 'CB', 'RWB', 'LM', 'CDM', 'CAM', 'CM', 'RM', 'LW', 'RW']
print ('3-5-2')
print (get_best_squad(squad_352))

#Visualizações

#distribuições
data.Age.plot(kind='hist', bins=20)
data.Overall.plot(kind='hist', bins=20)

#histograma melhorado
# entre os melhores times
melhoresClubs = data[(data.Club == 'FC Barcelona') | (data.Club == 'Juventus') | (data.Club == 'Real Madrid CF') | (data.Club == 'FC Bayern Munich') | (data.Club == 'Paris Saint-Germain') ]
hist = Histogram(data=melhoresClubs, values="Age", color="Club", legend="top_right", bins=12)
show(hist)

#box plot para analisar salarios dos melhores clubs
sns.set(style="whitegrid", color_codes=True)
sns.boxplot(x="Club", y="salario", hue="Club", data=melhoresClubs, palette="PRGn")
sns.despine(offset=10, trim=True)

best = data[data['Overall']> 85]
grouped = best.groupby('Club')
count_by_club = grouped.count()['Name'].sort_values(ascending = False)
ax = sns.countplot(x = 'Club', data = best, order = count_by_club.index)
ax.set_xticklabels(labels = count_by_club.index, rotation='vertical')
ax.set_ylabel('Numero de jogadores')
ax.set_xlabel('Clube')
ax.set_title('Clubes com os melhores jogadores')

#Correlações
#criando um novo dataset com os atributos que se deseja avaliar a correlação
analise = data.loc[:,['Age','Overall', 'Potential','salario', 'Agility', 'Finishing', 'Acceleration','Ball control','Free kick accuracy','Jumping', 'Long passing' ]]

#fazendo a matriz de correlação
corr = analise.corr()

#plotando a matriz de correlação
ax = sns.heatmap(corr, xticklabels=corr.columns.values, yticklabels=corr.columns.values,
linewidths=0.25, vmax=1.0, square=True, cmap = 'PuBu', linecolor='black', annot=False)