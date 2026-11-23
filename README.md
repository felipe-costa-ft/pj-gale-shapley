## Bibliotecas utilizadas

Matplotlib - Gerar as visualizações dos grafos.

NetworkX - Representar e desenhar o grafo bipartido de alunos e projetos.

JupyterLab - Criar e executar o notebook de entrega do projeto.

## Pseudocódigos de Gale–Shapley

As duas direções começam limpando as alocações anteriores. Cada aluno pode ocupar
no máximo um projeto, e cada projeto respeita sua quantidade de vagas.

### Alunos → projetos

```text
Limpar o projeto atual de cada aluno e os alunos aceitos de cada projeto
Colocar todos os alunos na fila de pendentes
Inicializar a próxima preferência de cada aluno

Enquanto houver alunos pendentes:
    Retirar o primeiro aluno da fila

    Enquanto o aluno tiver preferências não tentadas:
        Selecionar o próximo projeto
        Avançar a próxima preferência do aluno

        Se a nota do aluno for menor que a mínima:
            Continuar para a próxima preferência

        Se o projeto tiver vaga:
            Criar relação entre aluno e projeto
            Parar as propostas desse aluno

        Senão:
            Encontrar o aluno de menor nota no projeto

            Se o candidato tiver nota maior:
                Liberar o aluno de menor nota
                Colocar o liberado na fila de pendentes
                Criar relação entre candidato e projeto
                Parar as propostas desse aluno

Retornar os pares aluno–projeto
```

Nos empates de nota, permanece o aluno já aceito. Um aluno substituído retoma as
propostas a partir de sua próxima preferência ainda não tentada.

### Projetos → alunos

```text
Limpar o projeto atual de cada aluno e os alunos aceitos de cada projeto

Para cada projeto:
    Listar os alunos que o escolheram e atendem à nota mínima
    Ordenar os candidatos por nota decrescente
    Inicializar o próximo candidato

Colocar todos os projetos na fila de pendentes

Enquanto houver projetos pendentes:
    Retirar o primeiro projeto da fila

    Enquanto o projeto tiver vaga e candidatos não tentados:
        Selecionar o próximo candidato
        Avançar o próximo candidato do projeto

        Se o aluno estiver alocado e não preferir o projeto proponente:
            Continuar para o próximo candidato

        Se o aluno já estiver alocado:
            Removê-lo do projeto anterior

            Se o anterior tiver candidatos não tentados
            e ainda não estiver na fila:
                Colocar o projeto anterior na fila

        Criar relação entre aluno e projeto

Retornar os pares aluno–projeto
```

Nos empates de nota, a ordenação preserva a ordem original dos candidatos. Um
projeto que volta à fila retoma as propostas a partir do próximo candidato ainda
não tentado.

## Caminhos alternados e dez iterações

Cada direção é executada em dez rodadas independentes da outra direção:

- A primeira rodada calcula o emparelhamento inicial com Gale–Shapley.
- Da segunda à décima, a busca parte dos alunos sem projeto e procura um caminho
  alternado até um projeto com vaga. Nos projetos cheios, qualquer aluno aceito
  pode ser realocado, inclusive quando sua nota difere da nota de quem entra.
- A busca segue a ordem dos alunos, das preferências e dos alunos aceitos, sem
  sorteios e sem repetir vértices no mesmo caminho.
- Cada caminho é aplicado provisoriamente. Se criar pares bloqueadores, todas as
  alocações anteriores são restauradas e a busca continua por outro caminho.
- Cada rodada aceita no máximo um aumento. Mesmo sem aumento, a rodada é
  registrada com o emparelhamento e as quantidades de tentativas e rejeições.

O histórico fica disponível no retorno de `executar_iteracoes`. A execução pelo
`main` mostra os dez resultados de cada direção; a direção dos projetos é exibida
por último. A validação usa estabilidade fraca: notas iguais não são preferência
estrita. A busca é uma heurística e não comprova o máximo estável nem garante
preencher projetos sem candidatos elegíveis. Enumerar caminhos simples pode
exigir tempo exponencial em instâncias maiores.

Nos dados fornecidos, as duas direções passam de 57 para 60 alunos alocados:
57 na primeira rodada, 58 na segunda, 59 na terceira e 60 da quarta à décima.
Os aumentos aceitos preservam a estabilidade fraca.

Para executar, a partir da raiz do repositório:

```bash
python src/main.py
```

Para rodar os testes:

```bash
python -m unittest discover -s tests -v
```
