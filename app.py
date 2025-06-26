import streamlit as st
from database import criar_tabelas, adicionar_produto, listar_produtos, atualizar_produto, remover_produto, registrar_venda, listar_vendas
from auth import verificar_login, cadastrar_usuario
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Controle de Estoque", page_icon="📦", layout="centered")

# Inicializar banco de dados
criar_tabelas()

# Gerenciar sessão de usuário
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# Função principal
def main():
    st.title("Controle de Estoque Youth 📦")

    if st.session_state.usuario_logado:
        st.success(f"Usuário logado: {st.session_state.usuario_logado}")
        menu_principal()
    else:
        aba = st.tabs(["Login", "Cadastro"])
        with aba[0]:
            tela_login()
        with aba[1]:
            tela_cadastro()

def tela_login():
    st.subheader("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if verificar_login(usuario, senha):
            st.session_state.usuario_logado = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def tela_cadastro():
    st.subheader("Cadastro de Novo Usuário")
    novo_usuario = st.text_input("Novo usuário")
    nova_senha = st.text_input("Nova senha", type="password")
    if st.button("Cadastrar"):
        if cadastrar_usuario(novo_usuario, nova_senha):
            st.success("Usuário cadastrado com sucesso! Faça login.")
        else:
            st.warning("Nome de usuário já existe.")

def menu_principal():
    opcoes = ["Ver Estoque", "Adicionar Produto", "Atualizar Produto", "Remover Produto", 
                "Registrar Venda", "Histórico de Vendas", "Sair"]
    escolha = st.sidebar.radio("Menu", opcoes)

    if escolha == "Ver Estoque":
        st.subheader("Estoque Atual")
        produtos = listar_produtos()
        if produtos:
            st.dataframe([{"Nome": p[1], "Quantidade": p[2], "Preço (R$)": f"{p[3]:.2f}"} for p in produtos],
            hide_index=True,
            column_order=["Nome", "Quantidade", "Preço (R$)"],
            use_container_width=True)
        else:
            st.info("Nenhum produto cadastrado.")


    elif escolha == "Adicionar Produto":
        st.subheader("Adicionar Novo Produto")
        nome = st.text_input("Nome do Produto")
        quantidade = st.number_input("Quantidade", min_value=0, step=1)
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")

        if "produto_adicionado" not in st.session_state:
            st.session_state.produto_adicionado = False
        if st.button("Adicionar"):
            try:
                adicionar_produto(nome, quantidade, preco)
                st.session_state.produto_adicionado = True
                st.rerun()
            except Exception as e:
                st.error(f"Produto já cadastrado! Entre em Atualizar Produto para atualizar o estoque.")
        if st.session_state.produto_adicionado:
            st.success("Produto adicionado com sucesso!")
            st.session_state.produto_adicionado = False



    elif escolha == "Atualizar Produto":
        st.subheader("Atualizar Produto")
        produtos = listar_produtos()
        if produtos:
            nomes = [f"{p[1]}" for p in produtos]
            selecionado = st.selectbox("Escolha um produto", nomes)
            produto = produtos[nomes.index(selecionado)]

            nova_qtd = st.number_input("Nova Quantidade", min_value=0, value=produto[2], step=1)
            novo_preco = st.number_input("Novo Preço (R$)", min_value=0.0, value=produto[3], format="%.2f")

            if "produto_atualizado" not in st.session_state:
                st.session_state.produto_atualizado = False
            if st.button("Salvar Alterações"):
                atualizar_produto(produto[0], nova_qtd, novo_preco)
                st.session_state.produto_atualizado = True
                st.rerun()
            if st.session_state.produto_atualizado:
                st.success("Produto atualizado com sucesso!")
                st.session_state.produto_atualizado = False       
        else:
            st.info("Nenhum produto cadastrado.")



    elif escolha == "Remover Produto":
        st.subheader("Remover Produto")
        produtos = listar_produtos()
        if produtos:
            nomes = [f"{p[1]}" for p in produtos]
            selecionado = st.selectbox("Selecione o produto para remover", nomes)
            produto = produtos[nomes.index(selecionado)]

            with st.expander("⚠️ Confirmar remoção", expanded=True):
                st.warning(f"Tem certeza que deseja remover o produto **{produto[1]}**? Essa ação não pode ser desfeita.")
                if st.button("Sim, remover produto"):
                    remover_produto(produto[0])
                    st.success("Produto removido com sucesso.")
                    st.rerun()
        else:
            st.info("Nenhum produto cadastrado.")


    elif escolha == "Registrar Venda":
        st.subheader("Registrar Venda de Produto")
        produtos = listar_produtos()
        if produtos:
            nomes = [f"{p[1]} (Estoque: {p[2]})" for p in produtos]
            selecionado = st.selectbox("Selecione o produto vendido", nomes)
            produto = produtos[nomes.index(selecionado)]
            
            if produto[2] > 0:
                qtd_vendida = st.number_input("Quantidade vendida", min_value=1, max_value=produto[2], step=1)
                if st.button("Confirmar Venda"):
                    sucesso = registrar_venda(produto[0], qtd_vendida)
                    if sucesso:
                        st.success("Venda registrada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro: estoque insuficiente.")
            else:
                st.warning("Estoque esgotado. Não é possível registrar vendas para este item.")        
        else:
            st.info("Nenhum produto cadastrado.")
    


    elif escolha == "Histórico de Vendas":
        st.subheader("Histórico de Vendas")
        vendas = listar_vendas()
        if not vendas:
            st.info("Nenhuma venda registrada ainda.")
        else:
            dados = [
                {"ID": v[0],
                "Produto": v[1],
                "Quantidade": v[2],
                "Data": datetime.fromisoformat(v[3])} for v in vendas]
            df = pd.DataFrame(dados)

            # Filtros
            produtos = df["Produto"].unique().tolist()
            produto_filtro = st.selectbox("Filtrar por produto", ["Todos"] + produtos)
            data_min = df["Data"].min().date()
            data_max = df["Data"].max().date()
            try:
                data_inicial, data_final = st.date_input("Intervalo de datas", (data_min, data_max))
            except ValueError:
                st.error("Por favor, selecione uma data válida.")

            # Aplicar filtros
            if produto_filtro != "Todos":
                df = df[df["Produto"] == produto_filtro]
            try:
                df = df[(df["Data"].dt.date >= data_inicial) & (df["Data"].dt.date <= data_final)]
            except ValueError:
                st.error("Por favor, selecione uma data válida.")

            # Mostrar tabela
            df_exibir = df.copy()
            df_exibir["Data"] = df_exibir["Data"].dt.strftime("%d/%m/%Y")
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)

            if df.empty:
                st.warning("Nenhuma venda encontrada com os filtros selecionados.")

            
            st.markdown("---")
            st.subheader("📊 Análises de Vendas")

            total_vendido = df["Quantidade"].sum()
            st.metric("Total de Itens Vendidos", total_vendido)

            vendas_por_produto = df.groupby("Produto")["Quantidade"].sum().sort_values(ascending=False)

            st.bar_chart(vendas_por_produto)

            vendas_por_dia = df.groupby(df["Data"].dt.date)["Quantidade"].sum()
            st.line_chart(vendas_por_dia)



    elif escolha == "Sair":
        st.session_state.usuario_logado = None
        st.rerun()



# Rodar app
if __name__ == "__main__":
    main()
