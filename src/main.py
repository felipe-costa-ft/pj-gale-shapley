from pathlib import Path

from utils.parser import create_instances

from gale_shapley import GaleShapley


def main():
    entrada = Path(__file__).resolve().parent.parent / "data/entradaProj2.26TAG.txt"
    alunos, projetos = create_instances(str(entrada))

    gale_shapley = GaleShapley(alunos, projetos)

    for direcao in ("alunos", "projetos"):
        print(f"----------- PROPOSTAS DOS {direcao.upper()} -----------")
        historico = gale_shapley.executar_iteracoes(direcao)

        for rodada in historico:
            if rodada.numero == 0:
                print(f"Gale–Shapley inicial: {len(rodada.pares)} alocados.")
                print("Emparelhamento:", rodada.pares)
                continue
            print(
                f"Iteração {rodada.numero}: {len(rodada.pares)} alocados; "
                f"{rodada.tentativas} caminhos testados; "
                f"{rodada.rejeitados} rejeitados por instabilidade."
            )
            if rodada.caminho:
                print("Novos pares do caminho:", rodada.caminho)
            print("Emparelhamento:", rodada.pares)

        print("Estável?", not gale_shapley.checa_estabilidade())


if __name__ == "__main__":
    main()
