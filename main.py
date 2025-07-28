# ✅ main.py — с визуалом, звуком, темами, сохранением и поддержкой DLC

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

st.set_page_config(page_title="СУПОЛЮЦИЯ", page_icon="🥣", layout="centered")

# 🎨 Кастомный фон и цвет

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
        </style>
    """, unsafe_allow_html=True)

# 🔊 Звук

def play_sound(url):
    st.markdown(f"""
        <audio autoplay>
            <source src="{url}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

# 🧠 Стейт и загрузка
if "game_data" in st.session_state:
    game = SoupGame()
    game.load_state(st.session_state["game_data"])
else:
    game = SoupGame()

state = game.get_state()

# 🎨 Выбор темы
if "theme" not in st.session_state:
    st.session_state.theme = "Классика"

available_themes = [t for t in THEMES if t in state.get("unlocked_themes", ["Классика"])]
selected_theme = st.selectbox("🎨 Тема супа:", available_themes, index=available_themes.index(st.session_state.theme))
st.session_state.theme = selected_theme

apply_custom_style()

st.session_state.game_data = game.to_dict()

# 🧠 Заголовок и интро
st.title("🥣 СУПОЛЮЦИЯ")
st.markdown("**Ты — суп. Разумный. Не дай себя вылить.**")

if state["turn"] == 0 and not state["tech"]:
    st.markdown("""
        <div style='padding:1em; background:#fff5db; border-left: 5px solid orange; border-radius: 8px;'>
            <h4>📢 Ты — суп. И ты живой.</h4>
            <p>Развивай свою супную цивилизацию, строй союзы, принимай решения...</p>
            <p><b>Цель:</b> достичь <i>Супознания</i> до того, как тебя выльют в унитаз.</p>
        </div>
    """, unsafe_allow_html=True)

# 🧾 Статистика и ресурсы
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🌀 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Жизнь супа:** `{state['hp']}`")
with col2:
    st.markdown("📦 **Ресурсы:**")
    for k, v in state["resources"].items():
        st.markdown(f"- {k}: `{v}`")

# 🎉 Победа / 💀 Поражение
if state["status"] == "ascended":
    play_sound("https://cdn.pixabay.com/audio/2022/10/31/audio_8c8d2f5f20.mp3")
    st.balloons()
    st.success("🎉 Суп стал сверхсуществом! Победа.")
    st.button("Играть снова", on_click=lambda: st.session_state.clear())
    st.stop()

if state["status"] == "flushed":
    play_sound("https://cdn.pixabay.com/audio/2023/04/28/audio_13fa01aa09.mp3")
    st.error("🚽 Суп вылили в унитаз. Всё пропало.")
    st.button("Попробовать снова", on_click=lambda: st.session_state.clear())
    st.stop()

# 📜 Хроники событий
st.divider()
st.markdown("### 📜 Супные хроники:")
for e in reversed(state["events_log"]):
    st.markdown(f"- {e}")

# 🏛️ Фракции
st.markdown("### 🏛️ Фракции:")
for name, value in state["factions"].items():
    bar = "🟩" * max(0, value) + "🟥" * max(0, -value)
    st.markdown(f"**{name}**: `{value}` {bar}")

# 🎭 Сюжетные выборы
if state.get("current_choice"):
    choice = state["current_choice"]
    st.markdown("### ⚖️ Судьбоносный выбор!")
    st.markdown(f"**{choice['text']}**")
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Согласен"):
        game.resolve_choice("yes")
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if col_b.button("❌ Отказаться"):
        game.resolve_choice("no")
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 🔬 Апгрейды (технологии)
st.markdown("### 🔬 Новые технологии:")
choices = game.get_upgrade_choices()
if not choices:
    st.warning("Все технологии изучены. Просто нажми 'Следующий ход'.")
    if st.button("Следующий ход"):
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
    st.stop()

selected_name = st.radio("Выбери технологию:", [c["name"] for c in choices])
selected_upgrade = next(u for u in choices if u["name"] == selected_name)
st.markdown(f"🔍 **Описание:** {selected_upgrade['desc']}")

if st.button("📈 Применить и перейти к следующему ходу"):
    play_sound("https://cdn.pixabay.com/audio/2022/03/15/audio_3fd16212d1.mp3")
    game.apply_upgrade(selected_name)
    game.next_turn()
    st.session_state.game_data = game.to_dict()
    st.rerun()

# 📊 Доп. информация
st.divider()
with st.expander("📊 Статистика цивилизации"):
    st.markdown("**🧱 Постройки:**")
    if state["structures"]:
        for s in state["structures"]:
            st.markdown(f"- 🏗️ {s}")
    else:
        st.markdown("_Пока ничего не построено._")

    st.markdown("**📘 Изученные технологии:**")
    if state["tech"]:
        for t in state["tech"]:
            st.markdown(f"- {t}")
    else:
        st.markdown("_Суп ещё не познал ни одной истины._")
