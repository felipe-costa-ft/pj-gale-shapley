from pathlib import Path

from gale_shapley import GaleShapley
from resultados import indices_preferencia, tabela_final
from utils.parser import create_instances


def main():
    entrada = Path(__file__).resolve().parent.parent / "data/entradaProj2.26TAG.txt"
    for direcao in ("alunos", "projetos"):
        alunos, projetos = create_instances(str(entrada))
        algoritmo = GaleShapley(alunos, projetos)
        historico = algoritmo.executar_iteracoes(direcao)
        print(f"\nPROPOSTAS DOS {direcao.upper()}")
        for rodada in historico:
            nome = "Gale–Shapley inicial" if rodada.numero == 0 else f"Iteração {rodada.numero}"
            print(f"{nome}: {len(rodada.pares)} alocados; {rodada.tentativas} caminhos; {rodada.rejeitados} rejeitados")
        print("Estável?", not algoritmo.checa_estabilidade())
        print("\nÍndices de preferência:")
        for linha in indices_preferencia(alunos, projetos):
            print(linha)
        print("\nTabela final:")
        for linha in tabela_final(alunos):
            print(linha)


if __name__ == "__main__":
    main()
