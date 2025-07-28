# ✅ main.py — оптимизировано для детей: ярче, понятнее, с иконками и весельем

import streamlit as st
from soup_game import SoupGame

THEMES = {
    "Классика": {
        "background": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGM4NmMyMmJjZjM3N2VkZGVkYmMyYmQ0YWI4ZjM2YjFkZGM4Y2QzZiZjdD1n/ZybDTC3S3kAUE/giphy.gif",
        "tone": "#fffbe6"
    },
    "Томатный апокалипсис": {
        "background": "https://media.giphy.com/media/fAnEC88LccN7a/giphy.gif",
        "tone": "#ffe6e6"
    },
    "Грибной лес": {
        "background": "https://media.giphy.com/media/l0HlGdELQG9UE6NfK/giphy.gif",
        "tone": "#f0fff0"
    },
    "Тёмный борщ": {
        "background": "https://media.giphy.com/media/3ohfFq2FFpE4BSPJ4s/giphy.gif",
        "tone": "#1a001a"
    }
}

st.set_page_config(page_title="🥣 СУПОЛЮЦИЯ для детей", page_icon="🧒", layout="centered")

# 🎨 Стиль с весёлым фоном и цветами

def apply_custom_style():
    theme = THEMES.get(st.session_state.get("theme", "Классика"), THEMES["Классика"])
    background = theme["background"]
    tone = theme["tone"]
    st.markdown(f"""
        <style>
        body {{
            background-image: url('{background}');
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        .stApp {{
            background-color: {tone};
            padding: 2rem;
            border-radius: 25px;
        }}
        h1, h2, h3, .stMarkdown p {{
            font-family: 'Comic Sans MS', cursive;
        }}
        </style>
    """, unsafe_allow_html=True)

# 🔊 Звук (весёлый и мультяшный)

def play_sound(url):
    st.markdown(f"""
        <audio autoplay>
            <source src="{url}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

# 🎮 Инициализация
if "game_data" in st.session_state:
    game = SoupGame()
    game.load_state(st.session_state["game_data"])
else:
    game = SoupGame()

state = game.get_state()

if "theme" not in st.session_state:
    st.session_state.theme = "Классика"

available_themes = [t for t in THEMES if t in state.get("unlocked_themes", ["Классика"])]
selected_theme = st.selectbox("🌈 Выбери стиль игры:", available_themes, index=available_themes.index(st.session_state.theme))
st.session_state.theme = selected_theme

apply_custom_style()
st.session_state.game_data = game.to_dict()

# 🧒 Весёлый заголовок
st.title("🥳 СУПОЛЮЦИЯ: Детская версия")
st.markdown("🧠 Ты — суп! Развивайся, дружи и не дай себя вылить в раковину!")

if state["turn"] == 0 and not state["tech"]:
    st.markdown("""
        <div style='padding:1em; background:#fff5db; border-left: 5px solid orange; border-radius: 8px;'>
            <h4>👋 Привет, Супчик!</h4>
            <p>Ты только родился в кастрюле, и у тебя много дел!</p>
            <p><b>Задача:</b> стать самым умным супом до того, как откроется холодильник!</p>
        </div>
    """, unsafe_allow_html=True)

# 🔢 Ходы и ресурсы
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🕓 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Жизнь супа:** `{state['hp']}`")
with col2:
    st.markdown("🍔 **Супные ресурсы:**")
    for k, v in state["resources"].items():
        emoji = "🍗" if k == "белки" else "🥓" if k == "жиры" else "🍞"
        st.markdown(f"- {emoji} {k}: `{v}`")

# 🏆 Победа и поражение
if state["status"] == "ascended":
    play_sound("https://cdn.pixabay.com/audio/2022/10/31/audio_8c8d2f5f20.mp3")
    st.balloons()
    st.success("🎉 Ты победил! Суп стал умнее всех в кастрюле!")
    st.button("Играть снова", on_click=lambda: st.session_state.clear())
    st.stop()

if state["status"] == "flushed":
    play_sound("https://cdn.pixabay.com/audio/2023/04/28/audio_13fa01aa09.mp3")
    st.error("💦 Упс! Тебя вылили... Попробуем ещё раз!")
    st.button("Попробовать снова", on_click=lambda: st.session_state.clear())
    st.stop()

# 🎲 Хроники и фракции
st.markdown("### 📖 Весёлые истории:")
for e in reversed(state["events_log"]):
    st.markdown(f"- {e}")

st.markdown("### 👫 Друзья супа:")
for name, value in state["factions"].items():
    face = "😀" if value >= 2 else "😐" if value >= 0 else "😠"
    st.markdown(f"**{name}**: `{value}` {face}")

# 🤔 Супный выбор
if state.get("current_choice"):
    choice = state["current_choice"]
    st.markdown("### ❓ Супный вопрос!")
    st.markdown(f"**{choice['text']}**")
    col_a, col_b = st.columns(2)
    if col_a.button("👍 Да!"):
        game.resolve_choice("yes")
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if col_b.button("👎 Нет!"):
        game.resolve_choice("no")
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 🔬 Технологии (весёлые и понятные)
st.markdown("### 🔍 Новые прикольные технологии:")
choices = game.get_upgrade_choices()
tech_tree = game.tech_tree

if not choices:
    st.warning("Все открытия уже сделаны. Жми 'Следующий ход'!")
    if st.button("👉 Следующий ход"):
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
    st.stop()

for choice in choices:
    deps = tech_tree.get(choice["name"], [])
    with st.expander(f"🧪 {choice['name']}"):
        st.markdown(f"**Что это?** {choice['desc']}")
        if deps:
            st.markdown(f"👣 Нужно сначала: {', '.join(deps)}")
        if st.button(f"🚀 Открыть — {choice['name']}"):
            play_sound("https://cdn.pixabay.com/audio/2022/03/15/audio_3fd16212d1.mp3")
            game.apply_upgrade(choice["name"])
            game.next_turn()
            st.session_state.game_data = game.to_dict()
            st.rerun()

# 📊 Доп. информация
st.divider()
with st.expander("📦 Что у тебя есть:"):
    st.markdown("**🏗️ Постройки:**")
    if state["structures"]:
        for s in state["structures"]:
            st.markdown(f"- 🧱 {s}")
    else:
        st.markdown("_Пока пусто._")

    st.markdown("**📚 Открытые технологии:**")
    if state["tech"]:
        for t in state["tech"]:
            st.markdown(f"- {t}")
    else:
        st.markdown("_Ты ещё ничего не изобрёл._")
