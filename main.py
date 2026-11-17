from utils.file import extract_lists, create_instances


def main():
    alunos, projetos = create_instances("./data/entradaProj2.26TAG.txt")

    print(alunos)

    print(projetos)


if __name__ == "__main__":
    main()
