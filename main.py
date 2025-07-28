import streamlit as st
from soup_game import SoupGame

st.set_page_config(page_title="🥣 Supolution", layout="centered")
st.title("🥣 Supolution — Эволюция Супа")

if "game" not in st.session_state:
    st.session_state.game = SoupGame()

game = st.session_state.game

st.markdown(f"**Ход:** {game.turn} / {game.max_turns}")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Ресурсы")
    for k, v in game.resources.items():
        max_v = game.resource_max.get(k, 1000)
        st.text(f"{k}: {v} / {max_v}")
with col2:
    st.subheader("Фракции")
    for k, v in game.factions.items():
        st.text(f"{k}: {v}")

st.markdown("---")
st.subheader("Выбор технологии")
choices = game.get_upgrade_choices()

for tech in choices:
    st.markdown(f"### 🔬 {tech['name']}")
    st.markdown(tech["desc"])
    if tech.get("cost"):
        st.markdown("💰 Цена:")
        cost_parts = []
        for c in tech["cost"]:
            if c["type"] == "faction":
                cost_parts.append(f"{c['amount']} к фракции '{c['target']}'")
            else:
                cost_parts.append(f"{c['amount']} {c['type']}")
        st.markdown(", ".join(cost_parts))
    if game.can_afford(tech["name"]):
        if st.button(f"Изучить: {tech['name']}"):
            game.apply_upgrade(tech["name"])
            game.check_synergies()
            st.rerun()
    else:
        st.markdown("❌ Недостаточно ресурсов или лояльности")

st.markdown("---")

if st.button("Следующий ход"):
    game.next_turn()
    st.rerun()

st.subheader("🕘 События")
for e in reversed(game.events_log[-8:]):
    st.markdown(e)
