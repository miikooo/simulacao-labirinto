import statistics
from database.config import Session
from database.models_db import MapaModel, ResultadoModel
from classes.Resultado import Resultado

def salvar_resultados(indice_mapa, jogadores, rodada, spawn_fixo):
    session = Session()
    #busca ordenada por ID para manter a sincronia com a navegação
    todos_mapas: list[MapaModel] = session.query(MapaModel).order_by(MapaModel.id).all()
    mapa_db: MapaModel = todos_mapas[indice_mapa] # type: ignore 

    #converte o booleano de spawn para um texto explicativo
    modo_texto = "Fixo" if spawn_fixo else "Aleatório"

    jogadores_ordenados = sorted(jogadores, key=lambda j: j.tempo) #ordena jogadores pelo tempo

    for posicao, jogador in enumerate(jogadores_ordenados, start=1):
        resultado = ResultadoModel(
            mapa_id=mapa_db.id,
            jogador_nome=jogador.nome,
            tempo=jogador.tempo,
            posicao=posicao,
            #grava a rodada atual e o modo de spawn se as colunas existirem no banco
            rodada=rodada,
            modo=modo_texto,
            #salvando as coordenadas iniciais
            start_l=jogador.start_l,
            start_c=jogador.start_c
        )
        session.add(resultado)

    nome_mapa = mapa_db.nome 
    session.commit()
    session.close()
    print(f"Resultados do {nome_mapa} salvos.")

def buscar_resultados(indice_mapa):
    session = Session()
    #mantém a ordem por ID na busca de histórico também
    todos_mapas: list[MapaModel] = session.query(MapaModel).order_by(MapaModel.id).all()

    if indice_mapa >= len(todos_mapas):
        session.close()
        return [], {}

    mapa_db: MapaModel = todos_mapas[indice_mapa] # type: ignore 
    
    #pega até 40 registros (10 rodadas)
    resultados = (
        session.query(ResultadoModel)
        .filter_by(mapa_id=mapa_db.id)
        .order_by(ResultadoModel.id.desc())
        .limit(40) 
        .all()
    )

    #inverte para a ordem cronológica
    resultados.reverse()

    historico_agrupado = [] 
    ultimo_titulo = None
    grupo_atual = None

    #dicionário agora separa tudo por modo ('Fixo' ou 'Aleatório')
    tempos_por_jogador = {} 

    for r in resultados:
        r_rodada = getattr(r, 'rodada', '?')
        r_modo = getattr(r, 'modo', 'Fixo') # Pega o modo do banco de dados
        
        #cria as chaves do modo e do jogador se não existirem
        if r_modo not in tempos_por_jogador:
            tempos_por_jogador[r_modo] = {}
        if r.jogador_nome not in tempos_por_jogador[r_modo]:
            tempos_por_jogador[r_modo][r.jogador_nome] = []
            
        #adiciona o tempo na lista correta (separando fixo de aleatório)
        tempos_por_jogador[r_modo][r.jogador_nome].append(r.tempo)

        titulo = f"Rodada {r_rodada} ({r_modo})"
        
        if titulo != ultimo_titulo:
            # Salvando o 'modo' dentro do grupo para a interface saber qual estatística puxar
            grupo_atual = {'titulo': titulo, 'modo': r_modo, 'dados': []}
            historico_agrupado.append(grupo_atual)
            ultimo_titulo = titulo
            
        r_start_l = getattr(r, 'start_l', '?')
        r_start_c = getattr(r, 'start_c', '?')
        grupo_atual['dados'].append(Resultado(r.jogador_nome, r.tempo, r.posicao, r_start_l, r_start_c)) # type: ignore

    #calcula a média, desvio padrão e o Coeficiente de Variação (Porcentagem)
    estatisticas = {}
    for modo, jogadores_dict in tempos_por_jogador.items():
        estatisticas[modo] = {}
        for nome, tempos in jogadores_dict.items():
            if len(tempos) >= 2:
                media = statistics.mean(tempos)
                desvio = statistics.stdev(tempos)
                
                #calcula quantos % o desvio representa da média (Coeficiente de Variação)
                porcentagem = (desvio / media) * 100 if media > 0 else 0
                aprovado = porcentagem < 10
                
                estatisticas[modo][nome] = {
                    'media': media,
                    'desvio': desvio,
                    'porcentagem': porcentagem,
                    'aprovado': aprovado
                }

    session.close()
    return historico_agrupado, estatisticas