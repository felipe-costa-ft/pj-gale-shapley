from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Aluno import Aluno


class Projeto:

    def __init__(self, label: str, vagas: int, nota_min: int):

        self.label = label
        self.vagas = vagas
        self.nota_min = nota_min
        self.alunos: list[Aluno] = []

    def __str__(self) -> str:
        return "{}: {}, {}".format(self.label, self.vagas, self.nota_min)

    def __repr__(self) -> str:
        return "{}: {}, {}".format(self.label, self.vagas, self.nota_min)

    def aluno_elegivel(self, aluno: Aluno) -> bool:
        return aluno.nota >= self.nota_min

    def checa_preferencia_aluno(self, aluno: Aluno) -> int | None:
        if not self.alunos:
            return None

        pior = 0

        for index, aluno_atual in enumerate(self.alunos):
            if aluno_atual.nota < self.alunos[pior].nota:
                pior = index

        # Notas iguais mantém o atual
        if aluno.nota > self.alunos[pior].nota:
            return pior

        return None
