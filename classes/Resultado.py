class Resultado:
    # !!!!! Adicionamos start_l e start_c no construtor
    def __init__(self, jogador_nome=None, tempo=None, posicao=None, start_l='?', start_c='?'):
        self.jogador_nome = jogador_nome
        self.tempo = tempo
        self.posicao = posicao
        self.start_l = start_l
        self.start_c = start_c

    def formatar_para_tela(self):
        # Exibe a posição no formato [L, C] no final da string
        return f"{self.posicao}º {self.jogador_nome}: {self.tempo} min [{self.start_l},{self.start_c}]"