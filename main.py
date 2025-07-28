# main.py

import streamlit as st
from soup_game import SoupGame

st.set_page_config(page_title="СУПОЛЮЦИЯ", page_icon="🥣", layout="centered")

def apply_custom_style():
    st.markdown("""
        <style>
        body {
            background-image: url('https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGM4NmMyMmJjZjM3N2VkZGVkYmMyYmQ0YWI4ZjM2YjFkZGM4Y2QzZiZjdD1n/ZybDTC3S3kAUE/giphy.gif');
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }
        .stApp {
            background-color: rgba(255, 255, 255, 0.88);
            padding: 2rem;
            border-radius: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

def play_sound(url):
    st.markdown(f"""
        <audio autoplay>
            <source src="{url}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

apply_custom_style()

if "game" not in st.session_state:
    st.session_state.game = SoupGame()

game = st.session_state.game
state = game.get_state()

st.title("🥣 СУПОЛЮЦИЯ")
st.markdown("**Ты — суп. Разумный. Не дай себя вылить.**")

if state["turn"] == 0 and not state["tech"]:
    st.markdown("""
        <div style='padding:1em; background:#fff5db; border-left: 5px solid orange; border-radius: 8px;'>
            <h4>📢 Ты — суп. И ты живой.</h4>
            <p>В этом холодильнике кипит жизнь. Развивай свою супную цивилизацию, заключай союзы, строй храмы... и постарайся не быть вылитым в унитаз.</p>
            <p><b>Твоя миссия:</b> обрести <i>Супознание</i> до того, как откроется дверца холодильника.</p>
        </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🌀 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Жизнь супа:** `{state['hp']}`")

with col2:
    st.markdown("📦 **Ресурсы:**")
    for k, v in state["resources"].items():
        st.markdown(f"- {k}: `{v}`")

if state["status"] == "ascended":
    play_sound("https://cdn.pixabay.com/audio/2022/10/31/audio_8c8d2f5f20.mp3")
    st.balloons()
    st.success("🎉 Суп стал существом высшего порядка. Поздравляем с супознанием!")
    st.button("Играть снова", on_click=lambda: st.session_state.clear())
    st.stop()

if state["status"] == "flushed":
    play_sound("https://cdn.pixabay.com/audio/2023/04/28/audio_13fa01aa09.mp3")
    st.error("🚽 О нет! Кто-то слил тебя в унитаз... Суп проиграл.")
    st.button("Попробовать снова", on_click=lambda: st.session_state.clear())
    st.stop()

st.divider()
st.markdown("### 📜 Супные хроники:")
for e in reversed(state["events_log"]):
    st.markdown(f"- {e}")

st.markdown("### 🏛️ Фракции супа:")
for name, value in state["factions"].items():
    bar = "🟩" * max(0, value) + "🟥" * max(0, -value)
    st.markdown(f"**{name}**: `{value}` {bar}")

if state.get("current_choice"):
    choice = state["current_choice"]
    st.markdown("### ⚖️ Судьбоносный выбор!")
    st.markdown(f"**{choice['text']}**")
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Согласен"):
        game.resolve_choice("yes")
        st.rerun()
    if col_b.button("❌ Отказаться"):
        game.resolve_choice("no")
        st.rerun()

st.markdown("### 🔬 Новые технологии:")
choices = game.get_upgrade_choices()

if not choices:
    st.warning("Все технологии изучены. Просто нажми 'Следующий ход'.")
    if st.button("Следующий ход"):
        game.next_turn()
        st.rerun()
    st.stop()

selected_name = st.radio("Выбери технологию:", [c["name"] for c in choices])
selected_upgrade = next(u for u in choices if u["name"] == selected_name)
st.markdown(f"🔍 **Описание:** {selected_upgrade['desc']}")

if st.button("📈 Применить и перейти к следующему ходу"):
    play_sound("https://cdn.pixabay.com/audio/2022/03/15/audio_3fd16212d1.mp3")
    game.apply_upgrade(selected_name)
    game.next_turn()
    st.rerun()

st.divider()
with st.expander("📊 Статистика цивилизации"):
    st.markdown("**🧱 Постройки:**")
    for s in state["structures"]:
        st.markdown(f"- 🏗️ {s}") if state["structures"] else st.markdown("_Ещё ничего не построено._")

    st.markdown("**📘 Изученные технологии:**")
    for t in state["tech"]:
        st.markdown(f"- {t}") if state["tech"] else st.markdown("_Суп ещё не познал ни одной истины._")
