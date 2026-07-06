import pygame
import sys
import random

from database.config import init_db
from classes.Jogador import Jogador, JogadorEsquerda, JogadorRapido, JogadorCuidadoso
from classes.MapaModel import Mapa
from classes.GeradorMapas import popular_banco_se_vazio
from classes.Historico import salvar_resultados, buscar_resultados

#garante que o banco exista e esteja populado antes de o Pygame iniciar
init_db()
popular_banco_se_vazio()

#configs básicas do pygame
pygame.init()

LARGURA, ALTURA = 1600, 950 
TELA = pygame.display.set_mode((LARGURA, ALTURA)) 
pygame.display.set_caption("corrida até o if")
FONTE = pygame.font.SysFont("Arial", 20)
FONTE_PEQUENA = pygame.font.SysFont("Consolas", 16)

OVERLAY_SCANLINE = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
OVERLAY_SCANLINE.fill((0, 0, 0, 0)) # Fundo totalmente transparente

# Desenha as linhas horizontais
# O passo '3' define o espaçamento. O valor '40' define a opacidade (0-255).
for y in range(0, ALTURA, 3):
    pygame.draw.line(OVERLAY_SCANLINE, (0, 0, 0, 40), (0, y), (LARGURA, y), 1)

CORES_MAPA = {
    0: (230, 224, 197),
    1: (62, 55, 66), 
    2: (235, 196, 169),
    3: (107, 123, 140),
    4: (130, 94, 101)
}

