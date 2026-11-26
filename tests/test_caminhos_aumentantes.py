import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from caminhos_aumentantes import executar_sem_estabilidade
from gale_shapley import GaleShapley, IteracaoEmparelhamento
from models.Aluno import Aluno
from models.Projeto import Projeto
from utils.parser import create_instances


class TestSemEstabilidade(unittest.TestCase):
    def test_aceita_aumento_mesmo_criando_bloqueio(self):
        p1, p2 = Projeto("P1", 1, 3), Projeto("P2", 1, 3)
        a1, a2 = Aluno("A1", [p1, p2], 5), Aluno("A2", [p1], 4)
        g = GaleShapley([a1, a2], [p1, p2])
        g.aluno_para_projetos()
        h = executar_sem_estabilidade(g)
        self.assertIsInstance(h[0], IteracaoEmparelhamento)
        self.assertEqual([r.numero for r in h], list(range(11)))
        self.assertEqual([len(r.pares) for r in h], [1] + [2] * 10)
        self.assertEqual(h[0].bloqueadores, [])
        self.assertIn(("A1", "P1"), h[-1].bloqueadores)
        self.assertIs(a1.projeto, p2)
        self.assertIs(a2.projeto, p1)

    def test_respeita_notas_e_capacidades(self):
        p = Projeto("P1", 2, 4)
        alunos = [
            Aluno(f"A{i}", [p], nota)
            for i, nota in enumerate([3, 4, 5, 4], 1)
        ]
        g = GaleShapley(alunos, [p])
        h = executar_sem_estabilidade(g)
        self.assertEqual(len(h[-1].pares), 2)
        self.assertIsNone(alunos[0].projeto)
        self.assertEqual(len(p.alunos), 2)
        self.assertTrue(all(
            a.projeto is p and a.nota >= p.nota_min for a in p.alunos
        ))

    def test_entrada_vazia_e_argumento_invalido(self):
        g = GaleShapley([], [])
        h = executar_sem_estabilidade(g)
        self.assertEqual(len(h), 11)
        self.assertTrue(all(not r.pares and not r.caminho for r in h))
        with self.assertRaises(ValueError):
            executar_sem_estabilidade(g, 0)

    def test_dados_reais_partindo_dos_60_estaveis(self):
        for direcao in ("alunos", "projetos"):
            entrada = RAIZ / "data/entradaProj2.26TAG.txt"
            alunos, projetos = create_instances(str(entrada))
            g = GaleShapley(alunos, projetos)
            estavel = g.executar_iteracoes(direcao)
            h = executar_sem_estabilidade(g)
            self.assertEqual(len(estavel[-1].pares), 60)
            self.assertEqual(h[0].pares, estavel[-1].pares)
            self.assertEqual(len(h[-1].pares), 63)
            self.assertTrue(h[-1].bloqueadores)
            esperados = 5 if direcao == "alunos" else 6
            self.assertEqual(len(h[-1].bloqueadores), esperados)
            por_aluno = {a.label: a for a in alunos}
            for rodada in h:
                pares = rodada.pares
                self.assertEqual(len(dict(pares)), len(pares))
                for p in projetos:
                    aceitos = [
                        por_aluno[a] for a, projeto in pares
                        if projeto == p.label
                    ]
                    self.assertLessEqual(len(aceitos), p.vagas)
                    self.assertTrue(all(
                        p in a.preferencias and a.nota >= p.nota_min
                        for a in aceitos
                    ))
            for antes, depois in zip(h, h[1:]):
                self.assertEqual(
                    len(depois.pares) - len(antes.pares),
                    int(bool(depois.caminho)),
                )
            for p in projetos:
                self.assertTrue(all(a.projeto is p for a in p.alunos))
            # A fotografia do resultado estável não foi alterada pelo experimento.
            self.assertEqual(len(estavel[-1].pares), 60)


if __name__ == "__main__":
    unittest.main()
