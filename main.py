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

st.title("🥣 Суполюция")
st.markdown("Разумный суп. Микроцивилизация. Научный бой за выживание.")

# 💬 Объяснение ресурсов
st.markdown("""
**📚 Ресурсы:**
- 🧬 **Белки** — рост, восстановление
- 🧈 **Жиры** — броня, стабильность температуры
- 🍞 **Углеводы** — энергия. Каждый ход тратятся
- 🪨 **Минералы** — дипломатия, апгрейды, технологии
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🧪 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Здоровье:** `{state['hp']}`")
with col2:
    for k, v in state["resources"].items():
        st.markdown(f"- {k.capitalize()}: `{v}`")

# 📣 Кризис
if state.get("active_crisis"):
    st.warning(f"⚠️ Кризис: {state['active_crisis']} требует 3 минерала.")
    colc1, colc2 = st.columns(2)
    if colc1.button("🤝 Подчиниться"):
        game.resolve_crisis(True)
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if colc2.button("🚫 Отказаться"):
        game.resolve_crisis(False)
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 🔬 Технологии
st.markdown("### 🔬 Исследования:")
choices = game.get_upgrade_choices()
if not choices:
    st.info("Все технологии изучены.")
    if st.button("➡ Следующий ход"):
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
else:
    for tech in choices:
        with st.expander(f"🔹 {tech['name']}"):
            st.markdown(tech["desc"])
            deps = game.tech_tree.get(tech["name"], [])
            if deps:
                st.markdown(f"🔗 Требует: {', '.join(deps)}")
            st.markdown("🧠 Возможные последствия: фракции, квесты, сюжет")
            if st.button(f"🔬 Изучить: {tech['name']}"):
                game.apply_upgrade(tech["name"])
                game.trigger_tech_effects(tech["name"])
                game.next_turn()
                st.session_state.game_data = game.to_dict()
                st.rerun()

# 🏛️ Фракции
st.markdown("### 🏛️ Фракции:")
for name, rep in state["factions"].items():
    if rep >= 6:
        status = "👑 альянс"
    elif rep >= 4:
        status = "🟢 союз"
    elif rep <= -4:
        status = "🔴 враг"
    else:
        status = "⚪ нейтрал"
    st.markdown(f"{status} **{name}** — `{rep}`")

# 📜 События
st.markdown("### 📜 Хроника:")
for log in reversed(state["events_log"]):
    icon = "🔬" if "техн" in log.lower() else "⚔️" if "атак" in log.lower() else "🎁" if "помощ" in log.lower() else "📍"
    st.markdown(f"- {icon} {log}")

# ⚖️ Выбор
if state.get("current_choice"):
    ch = state["current_choice"]
    st.markdown(f"### ❓ {ch['text']}")
    cola, colb = st.columns(2)
    if cola.button("✅ Да"):
        game.resolve_choice("yes")
        game.choice_impact(ch["id"], "yes")
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if colb.button("❌ Нет"):
        game.resolve_choice("no")
        game.choice_impact(ch["id"], "no")
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 🏗️ Постройки
with st.expander("🏗️ Постройки"):
    for s in state["structures"]:
        st.markdown(f"- 🧱 {s}")
    if not state["structures"]:
        st.markdown("_Ничего не построено._")

# 📘 Технологии
with st.expander("📘 Изученные технологии"):
    for t in state["tech"]:
        st.markdown(f"- {t}")
    if not state["tech"]:
        st.markdown("_Пока пусто._")
