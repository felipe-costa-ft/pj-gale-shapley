import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gale_shapley import GaleShapley
from models.Aluno import Aluno
from models.Projeto import Projeto


class TestEventos(unittest.TestCase):
    def test_proposta_antecede_alocacao_nas_duas_direcoes(self):
        p = Projeto("P1", 1, 3)
        a = Aluno("A1", [p], 5)
        g = GaleShapley([a], [p])
        for metodo in (g.aluno_para_projetos, g.projeto_para_alunos):
            metodo()
            self.assertEqual([e.tipo for e in g.eventos], ["proposta", "temporario"])
            self.assertEqual(g.eventos[0].adicionadas, [])
            self.assertEqual(g.eventos[1].adicionadas, [("A1", "P1")])

    def test_simulacao_instavel_e_restauracao_aparecem_nos_eventos(self):
        p1, p2 = Projeto("P1", 1, 3), Projeto("P2", 1, 3)
        a1, a2 = Aluno("A1", [p1, p2], 5), Aluno("A2", [p1], 4)
        g = GaleShapley([a1, a2], [p1, p2])
        g.aluno_para_projetos()
        g.eventos = []
        self.assertEqual(g.tenta_aumento(), ([], 1, 1))
        self.assertEqual([e.tipo for e in g.eventos], ["proposta", "temporario", "rejeicao"])
        self.assertIn(("A1", "P2"), g.eventos[1].adicionadas)
        self.assertIn(("A1", "P1"), g.eventos[2].adicionadas)
        self.assertIn(("A1", "P2"), g.eventos[2].removidas)
        self.assertIn("Pares bloqueadores", g.eventos[2].motivo)

    def test_rodada_sem_caminho_tambem_tem_evento_final(self):
        historico = GaleShapley([], []).executar_iteracoes()
        self.assertEqual(historico[0].eventos, [])
        for rodada in historico[1:]:
            self.assertEqual(len(rodada.eventos), 1)
            self.assertEqual(rodada.eventos[0].tipo, "fim")


if __name__ == "__main__":
    unittest.main()
