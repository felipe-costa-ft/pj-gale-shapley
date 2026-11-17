from models.Aluno import Aluno
from models.Projeto import Projeto


def extract_lists(path: str) -> tuple[list[str], list[str]]:
    with open(path, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        linhas = [l.strip() for l in linhas if l.strip().startswith("(")]

        alunos = [l for l in linhas if l.startswith("(A")]
        projetos = [l for l in linhas if l.startswith("(P")]

    return alunos, projetos


def remove_parenthesis(text: str):
    return text.replace("(", "").replace(")", "")


def create_alunos(alunos: list[str], projetos_inst: list[Projeto]) -> list[Aluno]:

    alunos_instances: list[Aluno] = []

    projetos_by_label = {p.label: p for p in projetos_inst}

    for aluno in alunos:

        aluno = aluno.split(":")

        label = remove_parenthesis(aluno[0])

        aluno_attr = aluno[1].split(")")
        preferencias = remove_parenthesis(aluno_attr[0]).split(", ")
        preferencias = [
            projetos_by_label[p] for p in preferencias if p in projetos_by_label
        ]
        nota = int(remove_parenthesis(aluno_attr[1]))

        alunos_instances.append(Aluno(label, preferencias, nota))

    return alunos_instances


def create_projetos(projetos: list[str]) -> list[Projeto]:
    projetos_instances: list[Projeto] = []

    for projeto in projetos:

        projeto_attr = remove_parenthesis(projeto)
        projeto_attr = projeto_attr.split(", ")

        label = projeto_attr[0]
        vagas = int(projeto_attr[1])
        nota_min = int(projeto_attr[2])

        projetos_instances.append(Projeto(label, vagas, nota_min))

    return projetos_instances


def create_instances(path: str) -> tuple[list[Aluno], list[Projeto]]:

    alunos, projetos = extract_lists(path)

    projetos_instances = create_projetos(projetos)

    alunos_instances = create_alunos(alunos, projetos_instances)

    return alunos_instances, projetos_instances
