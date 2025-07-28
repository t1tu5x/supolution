# main.py

import streamlit as st
from soup_game import SoupGame

# Настройка страницы
st.set_page_config(page_title="СУПОЛЮЦИЯ", page_icon="🍲", layout="centered")

# Инициализация состояния игры
if "game" not in st.session_state:
    st.session_state.game = SoupGame()

game = st.session_state.game
state = game.get_state()

# Заголовок
st.title("🥣 СУПОЛЮЦИЯ")
st.markdown("##### Ты — суп в холодильнике. Развивай цивилизацию, пока тебя не вылили в унитаз!")

# Статус и параметры супа
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"👣 **Ход:** {state['turn']} из {game.max_turns}")
    st.markdown(f"❤️ **Жизнь супа:** {state['hp']}")

with col2:
    st.markdown("📦 **Ресурсы:**")
    for k, v in state["resources"].items():
        st.markdown(f"- {k}: `{v}`")

st.divider()

# Победа
if state["status"] == "ascended":
    st.balloons()
    st.success("🎉 УРА! Твоя супная цивилизация обрела СУПОЗНАНИЕ и стала вкусным бессмертным духом!")
    st.button("Начать заново", on_click=lambda: st.session_state.clear())
    st.stop()

# Проигрыш
if state["status"] == "flushed":
    st.error("🚽 Увы... холодильник открылся, и тебя вылили в унитаз. Суп проиграл.")
    st.button("Попробовать снова", on_click=lambda: st.session_state.clear())
    st.stop()

# Выбор апгрейда
st.markdown("### 🧪 Новые возможности для супа:")

choices = game.get_upgrade_choices()

if not choices:
    st.warning("🤷 Всё уже исследовано. Нажми 'Следующий ход'.")
    if st.button("Следующий ход"):
        game.next_turn()
        st.rerun()
    st.stop()

selected_name = st.radio("Выбери улучшение:", [c["name"] for c in choices])

# Показ описания выбранного апгрейда
selected_upgrade = next(u for u in choices if u["name"] == selected_name)
st.markdown(f"🔍 **Описание:** {selected_upgrade['desc']}")

# Кнопка применения
if st.button("📈 Применить и перейти к следующему ходу"):
    game.apply_upgrade(selected_name)
    game.next_turn()
    st.rerun()
