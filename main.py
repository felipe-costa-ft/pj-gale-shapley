from utils.file import create_instances

from gale_shapley import GaleShapley


def main():
    alunos, projetos = create_instances("./data/entradaProj2.26TAG.txt")

    gale_shapley = GaleShapley(alunos, projetos)

    print(gale_shapley.aluno_para_projetos())


if __name__ == "__main__":
    main()
