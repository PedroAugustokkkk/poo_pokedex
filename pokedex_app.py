import streamlit as st
import requests

# Define a URL base da PokéAPI. Todas as nossas buscas de dados partirão daqui.
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

# Definimos a classe Pokemon, que servirá como um molde para criar objetos de cada Pokémon.
class Pokemon:
    def __init__(self, nome, url):
        self.nome = nome.title() # Nome do Pokemon, com a primeira letra maiúscula.
        self.url = url # url (link) específico daquele Pokemon.
        # Inicializa os outros atributos como None. Eles serão preenchidos depois pelo método fetch_details.
        self.id = None # ID na Pokédex.
        self.tipos = [] # tipo dele (fogo, agua/fogo e agua e etc)
        self.habilidades = [] # habilidades especificas daquele pokemon 
        self.altura = None
        self.peso = None
        self.imagem_url = None
        self.stats = {}

# Este método busca os detalhes completos do Pokémon na API usando a URL armazenada.
# Dentro da classe Pokemon

    def detalhes_busca(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()
            
            self.id = data.get('id')
            self.altura = data.get('height', 0) / 10
            self.peso = data.get('weight', 0) / 10

            sprites_data = data.get('sprites', {})
            other_data = sprites_data.get('other', {})
            artwork_data = other_data.get('official-artwork', {})
            self.imagem_url = artwork_data.get('front_default')

            # O mesmo princípio para as outras listas:
            self.tipos = [t['type']['name'].title() for t in data.get('types', [])]
            self.habilidades = [a['ability']['name'].title() for a in data.get('abilities', [])]

            self.stats = {}
            for stat in data.get('stats', []):
                stat_name = stat['stat']['name'].replace('-', ' ').title()
                base_stat = stat['base_stat']
                self.stats[stat_name] = base_stat

        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao buscar detalhes do Pokémon: {e}")

# função especifica do streamlit que guarda o resultado em cache para evitar chamadas repetidas
@st.cache_data
def pegar_lista_pokemon():
    url = f"{BASE_URL}?limit=151" # aqui definimos que são apenas 151 Pokemons
    try:
        response = requests.get(url) # Faz a requisição para a API.
        response.raise_for_status() # Verifica se a requisição foi bem-sucedida.
        data = response.json() # Converte o JSON em um dicionário.
        return data['results'] # Retorna a lista de resultados, que contém o nome e a URL de cada Pokémon.
    
    except requests.exceptions.RequestException as e: # Trata possíveis erros na requisição.
        st.error(f"Erro ao buscar a lista de Pokémons: {e}") # Exibe um erro no Streamlit
        return [] # retorna lista vazia

# Configura o título da página e o ícone que aparecem na aba do navegador.
st.set_page_config(page_title="Pokédex", page_icon="🔴")

# Define o título principal da aplicação que será exibido na página.
st.title("Pokédex - Os 151 Originais")
st.markdown("Aplicação feita com Python, POO e Streamlit, consumindo a [PokéAPI](https://pokeapi.co/).")

# Chama a função para obter a lista de Pokémons. O resultado virá do cache se já tiver sido chamado antes.
lista_pokemon = pegar_lista_pokemon()

# Verifica se a lista de Pokémons não está vazia.
if lista_pokemon:
    nome_pokemon = [f"{i+1} - {p['name'].title()}" for i, p in enumerate(lista_pokemon)] # exibe numero e pokemon
    # Cria um seletor (selectbox) na barra lateral (sidebar) com a lista de nomes que criamos.
    nome_selecionado = st.sidebar.selectbox("Escolha um Pokémon:", nome_pokemon)
    # Encontra o índice (posição) do Pokémon selecionado na lista.
    selected_index = nome_pokemon.index(nome_selecionado)
    # Pega o dicionário do Pokémon selecionado (contendo nome e url) da lista original.
    dados_pokemon = lista_pokemon[selected_index]
    # Cria uma instância (objeto) da nossa classe Pokemon com os dados do Pokémon selecionado.
    # Aqui a mágica da POO acontece: transformamos os dados brutos em um objeto estruturado.
    pokemon = Pokemon(dados_pokemon['name'], dados_pokemon['url'])
    # Chama o método para buscar todos os detalhes deste Pokémon na API.
    pokemon.detalhes_busca()

    # Agora, usamos os atributos do nosso objeto 'pokemon' para exibir as informações.

    # Divide a tela em duas colunas para organizar melhor a imagem e as informações básicas.
    col1, col2 = st.columns([1, 2]) # A coluna 2 será duas vezes maior que a 1.

    # Bloco 'with' para a primeira coluna.
    with col1:
        # Verifica se a URL da imagem foi encontrada.
        if pokemon.image_url:
            # Exibe a imagem do Pokémon.
            st.image(pokemon.image_url, caption=pokemon.name)

    # Bloco 'with' para a segunda coluna.
    with col2:
        # Exibe o nome e o ID do Pokémon como um subtítulo.
        st.subheader(f"{pokemon.nome} #{pokemon.id:03d}") # O :03d formata o número para ter sempre 3 dígitos (ex: 001).
        # Junta a lista de tipos em uma única string, separada por " / ".
        st.write(f"**Tipo:** {', '.join(pokemon.tipos)}")
        # Exibe a altura e o peso.
        st.write(f"**Altura:** {pokemon.altura} m")
        st.write(f"**Peso:** {pokemon.peso} kg")
        # Junta a lista de habilidades em uma única string.
        st.write(f"**Habilidades:** {', '.join(pokemon.habilidades)}")


    # Cria um subtítulo para a seção de status.
    st.subheader("Status Base")

    # Divide a área de status em duas colunas para não ficar muito comprida.
    stat_col1, stat_col2 = st.columns(2)

    # Itera sobre os itens (nome do status, valor) no dicionário de stats.
    # O `items()` nos dá tanto a chave quanto o valor a cada iteração.
    for i, (stat_nome, stat_valor) in enumerate(pokemon.stats.items()):
        # Se o índice for par, coloca o status na primeira coluna.
        if i % 2 == 0:
            with stat_col1:
                # Escreve o nome do status.
                st.text(stat_nome)
                # Cria uma barra de progresso para visualizar o valor do status. O valor máximo na API é geralmente em torno de 255.
                st.progress(stat_valor / 255)
        # Se o índice for ímpar, coloca na segunda coluna.
        else:
            with stat_col2:
                # Escreve o nome do status.
                st.text(stat_nome)
                # Cria a barra de progresso.

                st.progress(stat_valor / 255)
