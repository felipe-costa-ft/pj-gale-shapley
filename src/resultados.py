"""Tabelas de resultados sem alterar as preferências ou as alocações."""

import csv
from dataclasses import asdict, dataclass, fields
from html import escape
from pathlib import Path

from models.Aluno import Aluno
from models.Projeto import Projeto


@dataclass
class LinhaEmparelhamento:
    aluno: str
    projeto: str | None
    nota: int
    escolha_do_aluno: int | None
    classificacao_no_projeto: int | None
    candidatos_elegiveis: int | None


@dataclass
class IndicePreferencia:
    projeto: str
    primeiras_escolhas: int
    segundas_escolhas: int
    terceiras_escolhas: int
    indice: int
    interessados: int
    candidatos_elegiveis: int
    vagas: int
    ocupadas: int


def tabela_final(alunos: list[Aluno]) -> list[LinhaEmparelhamento]:
    """Inclui não alocados; notas empatadas recebem posições 1, 2, 2, 4 etc."""
    linhas = []
    for aluno in alunos:
        projeto = aluno.projeto
        if projeto is None:
            linhas.append(LinhaEmparelhamento(aluno.label, None, aluno.nota, None, None, None))
            continue

        candidatos = [
            a for a in alunos
            if projeto in a.preferencias and projeto.aluno_elegivel(a)
        ]
        classificacao = 1 + sum(a.nota > aluno.nota for a in candidatos)
        linhas.append(
            LinhaEmparelhamento(
                aluno.label,
                projeto.label,
                aluno.nota,
                aluno.preferencias.index(projeto) + 1,
                classificacao,
                len(candidatos),
            )
        )
    return linhas


def indices_preferencia(
    alunos: list[Aluno], projetos: list[Projeto]
) -> list[IndicePreferencia]:
    """Mede procura: 3 pontos por 1ª escolha, 2 por 2ª e 1 por 3ª.

    Conta todos os interessados, inclusive os que não atingem a nota mínima.
    A quantidade de candidatos elegíveis é apresentada separadamente.
    """
    escolhas = {p: [0, 0, 0] for p in projetos}
    elegiveis = {p: 0 for p in projetos}
    for aluno in alunos:
        for posicao, projeto in enumerate(aluno.preferencias):
            escolhas[projeto][posicao] += 1
            if projeto.aluno_elegivel(aluno):
                elegiveis[projeto] += 1

    return [
        IndicePreferencia(
            p.label,
            *escolhas[p],
            sum(qtd * peso for qtd, peso in zip(escolhas[p], (3, 2, 1))),
            sum(escolhas[p]),
            elegiveis[p],
            p.vagas,
            len(p.alunos),
        )
        for p in projetos
    ]


def _tabela_html(linhas: list, classe: type) -> str:
    colunas = [campo.name for campo in fields(classe)]
    cabecalho = "".join(f"<th>{escape(c.replace('_', ' '))}</th>" for c in colunas)
    corpo = []
    for linha in linhas:
        valores = asdict(linha)
        celulas = "".join(
            f"<td>{escape(str(valores[c])) if valores[c] is not None else '—'}</td>"
            for c in colunas
        )
        corpo.append(f"<tr>{celulas}</tr>")
    return f"<table><thead><tr>{cabecalho}</tr></thead><tbody>{''.join(corpo)}</tbody></table>"


def salvar_resultados(
    alunos: list[Aluno], projetos: list[Projeto], direcao: str, pasta: Path
) -> Path:
    """Exporta uma fotografia do resultado antes de executar a outra direção."""
    if direcao not in ("alunos", "projetos"):
        raise ValueError("A direção deve ser 'alunos' ou 'projetos'.")
    pasta.mkdir(parents=True, exist_ok=True)
    tabela = tabela_final(alunos)
    indices = indices_preferencia(alunos, projetos)

    for nome, linhas, classe in (
        ("emparelhamentos", tabela, LinhaEmparelhamento),
        ("indices", indices, IndicePreferencia),
    ):
        with (pasta / f"{nome}_{direcao}.csv").open("w", encoding="utf-8-sig", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=[c.name for c in fields(classe)])
            escritor.writeheader()
            escritor.writerows(asdict(linha) for linha in linhas)

    proposta = " — Proposta final" if direcao == "projetos" else " — Comparação"
    alocados = sum(l.projeto is not None for l in tabela)
    pagina = f"""<!doctype html>
<html lang="pt-BR"><meta charset="utf-8">
<title>Resultados — propostas dos {direcao}</title>
<style>
body {{font: 16px system-ui; max-width: 1100px; margin: 32px auto; padding: 0 16px; color: #172b3a}}
table {{border-collapse: collapse; width: 100%; margin-bottom: 32px}}
th, td {{border: 1px solid #cbd5e1; padding: 8px; text-align: left}}
th {{background: #e6eef4}} tbody tr:nth-child(even) {{background: #f5f8fa}}
</style>
<h1>Propostas dos {direcao}{proposta}</h1>
<p><a href="visualizacao_{direcao}.html">Ver grafo e evolução das dez iterações</a></p>
<p>{alocados} alunos alocados; {len(alunos) - alocados} não alocados;
{sum(bool(p.alunos) for p in projetos)} projetos ocupados.</p>
<h2>Índice de preferência por projeto</h2>
<p>Índice de procura = 3 × primeiras escolhas + 2 × segundas escolhas + terceiras escolhas.
Inclui interessados abaixo da nota mínima; candidatos elegíveis aparecem em coluna própria.</p>
{_tabela_html(indices, IndicePreferencia)}
<h2>Matriz final dos emparelhamentos</h2>
<p>Escolhas contadas após descartar projetos inexistentes. A classificação no projeto
considera apenas candidatos elegíveis. Empatados por nota compartilham a posição
(por exemplo, 1, 2, 2, 4). Traços indicam ausência de alocação.</p>
{_tabela_html(tabela, LinhaEmparelhamento)}
</html>"""
    destino = pasta / f"resultados_{direcao}.html"
    destino.write_text(pagina, encoding="utf-8")
    return destino
