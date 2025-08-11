import streamlit as st
import pandas as pd
import plotly.express as px

#Definir o título da página, o ícone e o layout
st.set_page_config(
    page_title = "Dashboard de Salários Anuais na Área de Dados",
    page_icon = "💸", #https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
    layout = "wide",
)

df = pd.read_csv("dados_tratados_imersao.csv")

#Definir os filtros que estarão disponíveis em um menu lateral
st.sidebar.header("🔍 Filtros")

#Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default = anos_disponiveis)

#Filtro de Senioridade
senioriadade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionadas = st.sidebar.multiselect("Nível de Experiência", senioriadade_disponiveis, default = senioriadade_disponiveis)

#Filtro de Modelo de Trabalho
modelos_disponiveis = sorted(df['modelo_trabalho'].unique())
modelos_selecionados = st.sidebar.multiselect("Modelo de Trabalho", modelos_disponiveis, default = modelos_disponiveis)

#Filtro de Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default = tamanhos_disponiveis)

#Criar a filtragem com base nos itens selecionados no filtro criado acima
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionadas)) &
    (df['modelo_trabalho'].isin(modelos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

#Exibir as informações em tela
st.title("Dashboard: Análise Salarial na Área de Dados")
st.markdown("Explore os dados salariais anuais na área de dados dos últimos anos")

#Exibição das métricas
st.subheader("Principais Métricas")

#caso todas as variável df_filtrado estejam preenchidas, exibir as informações de acordo com os filtros selecionados
if not df_filtrado.empty:
    salario_medio = df_filtrado['salario_usd'].mean()
    salario_maximo = df_filtrado['salario_usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
#caso alguma variavel de df_filtrado esteja vazia, indicando que nenhum filtro foi selecionado, não exibir nenhuma informação
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, "Selecione uma opção"

#dividir a seção em 4 colunas para exibir as informações
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio Anual: ", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo Anual: ", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros: ", f"${total_registros:,.0f}")
col4.metric("Cargo mais frequente: ", cargo_mais_frequente)

st.markdown("--")

#Exibição dos gráficos
st.subheader("Gráficos")

#dividir a exibição dos gráficos em 2 colunas
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        #exibir os 10 maiores cargos
        top_cargos = df_filtrado.groupby('cargo')['salario_usd'].mean().nlargest(10).sort_values(ascending = True).reset_index()
        grafico_barra_cargos = px.bar(
            top_cargos,
            x = 'salario_usd',
            y = "cargo",
            orientation = 'h', #exibição na horizontal
            title = 'Top 10 Cargos por Salário',
            labels = {'salario_usd': 'Salário Médio Anual (USD)', 'cargo': ''}
        )
        grafico_barra_cargos.update_layout(title_x = 0.1, yaxis = {'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_barra_cargos, use_container_width = True)
    else:
        st.warning("Nenhum dado a ser exibido, selecione um filtro.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist_salarios = px.histogram(
            df_filtrado,
            x = 'salario_usd',
            nbins = 30,
            title = 'Distruibuição de Salários Anuais',
            labels = {'salario_usd': 'Salário Médio Anual (USD)', 'count': 'Quantidade'}
        )
        grafico_hist_salarios.update_layout(title_x = 0.1)
        st.plotly_chart(grafico_hist_salarios, use_container_width = True)
    else:
        st.warning("Nenhum dado a ser exibido, selecione um filtro.")

#dividir a exibição dos gráficos em 2 colunas
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        modelo_contagem = df_filtrado['modelo_trabalho'].value_counts().reset_index()
        modelo_contagem.columns = ['modelo_trabalho', 'quantidade']
        grafico_pizza_modelos = px.pie(
            modelo_contagem,
            names = 'modelo_trabalho',
            values = 'quantidade',
            title = 'Distruibuição dos Modelos de Trabalho',
            hole = 0.5
        )
        grafico_pizza_modelos.update_traces(textinfo = 'percent+label')
        grafico_pizza_modelos.update_layout(title_x = 0.1)
        st.plotly_chart(grafico_pizza_modelos, use_container_width = True)
    else:
        st.warning("Nenhum dado a ser exibido, selecione um filtro.")

with col_graf4:
    if not df_filtrado.empty:
        df_datascience = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_salarial_pais = df_datascience.groupby('residencia_iso3')['salario_usd'].mean().reset_index()
        grafico_mapa_paises = px.choropleth(
            media_salarial_pais,
            locations = 'residencia_iso3',
            color = 'salario_usd',
            color_continuous_scale = 'rdylgn', #https://plotly.com/python/builtin-colorscales/
            title = "Salário Médio de Cientista de Dados por País",
            labels = {'salario_usd': 'Salário Médio Anual (USD)', 'residencia_iso3': 'País'},
        )
        grafico_mapa_paises.update_layout(title_x = 0.1)
        st.plotly_chart(grafico_mapa_paises, use_container_width = True)
    else:
        st.warning("Nenhum dado a ser exibido, selecione um filtro.")

st.subheader("Dados Detalhados")
if not df_filtrado.empty:
    st.dataframe(df_filtrado)
else:
    st.warning("Nenhum dado a ser exibido, selecione um filtro.")