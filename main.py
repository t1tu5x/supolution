# main.py

import streamlit as st
from soup_game import SoupGame

st.set_page_config(page_title="СУПОЛЮЦИЯ", page_icon="🥣", layout="centered")

if "game" not in st.session_state:
    st.session_state.game = SoupGame()

game = st.session_state.game
state = game.get_state()

# Заголовок
st.title("🥣 СУПОЛЮЦИЯ")
st.markdown("**Добро пожаловать в ХОЛОДИЛЬНИК.** Здесь кипит разум и судьба.")

# Основной статус
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🌀 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Жизнь супа:** `{state['hp']}`")

with col2:
    st.markdown("📦 **Ресурсы:**")
    for k, v in state["resources"].items():
        st.markdown(f"- {k}: `{v}`")

# Победа
if state["status"] == "ascended":
    st.balloons()
    st.success("🎉 Суп стал существом высшего порядка. Поздравляем с супознанием!")
    st.button("Играть снова", on_click=lambda: st.session_state.clear())
    st.stop()

# Поражение
if state["status"] == "flushed":
    st.error("🚽 О нет! Кто-то слил тебя в унитаз... Суп проиграл.")
    st.button("Попробовать снова", on_click=lambda: st.session_state.clear())
    st.stop()

st.divider()

# 📚 Журнал последних событий
st.markdown("### 📜 Супные хроники:")
if state["events_log"]:
    for e in reversed(state["events_log"]):
        st.markdown(f"- {e}")
else:
    st.markdown("_Суп пока мирен..._")

# 🛐 Фракции и репутация
st.markdown("### 🏛️ Фракции супа:")
for name, value in state["factions"].items():
    bar = "🟩" * max(0, value) + "🟥" * max(0, -value)
    st.markdown(f"**{name}**: {value} {bar}")

# 🧪 Доступные улучшения
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

# 🧠 Статус цивилизации
st.divider()
with st.expander("📊 Статистика цивилизации"):
    st.markdown("**🧱 Постройки:**")
    if state["structures"]:
        for s in state["structures"]:
            st.markdown(f"- 🏗️ {s}")
    else:
        st.markdown("_Пока ничего не построено_")

    st.markdown("**🧬 Изученные технологии:**")
    if state["tech"]:
        for t in state["tech"]:
            st.markdown(f"- 📘 {t}")
    else:
        st.markdown("_Суп ещё не познал ни одной истины_")