CORES_JOGADORES = {
    "normal": (220, 80, 80),     # Vermelho Retrô
    "esquerda": (80, 200, 120),  # Verde Terminal
    "rápido": (240, 180, 50),    # Amarelo Arcade
    "cuidadoso": (100, 150, 220) # Azul Elétrico
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
        # no modo aleatório cada jogador recebe uma posição diferente
        if not spawn_fixo:
            l_inicio, c_inicio = gerar_posicao_valida(mapa_atual, min_distancia=20)

        j = Classe( 
            f"{nome_tipo}",
            CORES_JOGADORES[nome_tipo], # <-- Puxa a cor vibrante que definimos!
            l_inicio, c_inicio,
            dest_l, dest_c  
        )
        jogadores.append(j)

    return jogadores

indice_mapa = 0            #controla qual mapa está sendo exibido
resultados_salvos = False  #flag pra não salvar mais de uma vez por partida
spawn_fixo = True          #controla se todos nascem no mesmo ponto ou em posições aleatórias
rodadas_mapa = 0           #conta quantas vezes o mapa atual foi rodado (para os testes com 3 execuções)

botoes_historico = []            # guarda os retângulos das caixinhas para o clique
indice_rodada_selecionada = None # controla qual aba está aberta no momento

mapa = Mapa(indice=indice_mapa)
TAM_CELULA = min(LARGURA // mapa.colunas, (ALTURA - 250) // mapa.linhas) #ajusta o tamanho da célula para caber o mapa na tela
jogadores = criar_jogadores(4, mapa, spawn_fixo)

#retângulo do botão de toggle de spawn fica no canto superior direito
BOTAO_SPAWN = pygame.Rect(LARGURA - 220, 5, 215, 30)

#desenho do mapa
def desenhar():
    TELA.fill((235, 196, 169))

    for l in range(mapa.linhas):
        for c in range(mapa.colunas):
            cor = CORES_MAPA[mapa.get(l, c)]
            pygame.draw.rect(TELA, cor, (c*TAM_CELULA, l*TAM_CELULA, TAM_CELULA, TAM_CELULA))
            pygame.draw.rect(TELA, (0,0,0), (c*TAM_CELULA, l*TAM_CELULA, TAM_CELULA, TAM_CELULA), 1)

    #ajusta o tamanho do jogador dependendo do labirinto
    margem = 5 if TAM_CELULA > 15 else 2
    tam_j = TAM_CELULA - (margem * 2)

    for j in jogadores:
        # 1. Desenha o quadrado do jogador
        x_jogador = j.c * TAM_CELULA + margem
        y_jogador = j.l * TAM_CELULA + margem
        pygame.draw.rect(TELA, j.cor, (x_jogador, y_jogador, tam_j, tam_j))
        
        # 2. Pega a primeira letra do nome (ex: 'N' para normal, 'E' para esquerda)
        letra = j.nome[0].upper()
        
        # 3. Renderiza a letra com uma cor bem escura para dar leitura
        texto_letra = FONTE_PEQUENA.render(letra, True, (30, 30, 30))
        
        # 4. Calcula a posição para a letra ficar perfeitamente centralizada no quadrado
        letra_x = x_jogador + (tam_j // 2) - (texto_letra.get_width() // 2)
        letra_y = y_jogador + (tam_j // 2) - (texto_letra.get_height() // 2)
        
        TELA.blit(texto_letra, (letra_x, letra_y))

    #calcula onde o labirinto termina pra começar a área de info logo abaixo
    base = mapa.linhas * TAM_CELULA + 10

    #linha separadora entre o labirinto e a área de informações
    pygame.draw.line(TELA, (100, 100, 100), (0, base - 5), (LARGURA, base - 5), 1)

    #navegação centralizada com nome e tipo do mapa, e contador de rodadas
    instrucao = FONTE.render(
        f"[←]  {mapa.nome}  [→]    |    [R] reiniciar  —  Rodada {rodadas_mapa}",
        True, (62, 55, 66)
    )
    TELA.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, base + 5))

    # --- ARQUITETURA DO PAINEL EM 3 COLUNAS VISUAIS (Abaixo da linha divisória) ---
    y_paineis = base + 35

    # Divisória Vertical 1 (Separa Corrida Atual do Histórico)
    pygame.draw.line(TELA, (150, 150, 150), (420, y_paineis), (420, ALTURA - 10), 1)
    
    # Divisória Vertical 2 (Separa Histórico do Teste de Hipótese)
    pygame.draw.line(TELA, (150, 150, 150), (980, y_paineis), (980, ALTURA - 10), 1)

    # ================= COLUNA 1: CORRIDA ATUAL =================
    titulo_corrida = FONTE_PEQUENA.render("-- Corrida atual --", True, (50, 50, 50))
    TELA.blit(titulo_corrida, (20, y_paineis))
    for i, j in enumerate(jogadores):
        status = f"Fim: {j.tempo} min" if j.venceu else f"Andando: {j.tempo} min"
        
        rect_jogador = pygame.Rect(20, y_paineis + 25 + i * 28, 380, 24)
        pygame.draw.rect(TELA, j.cor, rect_jogador, border_radius=4)
        
        texto = FONTE_PEQUENA.render(f" {j.nome.upper()}: {status} ", True, (255, 255, 255))
        TELA.blit(texto, (25, y_paineis + 28 + i * 28))

    # ================= LADO DIREITO (Histórico disponível após fim da prova) =================
    if all(j.venceu for j in jogadores):
        historico, estatisticas = buscar_resultados(indice_mapa)
        
        if historico:
            global botoes_historico, indice_rodada_selecionada
            botoes_historico.clear() # limpa os botões antigos a cada frame desenhado
            
            # Se não tiver nenhuma aba selecionada, foca na mais recente
            if indice_rodada_selecionada is None or indice_rodada_selecionada >= len(historico):
                indice_rodada_selecionada = len(historico) - 1
                
            # ================= COLUNA 2: HISTÓRICO DE RODADAS =================
            titulo_hist = FONTE_PEQUENA.render("-- Histórico de Rodadas --", True, (50, 50, 50))
            TELA.blit(titulo_hist, (440, y_paineis))
            
            x_btn = 440
            y_btn = y_paineis + 25
            
            # desenha as caixinhas/abas lado a lado
            for i, group in enumerate(historico):
                texto_btn = FONTE_PEQUENA.render(group['titulo'], True, (255, 255, 255))
                largura_btn = texto_btn.get_width() + 16 # espaço interno do botão
                
                # se a caixinha for passar da linha divisória central, pula linha
                if x_btn + largura_btn > 970:
                    x_btn = 440
                    y_btn += 32
                    
                rect_btn = pygame.Rect(x_btn, y_btn, largura_btn, 24)
                botoes_historico.append((rect_btn, i)) # salva para o evento de clique
                
                # cor diferente se for a aba selecionada atual
                cor_btn = (60, 120, 180) if i == indice_rodada_selecionada else (150, 150, 150)
                
                pygame.draw.rect(TELA, cor_btn, rect_btn, border_radius=5)
                TELA.blit(texto_btn, (x_btn + 8, y_btn + 2))
                
                x_btn += largura_btn + 8 # avança o X para a próxima caixinha
            
            # Resultados específicos da rodada clicada posicionados logo abaixo das abas
            y_resultados = y_btn + 35
            grupo_sel = historico[indice_rodada_selecionada]
            
            rect_tabela_hist = pygame.Rect(440, y_resultados, 520, 130)
            pygame.draw.rect(TELA, (230, 224, 197), rect_tabela_hist) 
            pygame.draw.rect(TELA, (62, 55, 66), rect_tabela_hist, 2) 

            texto_sel = FONTE_PEQUENA.render(f"Resultados: {grupo_sel['titulo']}", True, (62, 55, 66))
            TELA.blit(texto_sel, (455, y_resultados + 10))
            
            pygame.draw.line(TELA, (62, 55, 66), (440, y_resultados + 33), (960, y_resultados + 33), 2)
            
            for i, r in enumerate(grupo_sel['dados']):
                linha = FONTE_PEQUENA.render(r.formatar_para_tela(), True, (62, 55, 66))
                TELA.blit(linha, (455, y_resultados + 43 + i * 20))

            # ================= COLUNA 3: TESTE DE HIPÓTESE (GRID DE CARDS MODERNOS) =================
            modo_selecionado = grupo_sel.get('modo', 'Fixo')
            titulo_estat = FONTE_PEQUENA.render(f"-- Teste de Hipótese: Modo {modo_selecionado} (<10%) --", True, (50, 50, 50))
            TELA.blit(titulo_estat, (1000, y_paineis))
            
            # Puxa apenas os cálculos correspondentes ao modo da rodada clicada
            estatisticas_modo = estatisticas.get(modo_selecionado, {})
            
            if i_estat_dict := estatisticas_modo:
                # 1. Desenha o fundo de uma tabela única
                rect_tabela = pygame.Rect(1000, y_paineis + 25, 560, 130)
                pygame.draw.rect(TELA, (230, 224, 197), rect_tabela) # Fundo bege claro da paleta
                pygame.draw.rect(TELA, (62, 55, 66), rect_tabela, 2) # Borda escura e reta
                
                # 2. Cabeçalho da tabela
                cabecalho = FONTE_PEQUENA.render("JOGADOR      |   DESVIO / VARIAÇÃO   |   STATUS", True, (62, 55, 66))
                TELA.blit(cabecalho, (1015, y_paineis + 35))
                
                # Linha separadora do cabeçalho (dupla para dar charme)
                pygame.draw.line(TELA, (62, 55, 66), (1000, y_paineis + 58), (1560, y_paineis + 58), 2)
                
                # 3. Preenche as linhas da tabela
                for idx, (nome_player, dados_estat) in enumerate(i_estat_dict.items()):
                    y_linha = y_paineis + 68 + (idx * 20)
                    
                    # Coluna 1: Nome do jogador
                    texto_nome = FONTE_PEQUENA.render(f"{nome_player.upper()}", True, (62, 55, 66))
                    TELA.blit(texto_nome, (1015, y_linha))
                    
                    # Coluna 2: Dados numéricos
                    texto_dados = FONTE_PEQUENA.render(f"{dados_estat['desvio']:.1f} ({dados_estat['porcentagem']:.1f}%)", True, (100, 100, 100))
                    TELA.blit(texto_dados, (1160, y_linha))
                    
                    # Coluna 3: Status (usando colchetes para vibe de terminal)
                    status_texto = "[ OK ]" if dados_estat['aprovado'] else "[ ALTO ]"
                    cor_status = (60, 120, 60) if dados_estat['aprovado'] else (180, 60, 60)
                    
                    texto_status = FONTE_PEQUENA.render(status_texto, True, cor_status)
                    TELA.blit(texto_status, (1370, y_linha))
            else:
                aviso = FONTE_PEQUENA.render(f"Aguardando mais rodadas do modo {modo_selecionado}...", True, (120, 120, 120))
                TELA.blit(aviso, (1000, y_paineis + 28))
        else:
            aviso = FONTE_PEQUENA.render(f"Aguardando mais rodadas do modo {modo_selecionado}...", True, (120, 120, 120)) # type: ignore
            TELA.blit(aviso, (1000, y_paineis + 28))

    pygame.draw.rect(TELA, (62, 55, 66), BOTAO_SPAWN, border_radius=5)
    texto_modo = "Fixo" if spawn_fixo else "Aleatório"
    texto_btn_spawn = FONTE_PEQUENA.render(f"Spawn: {texto_modo} [S]", True, (230, 224, 197))
    TELA.blit(texto_btn_spawn, (BOTAO_SPAWN.x + 15, BOTAO_SPAWN.y + 7))

    TELA.blit(OVERLAY_SCANLINE, (1, 1))

    pygame.display.update()

def reiniciar_mapa():
    #reinicia os jogadores no mesmo mapa sem trocar de mapa nem resetar o contador
    global jogadores, resultados_salvos, rodadas_mapa, indice_rodada_selecionada
    resultados_salvos = False
    indice_rodada_selecionada = None # reseta a caixinha selecionada
    rodadas_mapa += 1
    jogadores = criar_jogadores(4, mapa, spawn_fixo) #cria novos jogadores com as mesmas configurações para a nova rodada
    #spawn_fixo é mantido, então se estava no modo aleatório continua aleatório, e se estava no fixo continua fixo

def trocar_mapa(novo_indice):
    #troca o mapa e reseta tudo, incluindo o contador de rodadas
    global mapa, TAM_CELULA, jogadores, resultados_salvos, rodadas_mapa, indice_mapa, indice_rodada_selecionada
    indice_mapa = novo_indice
    resultados_salvos = False
    indice_rodada_selecionada = None # reseta a caixinha selecionada
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
                
            # verifica se clicou em alguma caixinha do histórico
            for rect, idx in botoes_historico:
                if rect.collidepoint(e.pos):
                    indice_rodada_selecionada = idx
                    break

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
        salvar_resultados(indice_mapa, jogadores, rodadas_mapa, spawn_fixo)
        resultados_salvos = True  #garante que só salva uma vez por partida

    pygame.time.delay(265) #265