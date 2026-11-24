## Bibliotecas utilizadas

Matplotlib - Gerar as visualizações dos grafos.

NetworkX - Representar e desenhar o grafo bipartido de alunos e projetos.

JupyterLab - Criar e executar o notebook de entrega do projeto.

## Pseudocódigos de Gale–Shapley

As duas execuções começam sem alocações. Cada aluno ocupa no máximo uma vaga,
e cada projeto aceita até o limite informado na entrada.

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

O resultado de Gale–Shapley é o estado inicial (0). Depois dele, cada direção faz
dez rodadas de melhoria, numeradas de 1 a 10. A busca parte dos alunos livres,
segue a ordem das preferências e procura um caminho alternado até uma vaga.
Cada caminho é simulado. Se criar pares bloqueadores, as trocas são desfeitas e
a busca continua. Cada rodada aceita no máximo um aumento.

A verificação usa estabilidade fraca: um projeto não prefere trocar alunos de
mesma nota. Na entrada fornecida, as duas direções passam de 57 para 60 alocados.
As dez rodadas não comprovam que esse total seja o máximo estável.

## Tabelas e gráficos

O índice de preferência mede a procura por projeto:

```text
índice = 3 × primeiras escolhas + 2 × segundas escolhas + terceiras escolhas
```

Essa fórmula foi escolhida porque o enunciado não a define. Todos os interessados
contam no índice; a coluna de elegíveis mostra quantos atingem a nota mínima.
A posição do aluno na lista do projeto considera apenas os elegíveis. Empatados
recebem a mesma posição, como em 1, 2, 2 e 4. As escolhas dos alunos são contadas
depois da remoção dos projetos inexistentes.

Os gráficos e as tabelas aparecem no notebook. Cada figura compara uma rodada
nas duas direções. Os recortes dos caminhos mostram propostas em azul,
emparelhamentos temporários ou aceitos em verde e rejeições em vermelho tracejado.
Guardamos o primeiro caminho rejeitado e o aumento aceito de cada rodada para
ilustrar essas etapas. As tabelas incluem a contagem de todas as tentativas.

## Como executar

Abra `Projeto2_Grafos.ipynb` no JupyterLab e execute as células em ordem a partir
da raiz do repositório:

```bash
jupyter lab Projeto2_Grafos.ipynb
```

No Colab, envie o notebook e `entradaProj2.26TAG.txt` pelo painel Arquivos.
O código está nas células; o arquivo de entrada é lido separadamente.
Antes de entregar, preencha os nomes e as matrículas na primeira célula.

Para executar pelos módulos Python e imprimir os resultados no terminal:

```bash
python src/main.py
```

Para rodar os testes:

```bash
python -m unittest discover -s tests -v
```

A entrega reúne o notebook com suas saídas e o mini-relatório pedido no enunciado.

## Problemas encontrados na entrada

P11, P13, P19, P32, P33, P42 e P46 não têm nenhum aluno que os tenha escolhido e
atinja a nota mínima. Com isso, a entrada não permite cumprir a exigência de
preencher todos os projetos. Há também referências a P51, P52, P53 e P54, que
não existem na lista e são descartadas na leitura.
