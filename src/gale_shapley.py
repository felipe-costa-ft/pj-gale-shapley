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

        # Cada simulação começa sem as alocações da execução anterior.
        for aluno in self.alunos:
            aluno.projeto = None

        for projeto in self.projetos:
            projeto.alunos.clear()

        alunos_pendentes: list[Aluno] = self.alunos.copy()
        proxima_preferencia: dict[Aluno, int] = {a: 0 for a in self.alunos}

        while alunos_pendentes:
            aluno = alunos_pendentes.pop(0)

            while proxima_preferencia[aluno] < len(aluno.preferencias):
                projeto = aluno.preferencias[proxima_preferencia[aluno]]
                proxima_preferencia[aluno] += 1
                elegivel = aluno.projeto_elegivel(projeto)
                aluno_index = projeto.checa_preferencia_aluno(aluno)

                if elegivel and aluno_index is not None:

                    if aluno_index < len(projeto.alunos):
                        removido = projeto.alunos[aluno_index]
                        removido.projeto = None
                        alunos_pendentes.append(removido)

                    self.cria_relacao(aluno, aluno_index, projeto)
                    break

        return [
            (a.label, a.projeto.label) for a in self.alunos if a.projeto is not None
        ]

    def projeto_para_alunos(self) -> list[tuple[str, str]]:

        # Cada simulação começa sem as alocações da execução anterior.
        for aluno in self.alunos:
            aluno.projeto = None

        projetos_pendentes = self.projetos.copy()
        proximo_candidato: dict[Projeto, int] = {}

        for projeto in projetos_pendentes:
            projeto.alunos.clear()
            projeto.monta_candidatos(self.alunos)
            proximo_candidato[projeto] = 0

        while projetos_pendentes:
            projeto = projetos_pendentes.pop(0)

            while len(projeto.alunos) < projeto.vagas and proximo_candidato[
                projeto
            ] < len(projeto.candidatos):
                aluno = projeto.candidatos[proximo_candidato[projeto]]
                proximo_candidato[projeto] += 1

                if not aluno.checa_preferencia_projeto(projeto):
                    continue

                projeto_anterior = aluno.projeto
                if projeto_anterior is not None:
                    projeto_anterior.alunos.remove(aluno)

                    # A saída do aluno abre uma vaga para novas propostas.
                    if (
                        proximo_candidato[projeto_anterior]
                        < len(projeto_anterior.candidatos)
                        and projeto_anterior not in projetos_pendentes
                    ):
                        projetos_pendentes.append(projeto_anterior)

                self.cria_relacao(aluno, len(projeto.alunos), projeto)

        return [
            (a.label, a.projeto.label) for a in self.alunos if a.projeto is not None
        ]
