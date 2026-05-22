import random
from sqlalchemy import create_engine, Column, Integer, String, PickleType, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base() #base q o banco herda

#modelo de tabela 
class MapaModel(Base):
    __tablename__ = 'mapas'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    tipo = Column(String) #guarda o perfil: bifurcacao, livre ou misto
    grade = Column(PickleType) #matriz do labirinto, pickle serializa por transformar em bytes
    resultados = relationship("ResultadoModel", back_populates="mapa") #liga a tabela de resultados ao mapa

#tabela de resultados, guarda como cada jogador se saiu em cada mapa
class ResultadoModel(Base):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True)
    mapa_id = Column(Integer, ForeignKey('mapas.id')) #qual mapa foi jogado
    jogador_nome = Column(String)                     #tipo do jogador
    tempo = Column(Integer)                           #tempo final em minutos
    posicao = Column(Integer)                         #1º, 2º, 3º, 4º lugar
    mapa = relationship("MapaModel", back_populates="resultados") #volta para o mapa

engine = create_engine('sqlite:///labirintos.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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
    #2 Bifurcados, 2 Livres (Simples), 2 Mistos (Meio-termo)
    ordem_cenarios = [
        ("Mapa Bifurcado 1", "bifurcacao"),
        ("Mapa Bifurcado 2", "bifurcacao"),
        ("Mapa Livre ", "livre"),
        ("Mapa Livre", "livre"),
        ("Mapa Meio-Termo", "misto"),
        ("Mapa Meio-Termo", "misto")
    ]

    for nome, tipo in ordem_cenarios:
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

def salvar_resultados(indice_mapa, jogadores):
    session = Session()
    #busca ordenada por ID para manter a sincronia com a navegação
    todos_mapas: list[MapaModel] = session.query(MapaModel).order_by(MapaModel.id).all()
    mapa_db: MapaModel = todos_mapas[indice_mapa] # type: ignore 

    jogadores_ordenados = sorted(jogadores, key=lambda j: j.tempo) #ordena jogadores pelo tempo

    for posicao, jogador in enumerate(jogadores_ordenados, start=1):
        resultado = ResultadoModel(
            mapa_id=mapa_db.id,
            jogador_nome=jogador.nome,
            tempo=jogador.tempo,
            posicao=posicao
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
        return []

    mapa_db: MapaModel = todos_mapas[indice_mapa] # type: ignore 
    resultados = session.query(ResultadoModel).filter_by(mapa_id=mapa_db.id).order_by(ResultadoModel.posicao).all()

    dados = [{"nome": r.jogador_nome, "tempo": r.tempo, "posicao": r.posicao} for r in resultados]
    session.close()
    return dados

popular_banco_se_vazio()


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