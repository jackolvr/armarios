import streamlit as st
import pandas as pd
import os
import datetime
import io
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(
    page_title="Controle de Armários",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para criar um link de download para um DataFrame
def gerar_link_download_excel(df, nome_arquivo="dados"):
    # Criar um buffer de bytes para o arquivo Excel
    output = io.BytesIO()
    # Escrever o DataFrame para o buffer como um arquivo Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    # Obter os bytes do buffer
    dados_excel = output.getvalue()
    # Criar o link de download
    st.download_button(
        label=f"📥 Baixar dados em Excel",
        data=dados_excel,
        file_name=f"{nome_arquivo}_{datetime.datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Função para criar um gráfico de pizza da ocupação dos armários
def criar_grafico_ocupacao(ocupados, disponiveis):
    # Dados para o gráfico de pizza
    labels = ['Ocupados', 'Disponíveis']
    sizes = [ocupados, disponiveis]
    colors = ['#FF9966', '#66B2FF']  # Laranja claro e azul claro

    # Criar o gráfico de pizza
    fig, ax = plt.subplots(figsize=(4, 2))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=55,
        shadow=False,
        textprops={'fontsize': 6, 'weight': 'bold'}
    )

    # Personalizar cores dos textos
    for text in texts:
        text.set_color('#333333')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(6)
        autotext.set_weight('bold')

    ax.axis('equal')  # Garante que o gráfico seja um círculo
    #plt.title('Ocupação de Armários', fontsize=16, pad=20)
    plt.tight_layout()

    return fig

# Aplica o CSS customizado do arquivo styles.css
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Não foi possível carregar o CSS customizado: {e}")

# Função para criar um cabeçalho estilizado
def header_estilizado(titulo, icone="🔐"):
    st.markdown(f"<h1 style='text-align: center; color: #1E88E5;'>{icone} {titulo}</h1>", unsafe_allow_html=True)
    st.markdown("---")

# Título do aplicativo
header_estilizado("Sistema de Controle de Armários")

# Função para gerar um ID único para cada armário
def gerar_id_unico(numero, localizacao):
    # Remove espaços e caracteres especiais da localização
    loc_formatada = ''.join(e for e in localizacao if e.isalnum()).upper()
    # Cria um ID combinando a localização e o número
    return f"{loc_formatada}-{numero:04d}"

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
        return pd.DataFrame(columns=['id_unico', 'numero', 'localizacao', 'nome', 'turma', 'status', 'data'])

# Função para salvar os registros
def salvar_registros(df):
    df.to_csv('registros_armarios.csv', index=False)

# Função para inicializar os registros com base nas informações dos armários
def inicializar_registros(df_info):
    registros = carregar_registros()

    # Verifica se o arquivo de registros já tem a coluna id_unico
    if 'id_unico' not in registros.columns:
        # Se o arquivo existir mas não tiver a coluna id_unico, adiciona a coluna
        if len(registros) > 0:
            registros['id_unico'] = registros.apply(lambda row: gerar_id_unico(row['numero'], row['localizacao']), axis=1)
            salvar_registros(registros)
            return registros

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
                id_unico = gerar_id_unico(numero, localizacao)
                novos_registros.append({
                    'id_unico': id_unico,
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

        # Adicionar gráfico de pizza logo após o cabeçalho
        fig = criar_grafico_ocupacao(ocupados, disponiveis)
        st.pyplot(fig)

        # Métricas em cards
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

        # Exibir tabela filtrada sem o id_unico e sem índice
        colunas_exibir = [col for col in df_filtrado.columns if col != 'id_unico']
        st.dataframe(df_filtrado[colunas_exibir], hide_index=True)

        # Adicionar link para download dos dados filtrados
        if len(df_filtrado) > 0:
            nome_arquivo = "armarios_visao_geral"
            if filtro_status != "Todos":
                nome_arquivo += f"_{filtro_status.lower()}"
            if filtro_localizacao != "Todas":
                nome_arquivo += f"_{filtro_localizacao.replace(' ', '_').lower()}"

            gerar_link_download_excel(df_filtrado[colunas_exibir], nome_arquivo)

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

                # Selecionar armário disponível - sem mostrar o ID único na interface
                opcoes_armarios_display = [f"{row['numero']} - {row['localizacao']}" for _, row in df_disponiveis.iterrows()]
                # Dicionário para mapear a opção exibida para o ID único
                mapa_opcoes_para_id = {f"{row['numero']} - {row['localizacao']}": row['id_unico'] for _, row in df_disponiveis.iterrows()}

                armario_selecionado_display = st.selectbox("Selecione o Armário", opcoes_armarios_display)

                # Obter o ID único do armário selecionado usando o mapeamento
                id_unico_selecionado = mapa_opcoes_para_id[armario_selecionado_display]

                # Dados do aluno
                nome_aluno = st.text_input("Nome do Aluno")
                turma_aluno = st.text_input("Turma")

                # Botão de submissão
                submitted = st.form_submit_button("Alocar Armário")

                if submitted:
                    if nome_aluno and turma_aluno:
                        # Converter dados para UPPER CASE
                        nome_aluno = nome_aluno.upper()
                        turma_aluno = turma_aluno.upper()

                        # Atualiza o registro
                        idx = df_registros[df_registros['id_unico'] == id_unico_selecionado].index[0]
                        df_registros.at[idx, 'nome'] = nome_aluno
                        df_registros.at[idx, 'turma'] = turma_aluno
                        df_registros.at[idx, 'status'] = 'Ocupado'
                        df_registros.at[idx, 'data'] = datetime.datetime.now().strftime("%d-%m-%Y")

                        # Salva os registros atualizados
                        salvar_registros(df_registros)

                        st.success(f"Armário {armario_selecionado_display} alocado com sucesso para {nome_aluno}!")
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
                # Cria opções de seleção sem mostrar o ID único
                opcoes_armarios_display = [f"{row['numero']} - {row['localizacao']}" for _, row in df_ocupados.iterrows()]
                # Dicionário para mapear a opção exibida para o ID único
                mapa_opcoes_para_id = {f"{row['numero']} - {row['localizacao']}": row['id_unico'] for _, row in df_ocupados.iterrows()}

                armario_selecionado_display = st.selectbox("Selecione o Armário", opcoes_armarios_display)

                # Obter o ID único do armário selecionado usando o mapeamento
                id_unico_selecionado = mapa_opcoes_para_id[armario_selecionado_display]

                # Exibe informações do armário selecionado
                armario_info = df_ocupados[df_ocupados['id_unico'] == id_unico_selecionado].iloc[0]
                st.info(f"Armário {armario_info['numero']} - Localização: {armario_info['localizacao']}")
                st.info(f"Ocupado por: {armario_info['nome']} - Turma: {armario_info['turma']}")

                if st.button("Liberar este Armário"):
                    # Atualiza o registro
                    idx = df_registros[df_registros['id_unico'] == id_unico_selecionado].index[0]
                    df_registros.at[idx, 'nome'] = ''
                    df_registros.at[idx, 'turma'] = ''
                    df_registros.at[idx, 'status'] = 'Disponível'
                    df_registros.at[idx, 'data'] = ''

                    # Salva os registros atualizados
                    salvar_registros(df_registros)

                    st.success(f"Armário {armario_selecionado_display} liberado com sucesso!")

            else:  # Pesquisa por nome
                nome_pesquisa = st.text_input("Digite o nome do aluno")

                if nome_pesquisa:
                    # Converter para UPPER CASE para pesquisa
                    nome_pesquisa = nome_pesquisa.upper()

                    # Filtra por nome (case insensitive e parcial)
                    resultados = df_ocupados[df_ocupados['nome'].str.contains(nome_pesquisa, case=False)]

                    if len(resultados) > 0:
                        st.subheader("Resultados encontrados:")
                        # Exibir resultados sem mostrar o ID único
                        colunas_exibir = [col for col in resultados.columns if col != 'id_unico']
                        st.dataframe(resultados[colunas_exibir], hide_index=True)

                        # Seleciona o armário a ser liberado sem mostrar o ID único
                        opcoes_armarios_display = [f"{row['numero']} - {row['localizacao']}" for _, row in resultados.iterrows()]
                        # Dicionário para mapear a opção exibida para o ID único
                        mapa_opcoes_para_id = {f"{row['numero']} - {row['localizacao']}": row['id_unico'] for _, row in resultados.iterrows()}

                        armario_selecionado_display = st.selectbox("Selecione o armário para liberar", opcoes_armarios_display)

                        # Obter o ID único do armário selecionado usando o mapeamento
                        id_unico_selecionado = mapa_opcoes_para_id[armario_selecionado_display]

                        if st.button("Liberar Armário Selecionado"):
                            # Atualiza o registro
                            idx = df_registros[df_registros['id_unico'] == id_unico_selecionado].index[0]
                            df_registros.at[idx, 'nome'] = ''
                            df_registros.at[idx, 'turma'] = ''
                            df_registros.at[idx, 'status'] = 'Disponível'
                            df_registros.at[idx, 'data'] = ''

                            # Salva os registros atualizados
                            salvar_registros(df_registros)

                            st.success(f"Armário {armario_selecionado_display} liberado com sucesso!")
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

            # Botão de pesquisa sempre visível
            if st.button("Pesquisar"):
                # Filtrar apenas armários ocupados com o número especificado
                resultado = df_registros[(df_registros['numero'] == numero_pesquisa) &
                                        (df_registros['status'] == 'Ocupado')]

                if len(resultado) > 0:
                    st.subheader("Resultados encontrados:")
                    # Exibir resultados sem o ID único e sem índice
                    colunas_exibir = [col for col in resultado.columns if col != 'id_unico']
                    st.dataframe(resultado[colunas_exibir], hide_index=True)

                    # Adicionar link para download dos resultados
                    gerar_link_download_excel(resultado[colunas_exibir], f"armarios_numero_{numero_pesquisa}")

                    # Se houver mais de um armário com o mesmo número, mostra uma mensagem
                    if len(resultado) > 1:
                        st.info(f"Foram encontrados {len(resultado)} armários ocupados com o número {numero_pesquisa} em diferentes localizações.")
                else:
                    st.warning(f"Nenhum armário ocupado com o número {numero_pesquisa} foi encontrado.")

        elif opcao_pesquisa == "Nome do Aluno":
            # Campo de entrada para o nome do aluno
            nome_pesquisa = st.text_input("Digite o nome do aluno")

            # Botão de pesquisa sempre visível, independente do preenchimento do campo
            botao_pesquisar = st.button("Pesquisar")

            # Executa a pesquisa quando o botão for clicado e houver texto no campo
            if botao_pesquisar:
                if nome_pesquisa:
                    # Converter para UPPER CASE para pesquisa
                    nome_pesquisa = nome_pesquisa.upper()

                    resultados = df_registros[df_registros['nome'].fillna('').str.contains(nome_pesquisa, case=False)]

                    if len(resultados) > 0:
                        st.subheader("Resultados encontrados:")
                        # Exibir resultados sem o ID único e sem índice
                        colunas_exibir = [col for col in resultados.columns if col != 'id_unico']
                        st.dataframe(resultados[colunas_exibir], hide_index=True)

                        # Adicionar link para download dos resultados
                        nome_arquivo = f"armarios_aluno_{nome_pesquisa.replace(' ', '_').lower()}"
                        gerar_link_download_excel(resultados[colunas_exibir], nome_arquivo)
                    else:
                        st.warning(f"Nenhum aluno encontrado com o nome '{nome_pesquisa}'.")
                else:
                    st.warning("Por favor, digite um nome para pesquisar.")

        else:  # Pesquisa por turma
            # Campo de entrada para a turma
            turma_pesquisa = st.text_input("Digite a turma")

            # Botão de pesquisa sempre visível, independente do preenchimento do campo
            botao_pesquisar = st.button("Pesquisar")

            # Executa a pesquisa quando o botão for clicado e houver texto no campo
            if botao_pesquisar:
                if turma_pesquisa:
                    # Converter para UPPER CASE para pesquisa
                    turma_pesquisa = turma_pesquisa.upper()

                    resultados = df_registros[df_registros['turma'].fillna('').str.contains(turma_pesquisa, case=False)]

                    if len(resultados) > 0:
                        st.subheader("Resultados encontrados:")
                        # Exibir resultados sem o ID único e sem índice
                        colunas_exibir = [col for col in resultados.columns if col != 'id_unico']
                        st.dataframe(resultados[colunas_exibir], hide_index=True)

                        # Adicionar link para download dos resultados
                        nome_arquivo = f"armarios_turma_{turma_pesquisa.replace(' ', '_').lower()}"
                        gerar_link_download_excel(resultados[colunas_exibir], nome_arquivo)
                    else:
                        st.warning(f"Nenhum aluno encontrado na turma '{turma_pesquisa}'.")
                else:
                    st.warning("Por favor, digite uma turma para pesquisar.")
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
    |----|----|----|
    | Bloco A    | 1    | 50  |
    | Bloco B    | 51    | 100 |
    """)