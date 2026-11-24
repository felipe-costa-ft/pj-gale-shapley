import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from models.Aluno import Aluno
from models.Projeto import Projeto
from resultados import indices_preferencia, salvar_resultados, tabela_final


class TestResultados(unittest.TestCase):
    def test_classificacao_preserva_empates_e_inclui_nao_alocados(self):
        p = Projeto("P1", 4, 3)
        alunos = [Aluno(f"A{i}", [p], n) for i, n in enumerate([5, 4, 4, 3], 1)]
        for a in alunos:
            a.projeto = p
        p.alunos = alunos.copy()
        alunos.append(Aluno("A5", [p], 3))
        linhas = tabela_final(alunos)
        self.assertEqual([l.classificacao_no_projeto for l in linhas], [1, 2, 2, 4, None])
        self.assertEqual(linhas[0].candidatos_elegiveis, 5)
        self.assertIsNone(linhas[-1].projeto)
        self.assertIsNone(linhas[-1].escolha_do_aluno)

    def test_classificacao_exclui_inelegiveis(self):
        p1, p2 = Projeto("P1", 2, 4), Projeto("P2", 1, 3)
        a1 = Aluno("A1", [p2, p1], 4)
        a2 = Aluno("A2", [p1], 5)
        a3 = Aluno("A3", [p1], 3)
        a1.projeto = p1
        linha = tabela_final([a1, a2, a3])[0]
        self.assertEqual(linha.escolha_do_aluno, 2)
        self.assertEqual(linha.classificacao_no_projeto, 2)
        self.assertEqual(linha.candidatos_elegiveis, 2)

    def test_indice_conta_interesse_mesmo_sem_nota_minima(self):
        p1, p2, p3, p4 = [Projeto(f"P{i}", 2, 4) for i in range(1, 5)]
        alunos = [
            Aluno("A1", [p1, p2, p3], 5),
            Aluno("A2", [p1], 3),
            Aluno("A3", [p3, p1], 4),
        ]
        indices = indices_preferencia(alunos, [p1, p2, p3, p4])
        self.assertEqual([i.indice for i in indices], [8, 2, 4, 0])
        self.assertEqual(indices[0].interessados, 3)
        self.assertEqual(indices[0].candidatos_elegiveis, 2)
        self.assertEqual(indices[0].primeiras_escolhas, 2)

    def test_exporta_as_duas_direcoes_sem_perder_o_primeiro_resultado(self):
        p = Projeto("P1", 1, 3)
        a = Aluno("A1", [p], 5)
        a.projeto = p
        p.alunos.append(a)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            destino = salvar_resultados([a], [p], "alunos", pasta)
            anterior = destino.read_text(encoding="utf-8")
            a.projeto = None
            p.alunos.clear()
            salvar_resultados([a], [p], "projetos", pasta)
            self.assertEqual(destino.read_text(encoding="utf-8"), anterior)
            self.assertIn("Proposta final", (pasta / "resultados_projetos.html").read_text())
            with (pasta / "emparelhamentos_alunos.csv").open(encoding="utf-8-sig") as f:
                linhas = list(csv.DictReader(f))
            self.assertEqual(linhas[0]["projeto"], "P1")
            self.assertEqual(linhas[0]["escolha_do_aluno"], "1")

    def test_entrada_vazia(self):
        self.assertEqual(tabela_final([]), [])
        self.assertEqual(indices_preferencia([], []), [])
        with tempfile.TemporaryDirectory() as pasta:
            self.assertTrue(salvar_resultados([], [], "alunos", Path(pasta)).exists())


if __name__ == "__main__":
    unittest.main()
