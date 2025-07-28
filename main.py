# ✅ main.py — визуальные связи с логикой ресурсов и фракций

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
st.markdown("Развивай свой суп — строй, дружи и не выливайся!")

# 💬 Объяснение ресурсов
st.markdown("""
**🧪 Ресурсы:**
- 🍞 *Углеводы* — энергия. Если их мало, теряешь здоровье каждый ход.
- 🧈 *Жиры* — броня. Без них шанс сгореть!
- 🧬 *Белки* — восстановление и строительство. Полезны во всём.
""")

# 📦 Ресурсы и ХП
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🧪 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Жизнь супа:** `{state['hp']}`")
with col2:
    for k, v in state["resources"].items():
        st.markdown(f"- {k.capitalize()}: `{v}`")

# 🔥 Фракции
st.markdown("### 🏛️ Фракции")
for name, value in state["factions"].items():
    icon = "🟢" if value >= 4 else "⚪" if value >= 0 else "🔴"
    st.markdown(f"{icon} **{name}**: `{value}`")

# 📘 Технологии
st.markdown("### 🔬 Доступные технологии")
choices = game.get_upgrade_choices()
tech_tree = game.tech_tree

if not choices:
    st.warning("Все технологии изучены. Жми 'Следующий ход'.")
    if st.button("➡ Следующий ход"):
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
else:
    for tech in choices:
        deps = tech_tree.get(tech["name"], [])
        with st.expander(f"🧪 {tech['name']}"):
            st.markdown(tech["desc"])
            if deps:
                st.markdown(f"🔗 Нужно сначала: {', '.join(deps)}")
            if st.button(f"🚀 Изучить — {tech['name']}"):
                game.apply_upgrade(tech["name"])
                game.next_turn()
                st.session_state.game_data = game.to_dict()
                st.rerun()

# 📜 История и выборы
st.markdown("### 📖 Хроника")
for e in reversed(state["events_log"]):
    st.markdown(f"- {e}")

if state.get("current_choice"):
    c = state["current_choice"]
    st.markdown(f"### ❓ {c['text']}")
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Да"):
        game.resolve_choice("yes")
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if col_b.button("❌ Нет"):
        game.resolve_choice("no")
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 📦 Структуры и достижения
with st.expander("📦 Что построено"):
    if state["structures"]:
        for s in state["structures"]:
            st.markdown(f"- 🏗️ {s}")
    else:
        st.markdown("_Ничего пока не построено._")

with st.expander("📚 Технологии изучены"):
    if state["tech"]:
        for t in state["tech"]:
            st.markdown(f"- {t}")
    else:
        st.markdown("_Пока ни одной._")
