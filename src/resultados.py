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


def mostrar_tabela(linhas: list[dict], titulo: str = "") -> None:
    """Exibe uma tabela estática na própria célula do notebook."""
    from IPython.display import HTML, display

    if not linhas:
        linhas = [{"Resultado": "Nenhum registro."}]
    colunas = list(linhas[0])
    cabecalho = "".join(
        '<th scope="col" style="padding:9px;text-align:left;'
        f'color:#172b3a!important;background:#e2eaf2!important">{escape(c)}</th>'
        for c in colunas
    )
    corpo = []
    for i, linha in enumerate(linhas):
        fundo = "#f4f7fa" if i % 2 else "#ffffff"
        celulas = []
        for coluna in colunas:
            valor = linha.get(coluna)
            if isinstance(valor, bool):
                valor = "Sim" if valor else "Não"
            texto = escape(str(valor)) if valor is not None else "—"
            alinhamento = "right" if isinstance(valor, (int, float)) else "left"
            celulas.append(
                f'<td style="padding:7px 9px;border-bottom:1px solid #dce3ea;'
                f'text-align:{alinhamento};color:#172b3a!important;'
                f'background:{fundo}!important">{texto}</td>'
            )
        corpo.append(f'<tr style="background:{fundo}">{"".join(celulas)}</tr>')
    legenda = (
        '<caption style="text-align:left;font-weight:600;padding:10px 9px;'
        'color:#172b3a!important;background:#e2eaf2!important">'
        f'{escape(titulo)}</caption>' if titulo else ""
    )
    display(HTML(
        '<table style="border-collapse:collapse;margin:12px 0;font-size:14px">'
        f'{legenda}<thead style="background:#e2eaf2"><tr>{cabecalho}</tr></thead>'
        f'<tbody>{"".join(corpo)}</tbody></table>'
    ))
