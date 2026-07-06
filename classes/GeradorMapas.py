import random
from database.config import Session
from database.models_db import MapaModel

def gerar_labirinto(linhas=15, colunas=35, tipo="misto"):
    #largura aumentada
    grade = [[1] * colunas for _ in range(linhas)]  

    #cria uma caminho base e depois abre mais ou menos paredes dependendo do tipo
    def esculpir(l, c):
        #visita células criando o caminho base
        direcoes = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(direcoes)
        for dl, dc in direcoes: #para cada direção, tenta esculpir
            nl, nc = l + dl, c + dc #nova posição
            if 0 <= nl < linhas and 0 <= nc < colunas and grade[nl][nc] == 1: #
                grade[l + dl//2][c + dc//2] = 0  #remove a parede entre a célula atual e a nova
                grade[nl][nc] = 0 #marca a nova célula como parte do caminho
                esculpir(nl, nc) 

    grade[1][1] = 0
    esculpir(1, 1)

    if tipo == "bifurcacao":
        #em vez de um caminho único, se ABRE 15% das paredes para criar ciclos e rotas extras
        for l in range(1, linhas - 1):
            for c in range(1, colunas - 1):
                if grade[l][c] == 1 and random.random() < 0.2:  
                    grade[l][c] = 0
    
    elif tipo == "livre":
        # 40% para virar um campo aberto
        for l in range(1, linhas - 1):
            for c in range(1, colunas - 1):
                if grade[l][c] == 1 and random.random() < 0.4: 
                    grade[l][c] = 0

    grade[linhas - 2][colunas - 2] = 4 #destino

    #obstáculos espalhados conforme o tipo
    chance = 0.20 if tipo == "bifurcacao" else 0.10
    for l in range(linhas):
        for c in range(colunas):
            if grade[l][c] == 0 and random.random() < chance:
                grade[l][c] = random.choice([2, 3])

    return grade

def gerar_e_salvar_labirintos():
    session = Session()
    
    # Lista limpa, apenas com os nomes dos cenários
    ordem_cenarios = [
        "Mapa Bifurcado 1",
        "Mapa Bifurcado 2",
        "Mapa Livre 1",
        "Mapa Livre 2",
        "Mapa Meio-Termo 1",
        "Mapa Meio-Termo 2"
    ]

    for nome in ordem_cenarios:
        # Descobre o tipo dinamicamente com base nas palavras do nome
        if "Bifurcado" in nome:
            tipo = "bifurcacao"
        elif "Livre" in nome:
            tipo = "livre"
        else:
            tipo = "misto"

        # Gera e salva usando as variáveis resolvidas acima
        grade = gerar_labirinto(tipo=tipo)
        novo_mapa = MapaModel(nome=nome, tipo=tipo, grade=grade)
        session.add(novo_mapa)
    
    session.commit()
    session.close()
    print("Mapas criados na ordem fixa com nomes específicos.")

#função de adicionar mapa
def popular_banco_se_vazio():
    session = Session()
    if session.query(MapaModel).count() == 0:
        session.close()
        gerar_e_salvar_labirintos() 
    else:
        session.close()