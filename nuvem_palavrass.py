import requests
import time
from datetime import datetime
import pandas as pd
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import string
from langdetect import detect
from collections import Counter


nltk.download('punkt')
nltk.download('stopwords')


def get_game_name(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if str(app_id) in data and data[str(app_id)].get('success'):
            return data[str(app_id)]['data'].get('name', 'Desconhecido')
    return 'Desconhecido'

def preprocess_comment(comment):
   
    tokens = nltk.word_tokenize(comment.lower()) 
  
    stop_words = set(nltk.corpus.stopwords.words('portuguese'))
    stop_words.update(["não", "nao"])  
  
    tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
    
   
    tokens = [word for word in tokens if len(word) > 1 and word.isalpha()]
    
    return tokens


def is_portuguese(comment):
    try:
        return detect(comment) == 'pt'  
    except:
        return False  


app_ids = ["1462040"]  
total_desejado = 5000
num_por_pagina = 100  
cursor = "*"  
todos_comentarios = [] 


all_words = []


for app_id in app_ids:
    print(f"Iniciando coleta de comentários para o jogo com AppID {app_id}...")

   
    nome_jogo = get_game_name(app_id)

    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    comentarios_jogo = [] 

    while len(comentarios_jogo) < total_desejado:
        params = {
            "filter": "recent",
            "language": "portuguese",  
            "purchase_type": "all",    
            "num_per_page": num_por_pagina,  
            "cursor": cursor  
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Erro ao acessar a API para o jogo {app_id}: {response.status_code}")
            break

      
        data = response.json()
        novos_comentarios = data.get("reviews", [])
        cursor = data.get("cursor", "*")  

        if not novos_comentarios:
            print(f"Sem mais comentários para o jogo {app_id}.")
            break

        for comentario in novos_comentarios:
            comentario_texto = comentario["review"]

           
            if is_portuguese(comentario_texto) and comentario_texto.strip():
                comentario_filtrado = {
                    "nome_jogo": nome_jogo,
                    "review": comentario_texto,
                    "data": datetime.utcfromtimestamp(comentario["timestamp_created"]).strftime('%Y-%m-%d %H:%M:%S'),
                    "avaliacao": "Positiva" if comentario["voted_up"] else "Negativa"
                }
                comentarios_jogo.append(comentario_filtrado)

             
                words = preprocess_comment(comentario_texto)
                all_words.extend(words)

        print(f"Coletados {len(comentarios_jogo)} comentários para o jogo {nome_jogo} até agora...")

        if cursor == "*":  
            break  

        time.sleep(1)  

  
    todos_comentarios.extend(comentarios_jogo)

 
    print(f"Total de comentários coletados para o jogo {nome_jogo}: {len(comentarios_jogo)}")


df = pd.DataFrame(todos_comentarios)


df.to_csv("comentarios_multijogos.csv", index=False, encoding="utf-8", sep=';')
print("Todos os comentários exportados para 'comentarios_multijogos.csv'")


word_counts = Counter(all_words)


wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)


plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title(f"Nuvem de Palavras dos Comentários - {nome_jogo}", fontsize=18)
plt.show()
