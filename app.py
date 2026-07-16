import os
import json
import qrcode

import streamlit as st
from fpdf import FPDF
from datetime import datetime

# Inicializar carrito en session_state
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

if "total" not in st.session_state:
    st.session_state["total"] = 0

st.set_page_config(
    page_title="Tótem Restaurante",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Cafetería UPPE")

# ======================================
# MENÚ
# ======================================

menu = {
    "🥪 Tortas": [
        {"nombre": "Torta Cubana", "precio": 60},
        {"nombre": "Torta Jamón", "precio": 40},
        {"nombre": "Torta Milanesa", "precio": 50},
        {"nombre": "Torta Salchicha", "precio": 40},
        {"nombre": "Torta Bistec", "precio": 40},
        {"nombre": "Torta Pastor", "precio": 40},
    ],
    "🫓 Quesadillas": [
        {"nombre": "Quesadilla Harina", "precio": 22},
        {"nombre": "Quesadilla Dorada", "precio": 25},
        {"nombre": "Quesadilla Comal", "precio": 25},
        {"nombre": "Gordita Comal", "precio": 15},
        {"nombre": "Gordita Dorada", "precio": 15},
    ],
    "🥤 Bebidas": [
        {"nombre": "Coca Cola 600", "precio": 24},
        {"nombre": "Agua Natural 1L", "precio": 15},
        {"nombre": "Agua Mineral", "precio": 25},
        {"nombre": "Boing", "precio": 22},
        {"nombre": "Café", "precio": 28},
    ],
    "⭐ Especiales": [
        {"nombre": "Combo Familiar", "precio": 280},
        {"nombre": "Paquete Ejecutivo", "precio": 145},
        {"nombre": "Promoción del Día", "precio": 120},
    ]
}

# ======================================
# INTERFAZ POR PESTAÑAS
# ======================================

tabs = st.tabs(list(menu.keys()))

for tab, (categoria, productos) in zip(tabs, menu.items()):
    with tab:
        for fila in range(0, len(productos), 3):
            cols = st.columns(3)
            for col_idx in range(3):
                indice = fila + col_idx
                if indice < len(productos):
                    producto = productos[indice]
                    with cols[col_idx]:
                        st.markdown(
                            f"""
                            ### {producto['nombre']}
                            **${producto['precio']}**
                            """
                        )
                        st.number_input(
                            "Cantidad",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"cant_{producto['nombre']}"
                        )

# ======================================
# CARRITO AUTOMÁTICO (usando session_state)
# ======================================

carrito_tmp = []
for categoria, productos in menu.items():
    for producto in productos:
        cantidad = st.session_state.get(f"cant_{producto['nombre']}", 0)
        if cantidad > 0:
            carrito_tmp.append({
                "producto": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"]
            })

st.session_state["carrito"] = carrito_tmp

# -------------------------------
# Sección lateral: Mi Pedido
# -------------------------------

with st.sidebar:
    # Calcular total dinámicamente
    if len(st.session_state["carrito"]) == 0:
        st.session_state["total"] = 0
    else:
        st.session_state["total"] = sum(
            item["cantidad"] * item["precio"] for item in st.session_state["carrito"]
        )

    # Encabezado con costo a la derecha
    col1, col2 = st.columns([2,1])
    with col1:
        st.title("🛒 Mi Pedido")
    with col2:
        st.subheader(f"${st.session_state['total']:.2f}")

    # Botones principales
    col1b, col2b = st.columns(2)
    confirmar = col1b.button("✅ Hacer Pedido", use_container_width=True)
    vaciar = col2b.button("🗑️ Vaciar", use_container_width=True)

    # Acción al presionar Vaciar
    if vaciar:
        # Borra carrito y total
        st.session_state["carrito"] = []
        st.session_state["total"] = 0

        # Eliminar todas las claves de cantidades
        for categoria, productos in menu.items():
            for producto in productos:
                key = f"cant_{producto['nombre']}"
                if key in st.session_state:
                   del st.session_state[key]   # elimina la clave

        # Reinicia la app como si refrescaras la página
        st.experimental_rerun()

    st.info("Carrito y cantidades reiniciados.")


    # Acción al presionar Confirmar
    if confirmar and len(st.session_state["carrito"]) > 0:
        st.success("✅ Pedido generado correctamente. Pasa a caja con el ticket a realizar el pago.")

        # Generar PDF del ticket
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Ticket de Pedido", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Total: ${st.session_state['total']:.2f}", ln=True, align="C")
        pdf.ln(10)

        for item in st.session_state["carrito"]:
            subtotal = item["cantidad"] * item["precio"]
            pdf.cell(200, 10, txt=f"{item['cantidad']} x {item['producto']} - ${subtotal:.2f}", ln=True)

        pdf.output("ticket.pdf")

        # Botón de descarga que además vacía el carrito
        with open("ticket.pdf", "rb") as f:
            st.download_button(
                label="📄 Descargar Ticket en PDF",
                data=f,
                file_name="ticket.pdf",
                mime="application/pdf",
                on_click=lambda: st.session_state.update({"carrito": [], "total": 0})
            )

    st.divider()

    if len(st.session_state["carrito"]) == 0:
        st.write("No hay productos seleccionados.")
    else:
        for i, item in enumerate(st.session_state["carrito"]):
            subtotal = item["cantidad"] * item["precio"]
            st.markdown(f"### {item['cantidad']} x {item['producto']}")
            st.write(f"${subtotal:.2f}")

            # Observaciones por unidad
            item["observaciones"] = []
            for unidad in range(item["cantidad"]):
                with st.expander(f"⚙️ {item['producto']} #{unidad + 1}"):
                    observaciones_unidad = []
                    if st.checkbox("Sin chile", key=f"sin_chile_{i}_{unidad}"):
                        observaciones_unidad.append("Sin chile")
                    if st.checkbox("Sin jitomate", key=f"sin_jitomate_{i}_{unidad}"):
                        observaciones_unidad.append("Sin jitomate")
                    if st.checkbox("Extra queso", key=f"extra_queso_{i}_{unidad}"):
                        observaciones_unidad.append("Extra queso")
                    item["observaciones"].append(observaciones_unidad)

            st.divider()
