from utils.file import create_instances

from gale_shapley import GaleShapley


def main():
    alunos, projetos = create_instances("../data/entradaProj2.26TAG.txt")

    gale_shapley = GaleShapley(alunos, projetos)

    print("----------- ALUNO PARA PROJETOS -----------")

    print(gale_shapley.aluno_para_projetos())

    pares_bloqueadores = gale_shapley.checa_estabilidade()
    print("Estavel? ", len(pares_bloqueadores) == 0)

    print("----------- PROJETO PARA ALUNOS -----------")

    print(gale_shapley.projeto_para_alunos())
    pares_bloqueadores = gale_shapley.checa_estabilidade()
    print("Estavel? ", len(pares_bloqueadores) == 0)


if __name__ == "__main__":
    main()
