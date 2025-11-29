from enum import Enum


class Estado(Enum):
    # TODO: Adicionar aguardando programação se nescessário
    AGUARDANDO = "Aguardando serviço"
    OFICINA = "Oficina"  # TODO: expandir maq. de estado para oficina
    AGUARDANDO_TESTE = "Aguardando teste"
    TESTE = "Testagem"
    AGUARDANDO_LAVAGEM = "Aguardando lavagem"
    LAVAGEM = "Lavagem"
    COMPLETO = "Completo"
    RETIRADO = "Retirado"

    def get_msg(self):
        if self == self.AGUARDANDO:
            return "Aguardando serviço."
        if self == self.OFICINA:
            return "Na oficina."
        if self == self.AGUARDANDO_TESTE:
            return "Aguardando testagem."
        if self == self.TESTE:
            return "Em teste."
        if self == self.AGUARDANDO_LAVAGEM:
            return "Aguardando lavagem."
        if self == self.LAVAGEM:
            return "Em lavagem."
        if self == self.COMPLETO:
            return "Aguardando retirada."
        if self == self.RETIRADO:
            return "Marcado como retirado pelo cliente."
        return "Desconhecido."

    def __gt__(self, outro):
        ordem = [
            Estado.AGUARDANDO,
            Estado.OFICINA,
            Estado.AGUARDANDO_TESTE,
            Estado.TESTE,
            Estado.AGUARDANDO_LAVAGEM,
            Estado.LAVAGEM,
            Estado.COMPLETO,
            Estado.RETIRADO,
        ]
        return ordem.index(self) > ordem.index(outro)


class Veiculo:
    def __init__(self, placa, status, id, retirado_em=None):
        self.placa = placa
        self.status = status
        self.id = id
        self.retirado_em = retirado_em

    def get_class_for_status(self):
        match self.status:
            case Estado.AGUARDANDO.value:
                return "status-aguardando"
            case Estado.OFICINA.value:
                return "status-servico"
            case Estado.TESTE.value:
                return "status-teste"
            case Estado.LAVAGEM.value:
                return "status-lavagem"
            case Estado.COMPLETO.value:
                return "status-pronto"
            case _:
                return "status-chegada"
