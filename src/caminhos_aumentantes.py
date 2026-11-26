"""Experimento de aumento sem impor estabilidade à alocação."""

from gale_shapley import GaleShapley, IteracaoEmparelhamento


def executar_sem_estabilidade(
    algoritmo: GaleShapley, total_iteracoes: int = 10
) -> list[IteracaoEmparelhamento]:
    """Parte da alocação atual e aceita até um caminho aumentante por rodada."""
    if total_iteracoes < 1:
        raise ValueError("O número de iterações deve ser pelo menos 1.")

    historico = []
    for numero in range(total_iteracoes + 1):
        caminho = []
        if numero > 0:
            for aluno in algoritmo.alunos:
                if aluno.projeto is not None:
                    continue
                caminhos = algoritmo._caminhos_alternados(aluno, {aluno}, set())
                caminho = next(caminhos, [])
                if caminho:
                    break

            # Abre as vagas do caminho e depois cria as novas relações.
            for aluno, _ in caminho:
                if aluno.projeto is not None:
                    aluno.projeto.alunos.remove(aluno)
                    aluno.projeto = None
            for aluno, projeto in caminho:
                algoritmo.cria_relacao(aluno, len(projeto.alunos), projeto)

        pares = [
            (a.label, a.projeto.label)
            for a in algoritmo.alunos if a.projeto is not None
        ]
        historico.append(
            IteracaoEmparelhamento(
                numero=numero,
                pares=pares,
                caminho=[(a.label, p.label) for a, p in caminho],
                tentativas=int(bool(caminho)),
                # Apenas diagnóstico: os bloqueios não impedem o aumento.
                bloqueadores=algoritmo.checa_estabilidade(),
            )
        )

    return historico
