import random
import heapq
from collections import deque

class Jogador: 
    def __init__(self, nome, cor, start_l, start_c, dest_l, dest_c):
        self.nome = nome
        self.cor = cor
        self.l, self.c = start_l, start_c
        self.start_l, self.start_c = start_l, start_c
        self.dest_l, self.dest_c = dest_l, dest_c
        self.tempo = 0
        self.venceu = False
        self.caminho = [] 

#essa função é necessária para o JogadorCuidadoso
    def _reconstruir_caminho(self, visitados: dict[tuple, tuple | None], destino: tuple): #essa função é usada para reconstruir o caminho depois de encontrar o destino, usando o dicionário de visitados que guarda a relação filho-pai
        #reconstrói o caminho de trás pra frente usando o dicionário de visitados
        caminho = [] 
        atual: tuple | None = destino #aqui o tipo é tuple ou None, porque o início tem valor None no dicionário de visitados
        while atual is not None: #Enquanto não chegar no início (que tem valor None), vai adicionando o caminho
            caminho.append(atual)
            atual = visitados[atual]
        caminho.reverse()
        return caminho[1:]

    def _calcular_caminho(self, mapa):
        inicio = (self.l, self.c)
        destino = (self.dest_l, self.dest_c)

        fila = deque()
        fila.append(inicio)
        visitados: dict[tuple, tuple | None] = {inicio: None} #o inicio não tem pai

        while fila:
            atual = fila.popleft() #pega o próximo da fila para explorar

            #se chegar no destino, reconstrói o caminho usando o dicionário de visitados
            if atual == destino:
                return self._reconstruir_caminho(visitados, destino)

            l, c = atual #explora os vizinhos (cima, baixo, esquerda, direita) em ordem aleatória para evitar caminhos previsíveis
            
            direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)] #cima, baixo, esquerda, direita
            random.shuffle(direcoes) #embaralha

            #verifica os vizinhos e adiciona os válidos na fila
            for dl, dc in direcoes:
                vizinho = (l + dl, c + dc)
                if vizinho not in visitados and mapa.posicao_valida(*vizinho):
                    visitados[vizinho] = atual
                    fila.append(vizinho)

        return [] 

    def pensar_e_mover(self, mapa):
        if self.venceu: return 
        
        if not self.caminho:
            self.caminho = self._calcular_caminho(mapa) #se o caminho planejado está vazio, calcula um novo

        if self.caminho:
            nl, nc = self.caminho.pop(0) 
            self.l, self.c = nl, nc
            self._aplicar_custo(mapa.get(self.l, self.c)) #pega o próximo passo do caminho, move o jogador e aplica o custo do terreno

        if self.l == self.dest_l and self.c == self.dest_c:
            self.venceu = True

    def _aplicar_custo(self, tipo):
        if tipo == 0 or tipo == 4:
            self.tempo += 5
        elif tipo == 2:
            self.tempo += 20
        elif tipo == 3:
            self.tempo += 15

class JogadorEsquerda(Jogador):
    def _calcular_caminho(self, mapa):
        inicio = (self.l, self.c)
        destino = (self.dest_l, self.dest_c)

        fila = deque()
        #(linha, coluna, direcao_linha_anterior, direcao_coluna_anterior)
        #está parado
        fila.append((inicio[0], inicio[1], 0, 0)) 
        visitados: dict[tuple, tuple | None] = {inicio: None}

        while fila:
            l, c, dl_ant, dc_ant = fila.popleft()
            atual = (l, c)

            if atual == destino:
                return self._reconstruir_caminho(visitados, destino) #reutiliza o método da classe base

            #ordem de prioridade 1º esquerda, 2º frente, 3º direita, 4º trás
            if dl_ant == -1 and dc_ant == 0:   # Estava indo para CIMA
                direcoes = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            elif dl_ant == 1 and dc_ant == 0:  # Estava indo para BAIXO
                direcoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            elif dl_ant == 0 and dc_ant == -1: # Estava indo para ESQUERDA
                direcoes = [(1, 0), (0, -1), (-1, 0), (0, 1)]
            elif dl_ant == 0 and dc_ant == 1:  #ir pra direita
                direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            else:                              #parado
                direcoes = [(0, -1), (-1, 0), (1, 0), (0, 1)] 

            for dl, dc in direcoes:
                vizinho = (l + dl, c + dc)
                if vizinho not in visitados and mapa.posicao_valida(*vizinho):
                    visitados[vizinho] = atual
                    #passa o dl e dc atuais para o próximo passo saber de onde viemos
                    fila.append((vizinho[0], vizinho[1], dl, dc))

        return []

class JogadorRapido(Jogador):
    def _aplicar_custo(self, tipo):
        if tipo == 0 or tipo == 4:
            self.tempo += 2
        elif tipo == 2:
            self.tempo += 15
        elif tipo == 3:
            self.tempo += 10

class JogadorCuidadoso(Jogador):
    def _calcular_caminho(self, mapa):
        inicio = (self.l, self.c)
        destino = (self.dest_l, self.dest_c)

        #fila de prioridade
        # (custo_acumulado, (linha, coluna))
        fila = [(0, inicio)] 
        visitados: dict[tuple, tuple | None] = {inicio: None}
        custos = {inicio: 0} #guarda info do custo

        while fila:
            #pega o caminho mais barato
            custo_atual, atual = heapq.heappop(fila)

            if atual == destino:
                return self._reconstruir_caminho(visitados, destino) #reutiliza o método da classe base

            l, c = atual
            direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(direcoes)

            for dl, dc in direcoes:
                vizinho = (l + dl, c + dc)
                if mapa.posicao_valida(*vizinho):
                    tipo_terreno = mapa.get(vizinho[0], vizinho[1])
                    
                    #custo diferente por tipo de terreno
                    custo_movimento = 1 #caminho normal
                    if tipo_terreno == 2 or tipo_terreno == 3:
                        custo_movimento = 100 #ele sempre foge dos obstáculos
                        
                    novo_custo = custos[atual] + custo_movimento

                    #se achar o vizinho mais barato, atualiza
                    if vizinho not in custos or novo_custo < custos[vizinho]:
                        custos[vizinho] = novo_custo
                        visitados[vizinho] = atual
                        heapq.heappush(fila, (novo_custo, vizinho))

        return []