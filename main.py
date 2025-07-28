# main.py

import streamlit as st
from soup_game import SoupGame

# ⬛ Настройки страницы
st.set_page_config(page_title="СУПОЛЮЦИЯ", page_icon="🥣", layout="centered")

# 🧼 Кастомный фон и стили
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

apply_custom_style()

# 🧠 Инициализация игры
if "game" not in st.session_state:
    st.session_state.game = SoupGame()

game = st.session_state.game
state = game.get_state()

# 🥄 Заголовок
st.title("🥣 СУПОЛЮЦИЯ")
st.markdown("**Ты — суп. Разумный. Не дай себя вылить.**")

# 🧾 Всплывающее супное интро
if state["turn"] == 0 and not state["tech"]:
    st.markdown("""
        <div style='padding:1em; background:#fff5db; border-left: 5px solid orange; border-radius: 8px;'>
            <h4>📢 Ты — суп. И ты живой.</h4>
            <p>В этом холодильнике кипит жизнь. Развивай свою супную цивилизацию, заключай союзы, строй храмы... и постарайся не быть вылитым в унитаз.</p>
            <p><b>Твоя миссия:</b> обрести <i>Супознание</i> до того, как откроется дверца холодильника.</p>
        </div>
    """, unsafe_allow_html=True)

# 📊 Основная информация
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🌀 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Жизнь супа:** `{state['hp']}`")

with col2:
    st.markdown("📦 **Ресурсы:**")
    for k, v in state["resources"].items():
        st.markdown(f"- {k}: `{v}`")

# ✅ Победа
if state["status"] == "ascended":
    st.balloons()
    st.success("🎉 Суп стал существом высшего порядка. Поздравляем с супознанием!")
    st.button("Играть снова", on_click=lambda: st.session_state.clear())
    st.stop()

# 💀 Поражение
if state["status"] == "flushed":
    st.error("🚽 О нет! Кто-то слил тебя в унитаз... Суп проиграл.")
    st.button("Попробовать снова", on_click=lambda: st.session_state.clear())
    st.stop()

st.divider()

# 🧾 Супные хроники
st.markdown("### 📜 Супные хроники:")
if state["events_log"]:
    for e in reversed(state["events_log"]):
        st.markdown(f"- {e}")
else:
    st.markdown("_Пока всё тихо в кастрюле..._")

# 🏛️ Репутация фракций
st.markdown("### 🏛️ Фракции супа:")
for name, value in state["factions"].items():
    bar = "🟩" * max(0, value) + "🟥" * max(0, -value)
    st.markdown(f"**{name}**: `{value}` {bar}")

# 🧪 Технологии (апгрейды)
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
    game.apply_upgrade(selected_name)
    game.next_turn()
    st.rerun()

# 🧬 Доп. инфо
st.divider()
with st.expander("📊 Статистика цивилизации"):
    st.markdown("**🧱 Постройки:**")
    if state["structures"]:
        for s in state["structures"]:
            st.markdown(f"- 🏗️ {s}")
    else:
        st.markdown("_Ещё ничего не построено._")

    st.markdown("**📘 Изученные технологии:**")
    if state["tech"]:
        for t in state["tech"]:
            st.markdown(f"- {t}")
    else:
        st.markdown("_Суп ещё не познал ни одной истины._")
