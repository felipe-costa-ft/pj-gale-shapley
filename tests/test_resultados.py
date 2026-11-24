import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from models.Aluno import Aluno
from models.Projeto import Projeto
from resultados import indices_preferencia, tabela_final


class TestResultados(unittest.TestCase):
    def test_classificacao_com_empates_e_nao_alocados(self):
        p = Projeto("P1", 4, 3)
        alunos = [Aluno(f"A{i}", [p], n) for i, n in enumerate([5, 4, 4, 3], 1)]
        for a in alunos:
            a.projeto = p
        alunos.append(Aluno("A5", [p], 3))
        linhas = tabela_final(alunos)
        self.assertEqual([l["Posição no projeto"] for l in linhas], [1, 2, 2, 4, None])
        self.assertEqual(linhas[0]["Candidatos elegíveis"], 5)
        self.assertIsNone(linhas[-1]["Projeto"])

    def test_classificacao_exclui_inelegiveis(self):
        p1, p2 = Projeto("P1", 2, 4), Projeto("P2", 1, 3)
        a1 = Aluno("A1", [p2, p1], 4)
        a2 = Aluno("A2", [p1], 5)
        a3 = Aluno("A3", [p1], 3)
        a1.projeto = p1
        linha = tabela_final([a1, a2, a3])[0]
        self.assertEqual(linha["Escolha do aluno"], 2)
        self.assertEqual(linha["Posição no projeto"], 2)
        self.assertEqual(linha["Candidatos elegíveis"], 2)

    def test_indice_de_procura(self):
        p1, p2, p3, p4 = [Projeto(f"P{i}", 2, 4) for i in range(1, 5)]
        alunos = [Aluno("A1", [p1, p2, p3], 5), Aluno("A2", [p1], 3), Aluno("A3", [p3, p1], 4)]
        indices = indices_preferencia(alunos, [p1, p2, p3, p4])
        self.assertEqual([i["Índice"] for i in indices], [8, 2, 4, 0])
        self.assertEqual(indices[0]["Elegíveis"], 2)
        self.assertEqual(indices[0]["1ª escolha"], 2)


if __name__ == "__main__":
    unittest.main()
