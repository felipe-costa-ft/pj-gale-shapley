"""Visualização dos eventos reais e dos estados finais de cada rodada."""

import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_pdf import PdfPages

from gale_shapley import IteracaoEmparelhamento
from models.Aluno import Aluno
from models.Projeto import Projeto


def cria_grafo(alunos: list[Aluno], projetos: list[Projeto]) -> nx.Graph:
    grafo = nx.Graph()
    grafo.add_nodes_from((a.label, {"bipartite": 0, "nota": a.nota}) for a in alunos)
    grafo.add_nodes_from((p.label, {"bipartite": 1, "vagas": p.vagas}) for p in projetos)
    grafo.add_edges_from(
        (a.label, p.label)
        for a in alunos for p in a.preferencias if p.aluno_elegivel(a)
    )
    return grafo


def _posicoes(alunos: list[Aluno], projetos: list[Projeto]) -> dict:
    pos = {}
    for grupo, x in ((alunos, 0), (projetos, 1)):
        for i, vertice in enumerate(grupo):
            pos[vertice.label] = (x, 1 - (i + 0.5) / max(len(grupo), 1))
    return pos


def salvar_visualizacao(
    alunos: list[Aluno], projetos: list[Projeto],
    historico: list[IteracaoEmparelhamento], direcao: str, pasta: Path,
) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    grafo = cria_grafo(alunos, projetos)
    pos = _posicoes(alunos, projetos)
    dados = {
        "direcao": direcao,
        "alunos": [{"id": a.label, "nota": a.nota} for a in alunos],
        "projetos": [{"id": p.label, "vagas": p.vagas} for p in projetos],
        "arestas": list(grafo.edges),
        "historico": [asdict(rodada) for rodada in historico],
    }
    # Impede que um identificador da entrada encerre a tag script do documento.
    serializado = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    modelo = Path(__file__).with_name("templates") / "visualizacao.html"
    pagina = modelo.read_text(encoding="utf-8").replace("__DADOS__", serializado)
    destino = pasta / f"visualizacao_{direcao}.html"
    destino.write_text(pagina, encoding="utf-8")

    # PDF com todos os estados estáveis; PNG final para notebook e relatório.
    with PdfPages(pasta / f"rodadas_{direcao}.pdf") as pdf:
        for rodada in historico:
            fig, ax = plt.subplots(figsize=(10, 18))
            nx.draw_networkx_edges(grafo, pos, ax=ax, edge_color="#cbd5e1", width=0.4, alpha=0.3)
            nx.draw_networkx_edges(grafo, pos, ax=ax, edgelist=rodada.pares, edge_color="#16834b", width=1.2)
            nx.draw_networkx_nodes(grafo, pos, ax=ax, nodelist=[a.label for a in alunos], node_color="#2563eb", node_size=8)
            nx.draw_networkx_nodes(grafo, pos, ax=ax, nodelist=[p.label for p in projetos], node_color="#e09316", node_size=20, node_shape="s")
            ocupacao = Counter(p for _, p in rodada.pares)
            for a in alunos:
                x, y = pos[a.label]
                ax.text(x - 0.02, y, a.label, ha="right", va="center", fontsize=5)
            for p in projetos:
                x, y = pos[p.label]
                ax.text(x + 0.02, y, f"{p.label} ({ocupacao[p.label]}/{p.vagas})", va="center", fontsize=7)
            titulo = "Gale–Shapley inicial" if rodada.numero == 0 else f"Iteração {rodada.numero}"
            ax.set_title(f"Propostas dos {direcao} — {titulo}\n{len(rodada.pares)} alunos alocados", pad=20)
            ax.set_xlim(-0.15, 1.25)
            ax.set_ylim(-0.02, 1.02)
            ax.axis("off")
            fig.text(0.5, 0.025, "Verde: emparelhamento ao fim da rodada • Cinza: relações elegíveis\nPropostas, simulações e rejeições: consulte a visualização HTML.", ha="center", fontsize=9)
            pdf.savefig(fig, bbox_inches="tight")
            if rodada is historico[-1]:
                fig.savefig(pasta / f"grafo_final_{direcao}.png", dpi=160, bbox_inches="tight")
            plt.close(fig)
    return destino
