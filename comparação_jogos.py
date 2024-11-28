import requests
import time
import pandas as pd
import matplotlib.pyplot as plt


app_ids = ["730", "570", "346110", "578080", "1172470", "271590", "2195250"] 
total_desejado = 30000
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


def collect_reviews_and_calculate_percent(app_id):
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    comentarios = []
    cursor = "*"
    
    while len(comentarios) < total_desejado:
        params = {
            "filter": "recent",           
            "language": "all",      
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
            print(f"Sem mais comentários disponíveis para o jogo {app_id}.")
            break

        for comentario in novos_comentarios:
            comentario_filtrado = {
                "review": comentario["review"],  
                "avaliacao": "Positiva" if comentario["voted_up"] else "Negativa"  
            }
            comentarios.append(comentario_filtrado)

        print(f"Coletados {len(comentarios)} comentários para o jogo {app_id}...")

      
        time.sleep(1)

 
    df = pd.DataFrame(comentarios)
    avaliacao_positiva = df[df["avaliacao"] == "Positiva"].shape[0]
    avaliacao_negativa = df[df["avaliacao"] == "Negativa"].shape[0]
    total_comentarios = avaliacao_positiva + avaliacao_negativa
    porcentagem_positiva = (avaliacao_positiva / total_comentarios) * 100
    return get_game_name(app_id), porcentagem_positiva


nomes_jogos = []
porcentagens_positivas = []


for app_id in app_ids:
    nome_jogo, porcentagem = collect_reviews_and_calculate_percent(app_id)
    nomes_jogos.append(nome_jogo)
    porcentagens_positivas.append(porcentagem)


plt.figure(figsize=(10, 6))
bars = plt.barh(nomes_jogos, porcentagens_positivas, color=['#66b3ff', '#ff6666', '#99ff99', '#ffcc99', '#66ff66', '#ffcc00', '#ff3399'])


plt.title('Porcentagem de Avaliações Positivas para Cada Jogo', fontsize=14)
plt.xlabel('Porcentagem de Avaliações Positivas (%)', fontsize=12)


plt.legend(bars, nomes_jogos, title='Jogos', loc='center left', bbox_to_anchor=(1, 0.5))  


for bar, porcentagem in zip(bars, porcentagens_positivas):
    plt.text(bar.get_width() - 10, bar.get_y() + bar.get_height()/2, f'{porcentagem:.1f}%', va='center', ha='right', color='black', fontsize=10)


plt.tight_layout()  
plt.show()
