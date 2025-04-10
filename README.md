# Sistema de Controle de Armários

Este é um aplicativo Streamlit para gerenciar a alocação e liberação de armários escolares ou institucionais.

## Requisitos

```
pip install -r requirements.txt
```

## Como executar

```
streamlit run app_completo.py
```

## Estrutura de arquivos

- `app.py`: Código principal do aplicativo Streamlit com todas as funcionalidades
- `armarios.xlsx`: Planilha com informações sobre os armários (localização e faixas de numeração)
- `registros_armarios.csv`: Arquivo CSV que armazena os registros de alocação
- `historico_armarios.csv`: Arquivo CSV que armazena o histórico de operações

## Estrutura da planilha armarios.xlsx

A planilha deve conter as seguintes colunas:
- **Localização**: local onde os armários estão (ex: Bloco A, Andar 2, etc)
- **Início**: número do primeiro armário da faixa
- **Fim**: número do último armário da faixa

Exemplo:

| Localização | Início | Fim |
|------------|--------|-----|
| Bloco A    | 1      | 50  |
| Bloco B    | 51     | 100 |

## Funcionalidades

- **Visão Geral**: Visualização de todos os armários com filtros por status e localização
- **Alocar Armário**: Formulário para alocar um armário a um aluno
- **Liberar Armário**: Opções para liberar um armário ocupado
- **Pesquisar**: Busca por número de armário, nome de aluno ou turma
- **Relatórios**: Geração de relatórios e gráficos de ocupação
- **Histórico**: Visualização do histórico de alocações e liberações

## Recursos adicionais

- **Exportação de dados**: Exportação de relatórios em formato Excel
- **Gráficos**: Visualização gráfica da ocupação de armários
- **Histórico de operações**: Registro de todas as alocações e liberações
- **Interface amigável**: Design responsivo e intuitivo