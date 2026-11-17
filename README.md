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
