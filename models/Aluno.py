from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Projeto import Projeto


class Aluno:

    def __init__(self, label: str, preferencias: list[Projeto], nota: int):
        self.label = label
        self.preferencias = preferencias
        self.nota = nota
        self.projeto: Projeto | None = None

    def __str__(self) -> str:
        return "{}: {}, ({})".format(self.label, self.preferencias, self.nota)

    def __repr__(self) -> str:
        return "{}: {}, ({})".format(self.label, self.preferencias, self.nota)

    # verifica se um projeto está na lista de preferências
    def projeto_elegivel(self, projeto: Projeto) -> bool:

        return projeto in self.preferencias

    # verifica se um projeto está nas preferências e se tem prioridade em relação ao atual
    def checa_preferencia_projeto(self, projeto: Projeto) -> bool:
        if projeto not in self.preferencias:
            return False

        if self.projeto is None:
            return True

        proj_atual_index = self.preferencias.index(self.projeto)
        proj_index = self.preferencias.index(projeto)

        return proj_index < proj_atual_index
