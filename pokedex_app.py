import streamlit as st
import requests

# URL base da API.
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon:
    # O construtor é chamado quando criamos um novo objeto Pokemon.
    def __init__(self, name, url):
        # Armazena o nome e a URL.
        self.name = name.title()
        self.url = url
        # Inicializamos todos os outros atributos como None (nulo).
        # Eles serão preenchidos pelo método fetch_details.
        self.id = None
        self.tipos = []
        self.habilidades = []
        self.altura = None
        self.peso = None
        self.imagem_url = None # Atributo para a URL da imagem.
        self.stats = {}

    # Método para buscar todos os detalhes do Pokémon na API.
    def fetch_details(self):
        # ----- PONTO DE VERIFICAÇÃO 1 -----
        # Este print aparecerá no seu terminal.
        print(f"--- Buscando dados para: {self.name} ---")

        try:
            # Faz a requisição para a API.
            response = requests.get(self.url)
            # Verifica se a requisição deu certo.
            response.raise_for_status()
            # Converte a resposta para o formato JSON (dicionário Python).
            data = response.json()

            # Extração segura dos dados. .get() evita erros se a chave não existir.
            self.id = data.get('id')
            self.altura = data.get('height', 0) / 10
            self.peso = data.get('weight', 0) / 10

            # --- Extração segura e verificada da IMAGEM ---
            # Navegamos passo a passo, usando .get() com um dicionário vazio {} como padrão.
            sprites = data.get('sprites', {})
            other = sprites.get('other', {})
            official_artwork = other.get('official-artwork', {})
            # A URL final. Se qualquer passo anterior falhar, o resultado será None.
            url_encontrada = official_artwork.get('front_default')

            self.imagem_url = url_encontrada

            # ----- PONTO DE VERIFICAÇÃO 2 -----
            # Este print nos dirá se a URL foi encontrada ou não.
            print(f"URL da Imagem: {self.imagem_url}")

            # Extrai os tipos, usando uma lista vazia [] como padrão.
            self.tipos = [t['type']['name'].title() for t in data.get('types', [])]
            # Extrai as habilidades.
            self.habilidades = [a['ability']['name'].title() for a in data.get('abilities', [])]

            # Extrai os status.
            self.stats = {}
            for stat in data.get('stats', []):
                stat_name = stat['stat']['name'].replace('-', ' ').title()
                base_stat = stat['base_stat']
                self.stats[stat_name] = base_stat

        except requests.exceptions.RequestException as e:
            st.error(f"Erro de rede ao buscar {self.name}: {e}")
        except Exception as e:
            # Captura qualquer outro erro que possa ocorrer durante a extração dos dados.
            st.error(f"Erro ao processar os dados de {self.name}: {e}")
            print(f"OCORREU UM ERRO AO PROCESSAR {self.name}: {e}")

# Função para buscar a lista dos 151 Pokémons (com cache para não recarregar toda hora).
@st.cache_data
def get_pokemon_list():
    url = f"{BASE_URL}?limit=1025"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['results']
    except requests.exceptions.RequestException as e:
        st.error(f"Não foi possível carregar a lista de Pokémons da API. Verifique sua conexão. Erro: {e}")
        return []

# Configurações da página.
st.set_page_config(page_title="Pokédex", page_icon="🔴")
st.title("Pokédex - Kanto")

# Carrega a lista de Pokémons.
pokemon_list = get_pokemon_list()

if pokemon_list:
    # Cria a lista de nomes para o seletor.
    pokemon_names = [f"{i+1} - {p['name'].title()}" for i, p in enumerate(pokemon_list)]
    
    # Cria o seletor na barra lateral.
    selected_pokemon_name = st.sidebar.selectbox("Escolha um Pokémon:", pokemon_names)

    # Acha os dados do Pokémon selecionado.
    selected_index = pokemon_names.index(selected_pokemon_name)
    selected_pokemon_data = pokemon_list[selected_index]

    # Cria o objeto Pokemon e busca seus detalhes.
    pokemon = Pokemon(selected_pokemon_data['name'], selected_pokemon_data['url'])
    pokemon.fetch_details()

    # Organiza a exibição em colunas.
    col1, col2 = st.columns([1, 2])

    with col1:
        # Só tenta mostrar a imagem se a URL não for nula (None).
        if pokemon.imagem_url:
            st.image(pokemon.imagem_url, caption=pokemon.name)
        else:
            # Mensagem de aviso se não encontrar a imagem.
            st.warning("Imagem não disponível.")

    with col2:
        # Exibe as informações básicas.
        st.subheader(f"{pokemon.name} #{pokemon.id:03d}")
        st.write(f"**Tipos:** {', '.join(pokemon.tipos)}")
        st.write(f"**Altura:** {pokemon.altura} m")
        st.write(f"**Peso:** {pokemon.peso} kg")
        st.write(f"**Habilidades:** {', '.join(pokemon.habilidades)}")

    # Exibe os status base.
    st.subheader("Status Base")
    # Itera sobre os status e os exibe.
    for stat_name, stat_value in pokemon.stats.items():
        st.text(stat_name)
        # A barra de progresso vai de 0 a 1. Dividimos por 255 (um valor máximo comum para status).
        st.progress(stat_value / 255)

