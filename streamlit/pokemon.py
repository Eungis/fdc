import streamlit as st

# session state
# reload page when refreshed by default.

print(st.session_state)

st.set_page_config(page_title="Pokemon Dictionary", page_icon="./images/monsterball.png")

# custom css
st.markdown(
    """
<style>
h1 {
    color: red;
}
img {
    max-height: 300px;
}
.st-emotion-cache-1clstc5 div {
    display: flex;
    justify-content: center;
    font-size: 20px;
}
[data-testid="stExpanderToggleIcon"] {
    visibility: hidden;
}
.st-emotion-cache-p5msec {
    pointer-events: none;
}

[data-testid="StyledFullScreenButton"] {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("streamlit pokemon")
st.markdown("add **pokemon** to fill out the pokemon dictionary")

type_emoji_dict = {
    "노말": "⚪",
    "격투": "✊",
    "비행": "🕊",
    "독": "☠️",
    "땅": "🌋",
    "바위": "🪨",
    "벌레": "🐛",
    "고스트": "👻",
    "강철": "🤖",
    "불꽃": "🔥",
    "물": "💧",
    "풀": "🍃",
    "전기": "⚡",
    "에스퍼": "🔮",
    "얼음": "❄️",
    "드래곤": "🐲",
    "악": "😈",
    "페어리": "🧚",
}

initial_pokemons = [
    {
        "name": "누오",
        "types": ["물", "땅"],
        "image_url": "https://i.namu.wiki/i/yuKkJ-6J_5JN3-I0rPJ18kuhsay_oS1H7949AJAkwUu4a425UCYSEOxdNVNzdGV97eVT3xJOxCUAFjqUdfXBwcayIGVIg2Np5Wk5I21R9Muvr1rRvbp6aXHNM389cwwyxOKP27SNwZxrwign4XUsXIIblsB5p1BLpqZrM5kIW54.webp",
    },
    {
        "name": "누오",
        "types": ["물", "땅"],
        "image_url": "https://i.namu.wiki/i/yuKkJ-6J_5JN3-I0rPJ18kuhsay_oS1H7949AJAkwUu4a425UCYSEOxdNVNzdGV97eVT3xJOxCUAFjqUdfXBwcayIGVIg2Np5Wk5I21R9Muvr1rRvbp6aXHNM389cwwyxOKP27SNwZxrwign4XUsXIIblsB5p1BLpqZrM5kIW54.webp",
    },
    {
        "name": "누오",
        "types": ["물", "땅"],
        "image_url": "https://i.namu.wiki/i/yuKkJ-6J_5JN3-I0rPJ18kuhsay_oS1H7949AJAkwUu4a425UCYSEOxdNVNzdGV97eVT3xJOxCUAFjqUdfXBwcayIGVIg2Np5Wk5I21R9Muvr1rRvbp6aXHNM389cwwyxOKP27SNwZxrwign4XUsXIIblsB5p1BLpqZrM5kIW54.webp",
    },
    {
        "name": "누오",
        "types": ["물", "땅"],
        "image_url": "https://i.namu.wiki/i/yuKkJ-6J_5JN3-I0rPJ18kuhsay_oS1H7949AJAkwUu4a425UCYSEOxdNVNzdGV97eVT3xJOxCUAFjqUdfXBwcayIGVIg2Np5Wk5I21R9Muvr1rRvbp6aXHNM389cwwyxOKP27SNwZxrwign4XUsXIIblsB5p1BLpqZrM5kIW54.webp",
    },
    {
        "name": "누오",
        "types": ["물", "땅"],
        "image_url": "https://i.namu.wiki/i/yuKkJ-6J_5JN3-I0rPJ18kuhsay_oS1H7949AJAkwUu4a425UCYSEOxdNVNzdGV97eVT3xJOxCUAFjqUdfXBwcayIGVIg2Np5Wk5I21R9Muvr1rRvbp6aXHNM389cwwyxOKP27SNwZxrwign4XUsXIIblsB5p1BLpqZrM5kIW54.webp",
    },
    {
        "name": "누오",
        "types": ["물", "땅"],
        "image_url": "https://i.namu.wiki/i/yuKkJ-6J_5JN3-I0rPJ18kuhsay_oS1H7949AJAkwUu4a425UCYSEOxdNVNzdGV97eVT3xJOxCUAFjqUdfXBwcayIGVIg2Np5Wk5I21R9Muvr1rRvbp6aXHNM389cwwyxOKP27SNwZxrwign4XUsXIIblsB5p1BLpqZrM5kIW54.webp",
    },
]

if "pokemons" not in st.session_state:
    st.session_state.pokemons = initial_pokemons

example_pokemon = {
    "name": "알로라 디그다",
    "types": ["땅", "강철"],
    "image_url": "https://storage.googleapis.com/firstpenguine-coding-school/pokemons/alora_digda.webp",
}

auto_complete = st.toggle("Fill out example")

with st.form(key="form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(label="Pokemon Name", value=example_pokemon["name"] if auto_complete else "")
    with col2:
        types = st.multiselect(
            label="types",
            options=list(type_emoji_dict.keys()),
            max_selections=2,
            default=example_pokemon["types"] if auto_complete else [],
        )
    image_url = st.text_input(label="Image URL", value=example_pokemon["image_url"] if auto_complete else "")
    submit = st.form_submit_button(label="Submit")
    if submit:
        if not name:
            st.error("Enter in Pokemon Name")
        elif len(types) == 0:
            st.error("Specify the Pokemon Types")
        else:
            st.success("You can add the new Pokemon.")
            st.session_state.pokemons.append(
                {"name": name, "types": types, "image_url": image_url if image_url else "./images/default.png"}
            )


for i in range(0, len(st.session_state.pokemons), 3):
    row_pokemons = st.session_state.pokemons[i : i + 3]
    cols = st.columns(3)
    for j in range(len(row_pokemons)):
        with cols[j]:
            pokemon = row_pokemons[j]
            with st.expander(label=f"{pokemon['name']}_{i+j}", expanded=True):
                st.image(pokemon["image_url"])
                st.text("description")
                emojis = [f"{_type} {type_emoji_dict[_type]}" for _type in pokemon["types"]]
                st.text(" / ".join(emojis))
                delete_button = st.button(label="delete", key=i + j, use_container_width=True)
                if delete_button:
                    # when delete button clicked, the page reload one time.
                    # to refresh the session_state right after deletion,
                    # explicitly reload page using st.rerun().
                    del st.session_state.pokemons[i + j]
                    st.rerun()
