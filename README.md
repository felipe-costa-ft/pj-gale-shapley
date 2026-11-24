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

Cada direção tem uma inicialização e dez rodadas de melhoria, independentes da
outra direção:

- Gale–Shapley calcula o emparelhamento inicial, fora das dez iterações. Esse
  estado é registrado no histórico com o número 0.
- Da primeira à décima rodada, a busca parte dos alunos sem projeto e procura um caminho
  alternado até um projeto com vaga. Nos projetos cheios, qualquer aluno aceito
  pode ser realocado, inclusive quando sua nota difere da nota de quem entra.
- A busca segue a ordem dos alunos, das preferências e dos alunos aceitos, sem
  sorteios e sem repetir vértices no mesmo caminho.
- Cada caminho é aplicado provisoriamente. Se criar pares bloqueadores, todas as
  alocações anteriores são restauradas e a busca continua por outro caminho.
- Cada rodada aceita no máximo um aumento. Mesmo sem aumento, a rodada é
  registrada com o emparelhamento e as quantidades de tentativas e rejeições.

O histórico fica disponível no retorno de `executar_iteracoes`. A execução pelo
`main` mostra o estado inicial e os dez resultados de cada direção; a direção dos projetos é exibida
por último. A validação usa estabilidade fraca: notas iguais não são preferência
estrita. A busca é uma heurística e não comprova o máximo estável nem garante
preencher projetos sem candidatos elegíveis. Enumerar caminhos simples pode
exigir tempo exponencial em instâncias maiores.

Nos dados fornecidos, as duas direções passam de 57 para 60 alunos alocados:
57 no estado inicial, 58 na primeira rodada, 59 na segunda e 60 da terceira à décima.
Os aumentos aceitos preservam a estabilidade fraca.

Para executar, a partir da raiz do repositório:

```bash
python src/main.py
```

Para rodar os testes:

```bash
python -m unittest discover -s tests -v
```

## Índice de preferência e tabela final

Ao executar `python src/main.py`, a pasta `resultados/` recebe tabelas HTML e CSV
das duas direções. `resultados_projetos.html` identifica a proposta final;
`resultados_alunos.html` permite a comparação.

O índice de preferência mede a procura por cada projeto:

```text
Índice = 3 × primeiras escolhas + 2 × segundas escolhas + terceiras escolhas
```

Essa fórmula é uma convenção do projeto, pois o enunciado não a especifica.
Todos os interessados são contados, inclusive os que não atingem a nota mínima.
As tabelas mostram separadamente os candidatos elegíveis, as vagas e a ocupação.

A matriz final inclui todos os alunos, com projeto alocado, nota, ordem de escolha
do projeto e classificação do aluno entre os candidatos elegíveis do projeto.
Notas iguais recebem a mesma classificação, sem criar uma preferência estrita
artificial: por exemplo, notas 5, 4, 4, 3 correspondem às posições 1, 2, 2, 4.
Para não alocados, os campos da alocação ficam vazios no CSV e com traços no HTML.
As ordens de escolha consideram apenas projetos válidos, após a limpeza da entrada.

## Visualização das rodadas e dos eventos

Com o ambiente virtual ativado e as dependências instaladas, execute:

```bash
python src/main.py
open resultados/visualizacao_projetos.html
```

`visualizacao_alunos.html` mostra a outra direção. As páginas funcionam localmente,
sem servidor ou conexão com a internet. Selecione o Gale–Shapley inicial ou uma das
dez rodadas, depois use os botões ou o controle de eventos para percorrer a execução.
O botão Reproduzir anima os eventos da rodada selecionada. A opção de mostrar todas
as relações elegíveis também exibe as arestas que não estão no emparelhamento.

As cores das arestas são:

- Azul: proposta ativa de um aluno, projeto ou caminho aumentante.
- Verde: emparelhamento temporário ou aumento aceito.
- Vermelho tracejado: proposta rejeitada, relação desfeita ou caminho rejeitado.
- Cinza: relação elegível que serve de contexto.

Os eventos são registrados durante o algoritmo, inclusive as simulações de caminhos
que são rejeitados por instabilidade. O estado temporário de uma simulação ainda
não foi validado; na rejeição, a alocação anterior é restaurada. O motivo da rejeição
é exibido junto ao grafo. Os eventos guardam apenas mudanças nas arestas, e o
histórico de cada rodada permite reconstruir os estados intermediários.

Também são gerados `rodadas_alunos.pdf` e `rodadas_projetos.pdf`, cada um com 11
páginas (inicialização e dez rodadas), e `grafo_final_alunos.png` e
`grafo_final_projetos.png`. Esses arquivos estáticos mostram os emparelhamentos ao
fim das rodadas; os três estados das propostas podem ser inspecionados no HTML.
