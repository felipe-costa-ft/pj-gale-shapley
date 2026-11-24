"""Gráficos de Matplotlib para exibir diretamente no notebook."""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx

from gale_shapley import TentativaEmparelhamento
from models.Aluno import Aluno
from models.Projeto import Projeto


def desenhar_grafo(
    ax, alunos: list[Aluno], projetos: list[Projeto], pares: list[tuple[str, str]],
    titulo: str, propostas=(), rejeicoes=(), foco=None,
) -> None:
    grafo = nx.Graph()
    grafo.add_nodes_from(a.label for a in alunos)
    grafo.add_nodes_from(p.label for p in projetos)
    grafo.add_edges_from(
        (a.label, p.label) for a in alunos for p in a.preferencias
        if p.aluno_elegivel(a)
    )
    if foco is not None:
        grafo = grafo.subgraph(foco)
    esquerda = [a.label for a in alunos if a.label in grafo]
    if grafo:
        pos = nx.bipartite_layout(grafo, esquerda)
        nx.draw_networkx_edges(grafo, pos, ax=ax, edge_color="#cbd5e1", alpha=0.3, width=0.5)
        for arestas, cor, estilo in (
            (pares, "#16834b", "solid"),
            (propostas, "#2563eb", "solid"),
            (rejeicoes, "#dc2626", "dashed"),
        ):
            visiveis = [(a, p) for a, p in arestas if a in grafo and p in grafo]
            nx.draw_networkx_edges(grafo, pos, ax=ax, edgelist=visiveis, edge_color=cor, width=1.5, style=estilo)
        cores = ["#526b83" if n in esquerda else "#e0a23b" for n in grafo]
        nx.draw_networkx_nodes(grafo, pos, ax=ax, node_size=60 if foco else 12, node_color=cores)
        # No grafo completo, os IDs dos alunos ficam na tabela para evitar sobreposição.
        rotulos = {n: n for n in grafo if foco is not None or n not in esquerda}
        nx.draw_networkx_labels(grafo, pos, ax=ax, labels=rotulos, font_size=9 if foco else 6)
        ax.margins(0.15)
    ax.set_title(titulo)
    ax.axis("off")


def desenhar_tentativa(
    alunos: list[Aluno], projetos: list[Projeto], tentativa: TentativaEmparelhamento
):
    """Mostra um recorte do caminho: proposta, simulação e decisão real."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    foco = {v for par in tentativa.propostas for v in par}
    rejeitada = bool(tentativa.bloqueadores)
    desenhar_grafo(axes[0], alunos, projetos, tentativa.antes,
                  "1. Proposta ativa", propostas=tentativa.propostas, foco=foco)
    desenhar_grafo(axes[1], alunos, projetos, tentativa.temporarios,
                  "2. Emparelhamento temporário", foco=foco)
    desenhar_grafo(
        axes[2], alunos, projetos,
        tentativa.antes if rejeitada else tentativa.temporarios,
        "3. Rejeição e restauração" if rejeitada else "3. Aumento estável aceito",
        rejeicoes=tentativa.propostas if rejeitada else (), foco=foco,
    )
    fig.legend(handles=[
        Line2D([], [], color="#2563eb", label="Proposta ativa"),
        Line2D([], [], color="#16834b", label="Emparelhamento temporário / aceito"),
        Line2D([], [], color="#dc2626", linestyle="--", label="Rejeição"),
    ], loc="lower center", ncol=3)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return fig
