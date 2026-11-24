"""Índice de procura e classificações dos emparelhamentos."""

from html import escape

from models.Aluno import Aluno
from models.Projeto import Projeto


def tabela_final(alunos: list[Aluno]) -> list[dict]:
    linhas = []
    for aluno in alunos:
        projeto = aluno.projeto
        candidatos = [
            a for a in alunos
            if projeto is not None
            and projeto in a.preferencias and projeto.aluno_elegivel(a)
        ]
        linhas.append({
            "Aluno": aluno.label,
            "Projeto": projeto.label if projeto else None,
            "Nota": aluno.nota,
            "Escolha do aluno": aluno.preferencias.index(projeto) + 1 if projeto else None,
            # Empatados compartilham a posição: 1, 2, 2, 4 etc.
            "Posição no projeto": 1 + sum(a.nota > aluno.nota for a in candidatos) if projeto else None,
            "Candidatos elegíveis": len(candidatos) if projeto else None,
        })
    return linhas


def indices_preferencia(alunos: list[Aluno], projetos: list[Projeto]) -> list[dict]:
    linhas = []
    for projeto in projetos:
        interessados = [a for a in alunos if projeto in a.preferencias]
        escolhas = [a.preferencias.index(projeto) for a in interessados]
        linhas.append({
            "Projeto": projeto.label,
            "1ª escolha": escolhas.count(0),
            "2ª escolha": escolhas.count(1),
            "3ª escolha": escolhas.count(2),
            "Índice": sum(3 - escolha for escolha in escolhas),
            "Elegíveis": sum(projeto.aluno_elegivel(a) for a in interessados),
            "Vagas": projeto.vagas,
            "Ocupadas": len(projeto.alunos),
        })
    return linhas


def mostrar_tabela(linhas: list[dict]) -> None:
    """Exibe uma tabela estática na própria célula do notebook."""
    from IPython.display import HTML, display

    if not linhas:
        print("Tabela vazia.")
        return
    cabecalho = "".join(f"<th>{escape(c)}</th>" for c in linhas[0])
    corpo = "".join(
        "<tr>" + "".join(
            f"<td>{escape(str(v)) if v is not None else '—'}</td>"
            for v in linha.values()
        ) + "</tr>"
        for linha in linhas
    )
    display(HTML(f"<table><thead><tr>{cabecalho}</tr></thead><tbody>{corpo}</tbody></table>"))
