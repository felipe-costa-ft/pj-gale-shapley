from utils.file import create_instances

from gale_shapley import GaleShapley


def main():
    alunos, projetos = create_instances("./data/entradaProj2.26TAG.txt")

    print(alunos)

    print(projetos)

    gale_shapley = GaleShapley(alunos, projetos)


if __name__ == "__main__":
    main()
