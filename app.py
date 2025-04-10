import streamlit as st
import pandas as pd
import os
import datetime
# import io
# import base64
# import matplotlib.pyplot as plt
# import seaborn as sns
# import PIL
# import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Controle de Armários",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para criar um cabeçalho estilizado
def header_estilizado(titulo, icone="🔐"):
    st.markdown(f"<h1 style='text-align: center; color: #1E88E5;'>{icone} {titulo}</h1>", unsafe_allow_html=True)
    st.markdown("---")

# Título do aplicativo
header_estilizado("Sistema de Controle de Armários")

# Função para carregar os dados dos armários da planilha Excel
def carregar_dados_armarios():
    try:
        # Tente carregar a planilha Excel com as informações dos armários
        df_info = pd.read_excel('armarios.xlsx')
        return df_info
    except Exception as e:
        st.error(f"Erro ao carregar a planilha de armários: {e}")
        return None

# Função para carregar os registros existentes
def carregar_registros():
    if os.path.exists('registros_armarios.csv'):
        df = pd.read_csv('registros_armarios.csv')
        # Converte a coluna 'numero' para inteiro se não for nulo
        if 'numero' in df.columns:
            df['numero'] = pd.to_numeric(df['numero'], errors='coerce').fillna(0).astype(int)
        return df
    else:
        # Se o arquivo não existir, cria um DataFrame vazio com as colunas necessárias
        return pd.DataFrame(columns=['numero', 'localizacao', 'nome', 'turma', 'status', 'data'])

# Função para salvar os registros
def salvar_registros(df):
    df.to_csv('registros_armarios.csv', index=False)

# Função para inicializar os registros com base nas informações dos armários
def inicializar_registros(df_info):
    registros = carregar_registros()
    
    # Se o arquivo de registros estiver vazio (apenas cabeçalho), inicializa com os armários disponíveis
    if len(registros) == 0:
        novos_registros = []
        
        # Para cada linha na planilha de informações
        for _, row in df_info.iterrows():
            localizacao = row['Localização']
            inicio = int(row['Início'])
            fim = int(row['Fim'])
            
            # Cria um registro para cada armário no intervalo
            for numero in range(inicio, fim + 1):
                novos_registros.append({
                    'numero': numero,
                    'localizacao': localizacao,
                    'nome': '',
                    'turma': '',
                    'status': 'Disponível',
                    'data': ''
                })
        
        # Cria um novo DataFrame com os registros e salva
        registros = pd.DataFrame(novos_registros)
        salvar_registros(registros)
    
    return registros

# Carrega as informações dos armários
df_info_armarios = carregar_dados_armarios()

