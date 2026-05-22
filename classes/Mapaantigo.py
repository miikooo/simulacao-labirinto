import random

class Mapa:
    def __init__(self):
        opcoes = [
            [
                [1, 1, 1, 1, 4, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 1, 2, 1, 1, 1, 2, 1, 0, 0],
                [0, 1, 2, 1, 0, 1, 2, 1, 0, 0],
                [0, 0, 3, 0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1],
                [0, 0, 0, 0, 1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                [0, 1, 1, 0, 1, 0, 1, 0, 2, 1, 2, 0, 1, 0, 1, 0, 1, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 1, 0, 2, 1, 2, 0, 1, 0, 0, 0, 0, 1, 0, 0],
                [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0],
                [0, 0, 0, 1, 3, 3, 3, 0, 1, 1, 1, 0, 3, 3, 3, 1, 0, 0, 0, 0],
                [1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1],
                [0, 0, 0, 2, 2, 2, 1, 0, 1, 0, 1, 0, 1, 2, 2, 2, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 1, 2, 1, 1, 1, 0, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]#persistencia, analise de como se saem em cada mapa 
            ]
        ]

        self.grade = random.choice(opcoes) 
        self.linhas = len(self.grade)
        self.colunas = len(self.grade[0])
 
    def get(self, l, c):
        return self.grade[l][c]
 
    def posicao_valida(self, l, c):
        return 0 <= l < self.linhas and 0 <= c < self.colunas and self.grade[l][c] != 1
    
    def encontrar_chegada(self):
        for l in range(self.linhas):
             for c in range(self.colunas):
                   if self.grade[l][c] == 4:
                    return l, c
        return 0, 0