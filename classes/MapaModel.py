import random
from database.config import Session
from database.models_db import MapaModel

#!!!!! (erro de tippo)
class Mapa:
    def __init__(self, indice=None):
        session = Session()
        todos_mapas: list[MapaModel] = session.query(MapaModel).order_by(MapaModel.id).all()

        if indice is not None and 0 <= indice < len(todos_mapas):
            mapa_escolhido: MapaModel = todos_mapas[indice]  # type: ignore
        else:
            mapa_escolhido: MapaModel = random.choice(todos_mapas)  # type: ignore
            
        self.grade: list[list[int]] = mapa_escolhido.grade  # type: ignore
        self.nome: str = str(mapa_escolhido.nome)   # nome real do banco: "Mapa Bifurcado A", etc
        self.tipo: str = str(mapa_escolhido.tipo)   # tipo real do banco: "bifurcacao", "livre", "misto"
        self.linhas = len(self.grade)
        self.colunas = len(self.grade[0])
        session.close()

    def get(self, l, c):
        return self.grade[l][c]
 
    def posicao_valida(self, l, c):
        return 0 <= l < self.linhas and 0 <= c < self.colunas and self.grade[l][c] != 1
    
    def encontrar_inicio(self):
        return 1, 1  # ponto fixo onde esculpir() sempre começa

    def encontrar_chegada(self):
        for l in range(self.linhas):
            for c in range(self.colunas):
                if self.grade[l][c] == 4:
                    return l, c
        return 0, 0