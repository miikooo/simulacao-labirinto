import pygame
import sys
import random

from classes.Jogador import Jogador, JogadorEsquerda, JogadorRapido, JogadorCuidadoso
from classes.MapaModel import Mapa, salvar_resultados, buscar_resultados

#configs básicas do pygame
pygame.init()
LARGURA, ALTURA = 1600, 1600 
TELA = pygame.display.set_mode((LARGURA, ALTURA)) 
pygame.display.set_caption("corrida até o if")
FONTE = pygame.font.SysFont("Arial", 20)
FONTE_PEQUENA = pygame.font.SysFont("Arial", 16)

CORES_MAPA = {
    0: (255, 255, 255),
    1: (50, 50, 50),
    2: (255, 215, 0), 
    3: (0, 191, 255),
    4: (0, 255, 0)
}

tipos_jogadores = [
    ("normal", Jogador),
    ("esquerda", JogadorEsquerda),
    ("rápido", JogadorRapido),
    ("cuidadoso", JogadorCuidadoso)
]

def gerar_posicao_valida(mapa_atual, min_distancia=15):
    dest_l, dest_c = mapa_atual.encontrar_chegada()
    
    while True:
        l = random.randint(0, mapa_atual.linhas - 1)
        c = random.randint(0, mapa_atual.colunas - 1)
        
        #vrifica se a posição é livre de paredes (valor != 1)
        if mapa_atual.posicao_valida(l, c):
            #|x1 - x2| + |y1 - y2|
            distancia = abs(l - dest_l) + abs(c - dest_c)
            
            if distancia >= min_distancia:
                return l, c

