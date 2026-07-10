import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(
    page_title="Tótem Restaurante",
    page_icon="🍽️",
    layout="wide"
)

# -----------------------------
# Carrito persistente
# -----------------------------
if "carrito" not in st.session_state:
    st.session_state.carrito = []

# -----------------------------
# Menú
# -----------------------------
menu = {
    "🥪 Tortas": [
        {"nombre": "Torta Cubana", "precio": 95},
        {"nombre": "Torta Jamón", "precio": 65},
        {"nombre": "Torta Hawaiana", "precio": 85},
        {"nombre": "Torta Especial", "precio": 110}
    ],

    "🫓 Quesadillas": [
        {"nombre": "Quesadilla de Queso", "precio": 35},
        {"nombre": "Quesadilla de Chorizo", "precio": 45},
        {"nombre": "Quesadilla Mixta", "precio": 55}
    ],

    "🥤 Bebidas": [
        {"nombre": "Coca Cola", "precio": 25},
        {"nombre": "Agua Natural", "precio": 18},
        {"nombre": "Agua Mineral", "precio": 22},
        {"nombre": "Jugo", "precio": 30}
    ],

    "⭐ Especiales": [
        {"nombre": "Combo Familiar", "precio": 280},
        {"nombre": "Paquete Ejecutivo", "precio": 145}
    ]
}

st.title("🍽️ Cafetería UPPE")

# -----------------------------
# Pestañas
# -----------------------------
tabs = st.tabs(list(menu.keys()))

for tab, (categoria, productos) in zip(tabs, menu.items()):

    with tab:

        st.subheader(categoria)

        for producto in productos:

            st.markdown(f"### {producto['nombre']}")
            st.write(f"Precio: **${producto['precio']}**")

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                step=1,
                key=f"cantidad_{producto['nombre']}"
            )

            st.write("Personalización")

            col1, col2, col3 = st.columns(3)

            with col1:
                sin_chile = st.checkbox(
                    "Sin chile",
                    key=f"chile_{producto['nombre']}"
                )

            with col2:
                sin_jitomate = st.checkbox(
                    "Sin jitomate",
                    key=f"jitomate_{producto['nombre']}"
                )

            with col3:
                extra_queso = st.checkbox(
                    "Extra queso",
                    key=f"queso_{producto['nombre']}"
                )

            if st.button(
                f"Agregar {producto['nombre']}",
                key=f"agregar_{producto['nombre']}"
            ):

                observaciones = []

                if sin_chile:
                    observaciones.append("Sin chile")

                if sin_jitomate:
                    observaciones.append("Sin jitomate")

                if extra_queso:
                    observaciones.append("Extra queso")

                st.session_state.carrito.append({
                    "producto": producto["nombre"],
                    "cantidad": cantidad,
                    "precio": producto["precio"],
                    "observaciones": observaciones
                })

                st.success(
                    f"{producto['nombre']} agregado al carrito."
                )

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🛒 Mi Pedido")

total = 0

if len(st.session_state.carrito) == 0:
    st.sidebar.write("El carrito está vacío.")

else:

    for idx, item in enumerate(st.session_state.carrito):

        subtotal = item["cantidad"] * item["precio"]
        total += subtotal

        st.sidebar.write(
            f"**{item['cantidad']} x {item['producto']}**"
        )

        st.sidebar.write(
            f"${subtotal}"
        )

        if len(item["observaciones"]) > 0:
            st.sidebar.caption(
                ", ".join(item["observaciones"])
            )

        if st.sidebar.button(
            "Eliminar",
            key=f"eliminar_{idx}"
        ):
            st.session_state.carrito.pop(idx)
            st.rerun()

        st.sidebar.divider()

    st.sidebar.metric(
        "TOTAL",
        f"${total}"
    )

# -----------------------------
# Generar comanda
# -----------------------------
if st.sidebar.button("🧾 Confirmar Pedido"):

    if len(st.session_state.carrito) == 0:
        st.sidebar.warning(
            "No hay productos en el carrito."
        )

    else:

        fecha = datetime.now()

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(
            0,
            10,
            "COMANDA",
            ln=True,
            align="C"
        )

        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0,
            8,
            fecha.strftime("%d/%m/%Y %H:%M"),
            ln=True,
            align="C"
        )

        pdf.ln(10)

        pdf.set_font("Arial", "", 12)

        for item in st.session_state.carrito:

            pdf.cell(
                0,
                8,
                f"{item['cantidad']} x {item['producto']}",
                ln=True
            )

            if len(item["observaciones"]) > 0:

                pdf.set_font("Arial", "I", 10)

                pdf.cell(
                    0,
                    6,
                    "   " + ", ".join(item["observaciones"]),
                    ln=True
                )

                pdf.set_font("Arial", "", 12)

        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            0,
            10,
            f"TOTAL: ${total}",
            ln=True
        )

        pdf.ln(10)

        pdf.set_font("Arial", "I", 10)
        pdf.cell(
            0,
            8,
            "Gracias por su preferencia",
            ln=True,
            align="C"
        )

        pdf_bytes = bytes(pdf.output())

        st.sidebar.download_button(
            "📄 Descargar Comanda",
            pdf_bytes,
            file_name=f"comanda_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

# -----------------------------
# Vaciar carrito
# -----------------------------
if len(st.session_state.carrito) > 0:

    if st.sidebar.button("🗑️ Vaciar carrito"):
        st.session_state.carrito = []
        st.rerun()