# Se conseguiu carregar as informações, inicializa os registros
if df_info_armarios is not None:
    df_registros = inicializar_registros(df_info_armarios)
    
    # Sidebar para navegação
    st.sidebar.title("Navegação")
    opcao = st.sidebar.radio(
        "Selecione uma opção:",
        ["Visão Geral", "Alocar Armário", "Liberar Armário", "Pesquisar"]
    )
    
    # Visão Geral
    if opcao == "Visão Geral":
        st.header("Visão Geral dos Armários")
        
        # Estatísticas
        total_armarios = len(df_registros)
        ocupados = len(df_registros[df_registros['status'] == 'Ocupado'])
        disponiveis = total_armarios - ocupados
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Armários", total_armarios)
        col2.metric("Armários Ocupados", ocupados)
        col3.metric("Armários Disponíveis", disponiveis)
        
        # Filtros
        st.subheader("Filtros")
        col1, col2 = st.columns(2)
        with col1:
            filtro_status = st.selectbox(
                "Status",
                ["Todos", "Disponível", "Ocupado"]
            )
        with col2:
            localizacoes = ["Todas"] + df_registros['localizacao'].unique().tolist()
            filtro_localizacao = st.selectbox("Localização", localizacoes)
        
        # Aplicar filtros
        df_filtrado = df_registros.copy()
        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
        if filtro_localizacao != "Todas":
            df_filtrado = df_filtrado[df_filtrado['localizacao'] == filtro_localizacao]
        
        # Exibir tabela filtrada
        st.dataframe(df_filtrado)
    
    # Alocar Armário
    elif opcao == "Alocar Armário":
        st.header("Alocar Armário")
        
        # Filtros para encontrar armários disponíveis
        localizacoes = ["Todas"] + df_registros['localizacao'].unique().tolist()
        filtro_localizacao = st.selectbox("Localização", localizacoes)
        
        # Filtrar armários disponíveis
        df_disponiveis = df_registros[df_registros['status'] == 'Disponível']
        if filtro_localizacao != "Todas":
            df_disponiveis = df_disponiveis[df_disponiveis['localizacao'] == filtro_localizacao]
        
        if len(df_disponiveis) > 0:
            # Formulário para alocação
            with st.form("form_alocacao"):
                st.subheader("Dados do Aluno")
                
                # Selecionar armário disponível
                armarios_disponiveis = df_disponiveis['numero'].tolist()
                numero_armario = st.selectbox("Número do Armário", armarios_disponiveis)
                
                # Dados do aluno
                nome_aluno = st.text_input("Nome do Aluno")
                turma_aluno = st.text_input("Turma")
                
                # Botão de submissão
                submitted = st.form_submit_button("Alocar Armário")
                
                if submitted:
                    if nome_aluno and turma_aluno:
                        # Atualiza o registro
                        idx = df_registros[df_registros['numero'] == numero_armario].index[0]
                        df_registros.at[idx, 'nome'] = nome_aluno
                        df_registros.at[idx, 'turma'] = turma_aluno
                        df_registros.at[idx, 'status'] = 'Ocupado'
                        df_registros.at[idx, 'data'] = datetime.datetime.now().strftime("%Y-%m-%d")
                        
                        # Salva os registros atualizados
                        salvar_registros(df_registros)
                        
                        st.success(f"Armário {numero_armario} alocado com sucesso para {nome_aluno}!")
                    else:
                        st.error("Por favor, preencha todos os campos.")
        else:
            st.warning("Não há armários disponíveis com os filtros selecionados.")
    
    # Liberar Armário
    elif opcao == "Liberar Armário":
        st.header("Liberar Armário")
        
        # Filtrar apenas armários ocupados
        df_ocupados = df_registros[df_registros['status'] == 'Ocupado']
        
        if len(df_ocupados) > 0:
            # Opções para pesquisar o armário a ser liberado
            opcao_pesquisa = st.radio(
                "Pesquisar por:",
                ["Número do Armário", "Nome do Aluno"]
            )
            
            if opcao_pesquisa == "Número do Armário":
                armarios_ocupados = df_ocupados['numero'].tolist()
                numero_armario = st.selectbox("Selecione o Armário", armarios_ocupados)
                
                # Exibe informações do armário selecionado
                armario_info = df_ocupados[df_ocupados['numero'] == numero_armario].iloc[0]
                st.info(f"Armário {numero_armario} - Localização: {armario_info['localizacao']}")
                st.info(f"Ocupado por: {armario_info['nome']} - Turma: {armario_info['turma']}")
                
                if st.button("Liberar este Armário"):
                    # Atualiza o registro
                    idx = df_registros[df_registros['numero'] == numero_armario].index[0]
                    df_registros.at[idx, 'nome'] = ''
                    df_registros.at[idx, 'turma'] = ''
                    df_registros.at[idx, 'status'] = 'Disponível'
                    df_registros.at[idx, 'data'] = ''
                    
                    # Salva os registros atualizados
                    salvar_registros(df_registros)
                    
                    st.success(f"Armário {numero_armario} liberado com sucesso!")
            
            else:  # Pesquisa por nome
                nome_pesquisa = st.text_input("Digite o nome do aluno")
                
                if nome_pesquisa:
                    # Filtra por nome (case insensitive e parcial)
                    resultados = df_ocupados[df_ocupados['nome'].str.contains(nome_pesquisa, case=False)]
                    
                    if len(resultados) > 0:
                        st.subheader("Resultados encontrados:")
                        st.dataframe(resultados[['numero', 'localizacao', 'nome', 'turma']])
                        
                        # Seleciona o armário a ser liberado
                        armarios_encontrados = resultados['numero'].tolist()
                        armario_liberar = st.selectbox("Selecione o armário para liberar", armarios_encontrados)
                        
                        if st.button("Liberar Armário Selecionado"):
                            # Atualiza o registro
                            idx = df_registros[df_registros['numero'] == armario_liberar].index[0]
                            df_registros.at[idx, 'nome'] = ''
                            df_registros.at[idx, 'turma'] = ''
                            df_registros.at[idx, 'status'] = 'Disponível'
                            df_registros.at[idx, 'data'] = ''
                            
                            # Salva os registros atualizados
                            salvar_registros(df_registros)
                            
                            st.success(f"Armário {armario_liberar} liberado com sucesso!")
                    else:
                        st.warning(f"Nenhum aluno encontrado com o nome '{nome_pesquisa}'.")
        else:
            st.info("Não há armários ocupados no momento.")
    
    # Pesquisar
    elif opcao == "Pesquisar":
        st.header("Pesquisar Armários")
        
        # Opções de pesquisa
        opcao_pesquisa = st.radio(
            "Pesquisar por:",
            ["Número do Armário", "Nome do Aluno", "Turma"]
        )
        
        if opcao_pesquisa == "Número do Armário":
            numero_pesquisa = st.number_input("Digite o número do armário", min_value=1, step=1)
            
            if st.button("Pesquisar"):
                resultado = df_registros[df_registros['numero'] == numero_pesquisa]
                
                if len(resultado) > 0:
                    armario = resultado.iloc[0]
                    st.subheader(f"Armário {numero_pesquisa}")
                    st.write(f"**Localização:** {armario['localizacao']}")
                    st.write(f"**Status:** {armario['status']}")
                    
                    if armario['status'] == 'Ocupado':
                        st.write(f"**Nome:** {armario['nome']}")
                        st.write(f"**Turma:** {armario['turma']}")
                        st.write(f"**Data de alocação:** {armario['data']}")
                else:
                    st.warning(f"Armário {numero_pesquisa} não encontrado.")
        
        elif opcao_pesquisa == "Nome do Aluno":
            nome_pesquisa = st.text_input("Digite o nome do aluno")

            if nome_pesquisa and st.button("Pesquisar"):
                resultados = df_registros[df_registros['nome'].fillna('').str.contains(nome_pesquisa, case=False)]

                if len(resultados) > 0:
                    st.subheader("Resultados encontrados:")
                    st.dataframe(resultados)
                else:
                    st.warning(f"Nenhum aluno encontrado com o nome '{nome_pesquisa}'.")
        
        else:  # Pesquisa por turma
            turma_pesquisa = st.text_input("Digite a turma")

            if turma_pesquisa and st.button("Pesquisar"):
                resultados = df_registros[df_registros['turma'].fillna('').str.contains(turma_pesquisa, case=False)]

                if len(resultados) > 0:
                    st.subheader("Resultados encontrados:")
                    st.dataframe(resultados)
                else:
                    st.warning(f"Nenhum aluno encontrado na turma '{turma_pesquisa}'.")
else:
    st.error("Não foi possível carregar as informações dos armários. Verifique se o arquivo 'armarios.xlsx' existe e está no formato correto.")
    
    # Exibe o formato esperado da planilha
    st.info("""
    O arquivo 'armarios.xlsx' deve conter as seguintes colunas:
    - Localização: local onde os armários estão (ex: Bloco A, Andar 2, etc)
    - Início: número do primeiro armário da faixa
    - Fim: número do último armário da faixa
    
    Exemplo:
    | Localização | Início | Fim |
    |------------|--------|-----|
    | Bloco A    | 1      | 50  |
    | Bloco B    | 51     | 100 |
    """)