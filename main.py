from utils.file import create_instances

from gale_shapley import GaleShapley


def main():
    alunos, projetos = create_instances("./data/entradaProj2.26TAG.txt")

    gale_shapley = GaleShapley(alunos, projetos)

    print("Aluno para projetos: ", gale_shapley.aluno_para_projetos())

    print("Projeto para alunos: ", gale_shapley.projeto_para_alunos())


if __name__ == "__main__":
    main()