#!!!!!
def criar_jogadores(qtd, mapa_atual, spawn_fixo):
    jogadores = []
    dest_l, dest_c = mapa_atual.encontrar_chegada() #destino é o mesmo pra todos os jogadores, então pode ser calculado uma vez aqui
    selecao_tipos = random.sample(tipos_jogadores, k=qtd) #seleciona aleatoriamente os tipos de jogadores para essa corrida, sem repetir (k=qtd garante isso)

    #todos partem do mesmo ponto ou de posições aleatórias, dependendo do modo
    if spawn_fixo:
        l_inicio, c_inicio = mapa_atual.encontrar_inicio()

    for nome_tipo, Classe in selecao_tipos:
        #no modo aleatório cada jogador recebe uma posição diferente
        if not spawn_fixo:
            l_inicio, c_inicio = gerar_posicao_valida(mapa_atual, min_distancia=20)

        j = Classe( 
            f"{nome_tipo}",
            (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
            l_inicio, c_inicio,
            dest_l, dest_c  
        )
        jogadores.append(j)

    return jogadores


indice_mapa = 0            #controla qual mapa está sendo exibido
resultados_salvos = False  #flag pra não salvar mais de uma vez por partida
spawn_fixo = True          #controla se todos nascem no mesmo ponto ou em posições aleatórias
rodadas_mapa = 0           #conta quantas vezes o mapa atual foi rodado (para os testes com 3 execuções)

mapa = Mapa(indice=indice_mapa)
TAM_CELULA = min(LARGURA // mapa.colunas, (ALTURA - 250) // mapa.linhas) #ajusta o tamanho da célula para caber o mapa na tela
jogadores = criar_jogadores(4, mapa, spawn_fixo)

#retângulo do botão de toggle de spawn fica no canto superior direito
BOTAO_SPAWN = pygame.Rect(LARGURA - 220, 5, 215, 30)

#desenho do mapa
def desenhar():
    TELA.fill((200, 200, 200))

    for l in range(mapa.linhas):
        for c in range(mapa.colunas):
            cor = CORES_MAPA[mapa.get(l, c)]
            pygame.draw.rect(TELA, cor, (c*TAM_CELULA, l*TAM_CELULA, TAM_CELULA, TAM_CELULA))
            pygame.draw.rect(TELA, (0,0,0), (c*TAM_CELULA, l*TAM_CELULA, TAM_CELULA, TAM_CELULA), 1)

    #ajusta o tamanho do jogador dependendo do labirinto
    margem = 5 if TAM_CELULA > 15 else 2
    tam_j = TAM_CELULA - (margem * 2)

    for j in jogadores:
        pygame.draw.rect(TELA, j.cor, (j.c*TAM_CELULA + margem, j.l*TAM_CELULA + margem, tam_j, tam_j))

    #botão de toggle de spawn: verde = fixo, laranja = aleatório
    cor_botao = (60, 180, 60) if spawn_fixo else (210, 120, 30)
    label_botao = "FIXO (1,1) [S]" if spawn_fixo else "ALEATÓRIO [S]"
    pygame.draw.rect(TELA, cor_botao, BOTAO_SPAWN, border_radius=6)
    texto_botao = FONTE_PEQUENA.render(label_botao, True, (255, 255, 255))
    TELA.blit(texto_botao, (BOTAO_SPAWN.x + 8, BOTAO_SPAWN.y + 7))

    #calcula onde o labirinto termina pra começar a área de info logo abaixo
    base = mapa.linhas * TAM_CELULA + 10

    #linha separadora entre o labirinto e a área de informações
    pygame.draw.line(TELA, (100, 100, 100), (0, base - 5), (LARGURA, base - 5), 1)

    #navegação centralizada com nome e tipo do mapa, e contador de rodadas
    instrucao = FONTE.render(
        f"[←]  {mapa.nome} ({mapa.tipo})  [→]    |    [R] reiniciars  —  Rodada {rodadas_mapa}",
        True, (0, 0, 0)
    )
    TELA.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, base + 5))

    #linha divisória vertical entre corrida atual e histórico
    pygame.draw.line(TELA, (150, 150, 150), (LARGURA // 2 - 5, base + 30), (LARGURA // 2 - 5, ALTURA - 5), 1)

    #lado esquerdo: status da corrida atual
    titulo_corrida = FONTE_PEQUENA.render("-- Corrida atual --", True, (50, 50, 50))
    TELA.blit(titulo_corrida, (10, base + 32))
    for i, j in enumerate(jogadores):
        status = f"Fim: {j.tempo} min" if j.venceu else f"Andando: {j.tempo} min"
        texto = FONTE_PEQUENA.render(f"{j.nome}: {status}", True, j.cor)
        TELA.blit(texto, (10, base + 52 + i * 22))

    #lado direito: histórico salvo no banco (só aparece quando todos terminaram)
    if all(j.venceu for j in jogadores):
        historico = buscar_resultados(indice_mapa)
        if historico:
            titulo_hist = FONTE_PEQUENA.render("-- Histórico --", True, (50, 50, 50))
            TELA.blit(titulo_hist, (LARGURA // 2 + 10, base + 32))
            for i, r in enumerate(historico[-6:]):  #mostra os últimos 6 resultados
                linha = FONTE_PEQUENA.render(f"{r['posicao']}º {r['nome']}: {r['tempo']} min", True, (30, 30, 30))
                TELA.blit(linha, (LARGURA // 2 + 10, base + 52 + i * 22))

    pygame.display.update()

def reiniciar_mapa():
    #reinicia os jogadores no mesmo mapa sem trocar de mapa nem resetar o contador
    global jogadores, resultados_salvos, rodadas_mapa
    resultados_salvos = False
    rodadas_mapa += 1
    jogadores = criar_jogadores(4, mapa, spawn_fixo) #cria novos jogadores com as mesmas configurações para a nova rodada
    #spawn_fixo é mantido, então se estava no modo aleatório continua aleatório, e se estava no fixo continua fixo

def trocar_mapa(novo_indice):
    #troca o mapa e reseta tudo, incluindo o contador de rodadas
    global mapa, TAM_CELULA, jogadores, resultados_salvos, rodadas_mapa, indice_mapa
    indice_mapa = novo_indice
    resultados_salvos = False
    rodadas_mapa = 1  #começa na rodada 1 ao entrar num mapa novo
    mapa = Mapa(indice=indice_mapa)
    TAM_CELULA = min(LARGURA // mapa.colunas, (ALTURA - 250) // mapa.linhas) #ajusta o tamanho da célula para caber o novo mapa
    jogadores = criar_jogadores(4, mapa, spawn_fixo)

#inicia o contador na rodada 1
rodadas_mapa = 1

#loop principal
while True:
    desenhar()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.MOUSEBUTTONDOWN:
            #clique no botão de spawn faz o mesmo que pressionar S
            if BOTAO_SPAWN.collidepoint(e.pos): #verifica se o clique foi dentro do retângulo do botão
                spawn_fixo = not spawn_fixo #alterna o modo de spawn
                reiniciar_mapa()

        if e.type == pygame.KEYDOWN:
            #navega para o próximo labirinto gerado no banco
            if e.key == pygame.K_RIGHT:
                trocar_mapa(indice_mapa + 1)

            #navega para o labirinto anterior, não deixa ir abaixo de 0
            elif e.key == pygame.K_LEFT:
                trocar_mapa(max(0, indice_mapa - 1))

            #reinicia a corrida no mesmo mapa (para rodar 3 vezes e comparar)
            elif e.key == pygame.K_r:
                reiniciar_mapa()

            #alterna entre spawn fixo e aleatório sem trocar de mapa
            elif e.key == pygame.K_s:
                spawn_fixo = not spawn_fixo
                reiniciar_mapa()

    #move todos os jogadores que ainda não venceram
    for j in jogadores: 
        if not j.venceu:
            j.pensar_e_mover(mapa)

    #quando todos terminarem e ainda não salvou, salva os resultados no banco
    if all(j.venceu for j in jogadores) and not resultados_salvos:
        salvar_resultados(indice_mapa, jogadores)
        resultados_salvos = True  #garante que só salva uma vez por partida

    pygame.time.delay(600)