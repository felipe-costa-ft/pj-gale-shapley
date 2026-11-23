import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from gale_shapley import GaleShapley
from models.Aluno import Aluno
from models.Projeto import Projeto
from utils.parser import create_instances


class TestCaminhosAlternados(unittest.TestCase):
    def verifica_solucao(self, g, pares):
        """Verificação independente, incluindo cada fotografia do histórico."""
        alunos = {a.label: a for a in g.alunos}
        projetos = {p.label: p for p in g.projetos}
        alocacoes = dict(pares)
        self.assertEqual(len(alocacoes), len(pares))
        aceitos = {p.label: [] for p in g.projetos}
        for a_label, p_label in pares:
            a, p = alunos[a_label], projetos[p_label]
            self.assertIn(p, a.preferencias)
            self.assertGreaterEqual(a.nota, p.nota_min)
            aceitos[p_label].append(a)
        for p in g.projetos:
            self.assertLessEqual(len(aceitos[p.label]), p.vagas)
        for a in g.alunos:
            for p in a.preferencias:
                if p.label == alocacoes.get(a.label):
                    break
                if a.nota < p.nota_min:
                    continue
                bloqueia = len(aceitos[p.label]) < p.vagas or any(
                    a.nota > outro.nota for outro in aceitos[p.label]
                )
                self.assertFalse(bloqueia, (a.label, p.label))

    def test_aumento_por_empate_em_dez_rodadas(self):
        p1, p2 = Projeto("P1", 1, 3), Projeto("P2", 1, 3)
        a1 = Aluno("A1", [p1, p2], 5)
        a2 = Aluno("A2", [p1], 5)
        g = GaleShapley([a1, a2], [p1, p2])
        historico = g.executar_iteracoes("alunos")
        self.assertEqual(len(historico), 10)
        self.assertEqual([len(r.pares) for r in historico], [1] + [2] * 9)
        self.assertEqual(historico[0].pares, [("A1", "P1")])
        self.assertEqual(historico[1].caminho, [("A2", "P1"), ("A1", "P2")])
        self.assertIs(a1.projeto, p2)
        self.assertIs(a2.projeto, p1)
        for rodada in historico:
            self.verifica_solucao(g, rodada.pares)

    def instancia_com_caminho_instavel(self, alternativa=False):
        p1 = Projeto("P1", 1, 3)
        p2 = Projeto("P2", 1, 3)
        p3 = Projeto("P3", 1, 3)
        a1 = Aluno("A1", [p1, p3, p2], 5)
        a2 = Aluno("A2", [p1], 5)
        a3 = Aluno("A3", [p3], 3)
        alunos, projetos = [a1, a2, a3], [p1, p2, p3]
        if alternativa:
            p4, p5 = Projeto("P4", 1, 3), Projeto("P5", 1, 3)
            a4 = Aluno("A4", [p4, p5], 5)
            a2.preferencias.append(p4)
            alunos.append(a4)
            projetos.extend([p4, p5])
            a4.projeto = p4
            p4.alunos.append(a4)
        a1.projeto = p1
        p1.alunos.append(a1)
        a3.projeto = p3
        p3.alunos.append(a3)
        return GaleShapley(alunos, projetos)

    def test_rejeita_caminho_e_restaura_estado(self):
        g = self.instancia_com_caminho_instavel()
        self.assertEqual(g.checa_estabilidade(), [])
        anteriores = {a: a.projeto for a in g.alunos}
        listas = {p: p.alunos for p in g.projetos}
        conteudos = {p: p.alunos.copy() for p in g.projetos}
        # A1 iria para P2, mas passaria a bloquear com P3 (ocupado por nota 3).
        self.assertEqual(g.tenta_aumento(), ([], 1, 1))
        for a, p in anteriores.items():
            self.assertIs(a.projeto, p)
        for p in g.projetos:
            self.assertIs(p.alunos, listas[p])
            self.assertEqual(p.alunos, conteudos[p])

    def test_tenta_outro_caminho_apos_rejeicao(self):
        g = self.instancia_com_caminho_instavel(alternativa=True)
        caminho, tentativas, rejeitados = g.tenta_aumento()
        self.assertEqual(caminho, [("A2", "P4"), ("A4", "P5")])
        self.assertEqual((tentativas, rejeitados), (2, 1))
        pares = [(a.label, a.projeto.label) for a in g.alunos if a.projeto]
        self.verifica_solucao(g, pares)

    def test_sem_empate_testa_e_rejeita_por_instabilidade(self):
        p1, p2 = Projeto("P1", 1, 3), Projeto("P2", 1, 3)
        a1, a2 = Aluno("A1", [p1, p2], 5), Aluno("A2", [p1], 4)
        g = GaleShapley([a1, a2], [p1, p2])
        g.aluno_para_projetos()
        self.assertEqual(g.tenta_aumento(), ([], 1, 1))
        self.assertIs(a1.projeto, p1)
        self.assertIsNone(a2.projeto)

    def test_aceita_caminho_com_notas_diferentes(self):
        p1, p2, p3 = (Projeto(f"P{i}", 1, 3) for i in range(1, 4))
        livre = Aluno("A1", [p1], 4)
        a2 = Aluno("A2", [p2, p1], 5)
        a3 = Aluno("A3", [p2, p3], 5)
        g = GaleShapley([livre, a2, a3], [p1, p2, p3])
        g.cria_relacao(a2, 0, p1)
        g.cria_relacao(a3, 0, p2)
        self.assertEqual(g.checa_estabilidade(), [])
        caminho, tentativas, rejeitados = g.tenta_aumento()
        self.assertEqual(caminho, [("A1", "P1"), ("A2", "P2"), ("A3", "P3")])
        self.assertEqual((tentativas, rejeitados), (1, 0))
        self.verifica_solucao(
            g, [(a.label, a.projeto.label) for a in g.alunos if a.projeto]
        )

    def test_projeto_com_multiplas_vagas(self):
        p1, p2 = Projeto("P1", 2, 3), Projeto("P2", 1, 3)
        a1 = Aluno("A1", [p1], 5)
        a2 = Aluno("A2", [p1, p2], 4)
        a3 = Aluno("A3", [p1], 4)
        g = GaleShapley([a1, a2, a3], [p1, p2])
        historico = g.executar_iteracoes("alunos")
        self.assertEqual(len(historico[-1].pares), 3)
        self.assertEqual(historico[1].caminho, [("A3", "P1"), ("A2", "P2")])
        self.verifica_solucao(g, historico[-1].pares)

    def test_ciclo_sem_vaga_e_aluno_inelegivel(self):
        p1, p2, p3 = (Projeto(f"P{i}", 1, 4) for i in range(1, 4))
        a1 = Aluno("A1", [p1, p2], 5)
        a2 = Aluno("A2", [p2, p1], 5)
        a3 = Aluno("A3", [p1, p3], 3)
        a4 = Aluno("A4", [p1], 5)
        g = GaleShapley([a1, a2, a3, a4], [p1, p2, p3])
        historico = g.executar_iteracoes("alunos")
        self.assertTrue(all(len(r.pares) == 2 for r in historico))
        self.assertIsNone(a3.projeto)

    def test_entrada_vazia_e_argumentos_invalidos(self):
        g = GaleShapley([], [])
        self.assertEqual(len(g.executar_iteracoes()), 10)
        with self.assertRaises(ValueError):
            g.executar_iteracoes(total_iteracoes=0)
        with self.assertRaises(ValueError):
            g.executar_iteracoes("inexistente")

    def test_rejeita_inicio_instavel(self):
        p = Projeto("P", 1, 3)
        a = Aluno("A", [p], 5)
        with self.assertRaises(ValueError):
            GaleShapley([a], [p]).tenta_aumento()

    def test_dados_fornecidos_nas_duas_direcoes(self):
        alunos, projetos = create_instances(str(RAIZ / "data/entradaProj2.26TAG.txt"))
        g = GaleShapley(alunos, projetos)
        for direcao in ("alunos", "projetos"):
            historico = g.executar_iteracoes(direcao)
            self.assertEqual([r.numero for r in historico], list(range(1, 11)))
            self.assertEqual(len(historico[0].pares), 57)
            self.assertEqual(len(historico[-1].pares), 60)
            for anterior, atual in zip(historico, historico[1:]):
                self.assertEqual(
                    len(atual.pares) - len(anterior.pares), int(bool(atual.caminho))
                )
            for rodada in historico:
                self.verifica_solucao(g, rodada.pares)
            for p in projetos:
                self.assertTrue(all(a.projeto is p for a in p.alunos))
            for a in alunos:
                if a.projeto is not None:
                    self.assertIn(a, a.projeto.alunos)
            self.assertEqual(g.checa_estabilidade(), [])
            self.assertEqual(g.executar_iteracoes(direcao), historico)


if __name__ == "__main__":
    unittest.main()
