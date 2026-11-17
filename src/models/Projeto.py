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
        self.candidatos: list[Aluno] = []

    def __str__(self) -> str:
        return "{}: Vagas({}), Nota Mínima({})".format(
            self.label, self.vagas, self.nota_min
        )

    def __repr__(self) -> str:
        return "{}: Vagas({}), Nota Mínima({})".format(
            self.label, self.vagas, self.nota_min
        )

    def tem_vaga(self) -> bool:
        return len(self.alunos) < self.vagas

    def monta_candidatos(self, alunos: list[Aluno]) -> None:

        candidatos: list[Aluno] = []
        for aluno in alunos:
            if self in aluno.preferencias and aluno.nota >= self.nota_min:
                candidatos.append(aluno)

        candidatos.sort(key=lambda aluno: aluno.nota, reverse=True)

        self.candidatos = candidatos

    def aluno_elegivel(self, aluno: Aluno) -> bool:
        return aluno.nota >= self.nota_min

    def checa_preferencia_aluno(self, aluno: Aluno) -> int | None:

        if aluno.nota < self.nota_min:
            return None

        if self.tem_vaga():
            return len(self.alunos)

        pior = 0

        for index, aluno_atual in enumerate(self.alunos):
            if aluno_atual.nota < self.alunos[pior].nota:
                pior = index

        # Notas iguais mantém o atual
        if aluno.nota > self.alunos[pior].nota:
            return pior

        return None
