# ✅ main.py — адаптирован под переработанное ядро с физикой, фракциями и ресурсами

import streamlit as st
from soup_game import SoupGame

st.set_page_config(page_title="🥣 Суполюция", page_icon="🥄", layout="centered")

if "game_data" in st.session_state:
    game = SoupGame()
    game.load_state(st.session_state["game_data"])
else:
    game = SoupGame()

state = game.get_state()
st.session_state.game_data = game.to_dict()

# 🧠 Заголовок
st.title("🥣 Суполюция")
st.markdown("Разумный суп. Реальная стратегия. Не дай себе выкипеть.")

# 💬 Объяснение ресурсов (по физике и биологии)
st.markdown("""
**📚 Ресурсы:**
- 🧬 **Белки** — строят ткани и восстанавливают HP
- 🧈 **Жиры** — защита и тепло. Без них перегрев/замерзание
- 🍞 **Углеводы** — энергия. Если не хватает — HP уходит
- 🪨 **Минералы** — катализаторы. Нужны для технологий и дипломатии
""")

# 📦 Статистика
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🧪 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Здоровье:** `{state['hp']}`")
with col2:
    for res, val in state["resources"].items():
        st.markdown(f"- {res.capitalize()}: `{val}`")

# 🔬 Технологии (с зависимостями)
st.markdown("### 🧪 Исследования:")
choices = game.get_upgrade_choices()
tech_tree = game.tech_tree

if not choices:
    st.info("Все технологии изучены. Жми ➡ Следующий ход.")
    if st.button("➡ Следующий ход"):
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
else:
    for tech in choices:
        deps = tech_tree.get(tech["name"], [])
        with st.expander(f"🔹 {tech['name']}"):
            st.markdown(f"{tech['desc']}")
            if deps:
                st.markdown(f"🔗 Требует: {', '.join(deps)}")
            if st.button(f"🔬 Изучить: {tech['name']}"):
                game.apply_upgrade(tech['name'])
                game.next_turn()
                st.session_state.game_data = game.to_dict()
                st.rerun()

# 🏛️ Фракции
st.markdown("### 🏛️ Фракции:")
for name, rep in state["factions"].items():
    status = "🟢 союз" if rep >= 4 else "🔴 враг" if rep <= -3 else "⚪ нейтрал"
    st.markdown(f"{status} **{name}** — `{rep}`")

# 🧾 События и логи
st.markdown("### 📜 Хроника:")
for log in reversed(state["events_log"]):
    st.markdown(f"- {log}")

# ⚖️ Выборы игрока
if state.get("current_choice"):
    ch = state["current_choice"]
    st.markdown(f"### ❓ {ch['text']}")
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Согласен"):
        game.resolve_choice("yes")
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if col_b.button("❌ Отказаться"):
        game.resolve_choice("no")
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 🏗️ Прогресс
with st.expander("📦 Постройки"):
    for s in state["structures"]:
        st.markdown(f"- 🧱 {s}")
    if not state["structures"]:
        st.markdown("_Ничего не построено._")

with st.expander("📘 Изученные технологии"):
    for t in state["tech"]:
        st.markdown(f"- {t}")
    if not state["tech"]:
        st.markdown("_Нет исследований._")
