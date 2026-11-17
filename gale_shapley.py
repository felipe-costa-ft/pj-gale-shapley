from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Aluno import Aluno
    from models.Projeto import Projeto


class GaleShapley:

    def __init__(self, alunos: list[Aluno], projetos: list[Projeto]):
        self.alunos = alunos
        self.projetos = projetos

    def cria_relacao(self, aluno: Aluno, aluno_index: int, projeto: Projeto):
        aluno.projeto = projeto

        if aluno_index < len(projeto.alunos):
            projeto.alunos[aluno_index] = aluno
        else:
            projeto.alunos.append(aluno)

    def aluno_para_projetos(self) -> list[tuple[str, str]]:

        alunos_pendentes: list[Aluno] = self.alunos.copy()

        aluno = alunos_pendentes[0]
        while len(alunos_pendentes):

            for projeto in aluno.preferencias:
                elegivel = aluno.projeto_elegivel(projeto)
                aluno_index = projeto.checa_preferencia_aluno(aluno)

                if elegivel and aluno_index is not None:
                    self.cria_relacao(aluno, aluno_index, projeto)
                    alunos_pendentes.remove(aluno)
                    break

        return []

    def projeto_para_alunos(self) -> list[tuple[str, str]]:
        return []
