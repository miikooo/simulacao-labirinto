from sqlalchemy import Column, Integer, String, PickleType, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base

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
    rodada = Column(Integer, default=1)
    modo = Column(String, default="Fixo")
    start_l = Column(Integer) #linha onde o jogador nasceu
    start_c = Column(Integer) #coluna onde o jogador nasceu