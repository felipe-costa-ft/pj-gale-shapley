from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Aluno import Aluno
    from models.Projeto import Projeto


@dataclass
class IteracaoEmparelhamento:
    numero: int
    pares: list[tuple[str, str]]
    caminho: list[tuple[str, str]]
    tentativas: int = 0
    rejeitados: int = 0


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

    def checa_estabilidade(self) -> list[tuple[str, str]]:

        pares_bloqueadores: list[tuple[str, str]] = []

        for aluno in self.alunos:

            for projeto in aluno.preferencias:

                # Se chegou aqui, os itens proximas iterações são piores
                if projeto == aluno.projeto:
                    break

                projeto_prefere = projeto.checa_preferencia_aluno(aluno) is not None

                if projeto_prefere:

                    pares_bloqueadores.append((aluno.label, projeto.label))

        return pares_bloqueadores

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

            while (
                projeto.tem_vaga()
                and proximo_candidato[projeto] < len(projeto.candidatos)
            ):
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

    def _caminhos_alternados(
        self,
        aluno: Aluno,
        alunos_visitados: set[Aluno],
        projetos_visitados: set[Projeto],
    ) -> Iterator[list[tuple[Aluno, Projeto]]]:
        """Gera caminhos simples, sem alterar as alocações durante a busca."""
        for projeto in aluno.preferencias:
            if projeto in projetos_visitados or not projeto.aluno_elegivel(aluno):
                continue

            if projeto.tem_vaga():
                yield [(aluno, projeto)]
                continue

            # Explora qualquer substituição; a estabilidade é validada ao final.
            for removido in projeto.alunos:
                if removido in alunos_visitados:
                    continue

                for restante in self._caminhos_alternados(
                    removido,
                    alunos_visitados | {removido},
                    projetos_visitados | {projeto},
                ):
                    yield [(aluno, projeto)] + restante

    def _tenta_caminho(self, caminho: list[tuple[Aluno, Projeto]]) -> bool:
        """Aplica o caminho provisoriamente e restaura tudo se houver bloqueios."""
        alocacoes = {a: a.projeto for a in self.alunos}
        aceitos = {p: p.alunos.copy() for p in self.projetos}
        manter = False

        try:
            # Primeiro abre as vagas, depois cria os novos pares.
            for aluno, _ in caminho:
                if aluno.projeto is not None:
                    aluno.projeto.alunos.remove(aluno)
                    aluno.projeto = None

            for aluno, projeto in caminho:
                self.cria_relacao(aluno, len(projeto.alunos), projeto)

            manter = not self.checa_estabilidade()
            return manter
        finally:
            if not manter:
                for aluno, projeto in alocacoes.items():
                    aluno.projeto = projeto
                for projeto, alunos in aceitos.items():
                    projeto.alunos[:] = alunos

    def tenta_aumento(self) -> tuple[list[tuple[str, str]], int, int]:
        """Aceita o primeiro aumento estável, em ordem determinística.

        Retorna o caminho aceito, a quantidade de tentativas e as rejeições.
        A ausência de aumento não comprova que o emparelhamento seja máximo.
        """
        if self.checa_estabilidade():
            raise ValueError("A busca deve começar em um emparelhamento estável.")

        tentativas = 0
        rejeitados = 0
        for aluno in self.alunos:
            if aluno.projeto is not None:
                continue

            for caminho in self._caminhos_alternados(aluno, {aluno}, set()):
                tentativas += 1
                if self._tenta_caminho(caminho):
                    return (
                        [(a.label, p.label) for a, p in caminho],
                        tentativas,
                        rejeitados,
                    )
                rejeitados += 1

        return [], tentativas, rejeitados

    def executar_iteracoes(
        self, direcao: str = "projetos", total_iteracoes: int = 10
    ) -> list[IteracaoEmparelhamento]:
        """Registra o estado inicial (0) e as rodadas de melhoria (1 a N)."""
        if total_iteracoes < 1:
            raise ValueError("O número de iterações deve ser pelo menos 1.")
        if direcao == "alunos":
            pares = self.aluno_para_projetos()
        elif direcao == "projetos":
            pares = self.projeto_para_alunos()
        else:
            raise ValueError("A direção deve ser 'alunos' ou 'projetos'.")

        historico = [IteracaoEmparelhamento(0, pares, [])]
        for numero in range(1, total_iteracoes + 1):
            caminho, tentativas, rejeitados = self.tenta_aumento()
            pares = [
                (a.label, a.projeto.label)
                for a in self.alunos
                if a.projeto is not None
            ]
            historico.append(
                IteracaoEmparelhamento(
                    numero, pares, caminho, tentativas, rejeitados
                )
            )

        return historico
