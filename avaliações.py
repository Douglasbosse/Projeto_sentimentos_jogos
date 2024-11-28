import requests
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


app_id = "1462040"  
url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
comentarios = []
total_desejado = 100  
num_por_pagina = 100  
cursor = "*"  


def get_game_name(app_id):
    game_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(game_url)
    if response.status_code == 200:
        data = response.json()
        if str(app_id) in data and data[str(app_id)].get('success'):
            return data[str(app_id)]['data'].get('name', 'Desconhecido')
    return 'Desconhecido'


nome_jogo = get_game_name(app_id)

while len(comentarios) < total_desejado:
    params = {
        "filter": "all",            
        "language": "all",      
        "purchase_type": "all",        
        "num_per_page": num_por_pagina,  
        "cursor": cursor               
    }

  
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Erro ao acessar a API: {response.status_code}")
        break

 
    data = response.json()
    novos_comentarios = data.get("reviews", [])
    cursor = data.get("cursor", "*")  

    if not novos_comentarios:
        print("Sem mais comentários disponíveis.")
        break

    for comentario in novos_comentarios:
        comentario_filtrado = {
            "review": comentario["review"],  
            "data": datetime.utcfromtimestamp(comentario["timestamp_created"]).strftime('%Y-%m-%d %H:%M:%S'), 
            "avaliacao": "Positiva" if comentario["voted_up"] else "Negativa" 
        }
        comentarios.append(comentario_filtrado)

    print(f"Coletados {len(comentarios)} comentários até agora...")

  
    time.sleep(1)


comentarios = comentarios[:total_desejado]


print(f"Total de comentários coletados: {len(comentarios)}")


df = pd.DataFrame(comentarios)


avaliacao_positiva = df[df["avaliacao"] == "Positiva"].shape[0]
avaliacao_negativa = df[df["avaliacao"] == "Negativa"].shape[0]


labels = ['Positivas', 'Negativas']
sizes = [avaliacao_positiva, avaliacao_negativa]
colors = ['#66b3ff', '#ff6666']
explode = (0.1, 0)  

plt.figure(figsize=(7, 7))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title(f"Avaliações para o Jogo: {nome_jogo}")
plt.axis('equal')  


total_avaliacoes = avaliacao_positiva + avaliacao_negativa
plt.legend([f'Total de avaliações: {total_avaliacoes}'], loc='upper right', fontsize=10)

plt.show()

df.to_csv("comentarios_cs.csv", index=False, encoding="utf-8", sep=';') 
print("Comentários exportados para 'comentarios_cs.csv'")
