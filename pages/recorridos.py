
import streamlit as st
import scr.models.BST as BST
tree = st.session_state.arbol
st.title("Recorridos del árbol", text_alignment="center")
st.sidebar.success("En esta sección se pueden reliazar los distintos tipos de recorridos, orden/preorden/postorden/anchura")
traversal_columns = st.columns(4)
traversals = (
    ("Preorden", tree.pre_order()),
    ("Inorden", tree.in_order()),
    ("Postorden", tree.post_order()),
    ("Por niveles", tree.breadth_first()),
)
for column, (title, traversal) in zip(traversal_columns, traversals):
    with column:
        identifiers = [f"{event.get_id():06d} , " for event in (traversal or [])]
        st.write(f"**{title}**")
        st.code(" -> ".join(identifiers) if identifiers else "Arbol vacio")

col1,col2,col3,col4,col5=st.columns(5)
with col1:
    if st.button("preorden"):
        st.session_state.pre=tree.pre_order()
with col2:
    if st.button("inorden"):
        st.session_state.inor=tree.in_order()
with col3:
    if st.button("postorden"):
        st.session_state.post=tree.post_order()
with col4:
    if st.button("anchura"):
        st.session_state.anch=tree.breadth_first()
with col5:
    if st.button("por niveles"):
        st.session_state.