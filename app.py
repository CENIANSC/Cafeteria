import os
import json
import qrcode

import streamlit as st
from fpdf import FPDF
from datetime import datetime

# ======================================
# MENÚ DE PRODUCTOS CON EMOJIS
# ======================================
menu = {
    "🍔 Tortas": [
        {"nombre": "Torta Cubana", "precio": 50},
        {"nombre": "Torta de Jamón", "precio": 35},
        {"nombre": "Torta de Milanesa", "precio": 40},
        {"nombre": "Torta de Pierna", "precio": 45},
    ],
    "🥤 Bebidas": [
        {"nombre": "Coca Cola 600ml", "precio": 20},
        {"nombre": "Agua 500ml", "precio": 15},
        {"nombre": "Jugo de Naranja", "precio": 25},
        {"nombre": "Café Americano", "precio": 18},
    ],
    "🍪 Snacks": [
        {"nombre": "Papas Fritas", "precio": 22},
        {"nombre": "Galletas", "precio": 12},
        {"nombre": "Barra de Granola", "precio": 15},
    ]
}

# Inicializar variables en session_state
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []
if "total" not in st.session_state:
    st.session_state["total"] = 0

# ======================================
# SECCIÓN DE PRODUCTOS EN PESTAÑAS Y COLUMNAS
# ======================================
st.title("Cafetería UPPE")

tabs = st.tabs(list(menu.keys()))

for i, categoria in enumerate(menu.keys()):
    with tabs[i]:
        st.header(categoria)
        productos = menu[categoria]
        cols = st.columns(4)
        for idx, producto in enumerate(productos):
            with cols[idx % 4]:
                key_cant = f"cant_{producto['nombre']}"
                cantidad = st.number_input(
                    f"{producto['nombre']} (${producto['precio']})",
                    min_value=0,
                    step=1,
                    key=key_cant
                )

                # Personalización por cada unidad seleccionada
                for j in range(cantidad):
                    st.write(f"Personalización {j+1} de {producto['nombre']}")
                    sin_chile = st.checkbox("Sin chile", key=f"{producto['nombre']}_{j}_chile")
                    sin_jitomate = st.checkbox("Sin jitomate", key=f"{producto['nombre']}_{j}_jitomate")
                    sin_queso = st.checkbox("Sin queso", key=f"{producto['nombre']}_{j}_queso")

# ======================================
# CARRITO AUTOMÁTICO CON PERSONALIZACIONES
# ======================================
carrito_tmp = []
total_tmp = 0
for categoria, productos in menu.items():
    for producto in productos:
        cantidad = st.session_state.get(f"cant_{producto['nombre']}", 0)
        for j in range(cantidad):
            sin_chile = st.session_state.get(f"{producto['nombre']}_{j}_chile", False)
            sin_jitomate = st.session_state.get(f"{producto['nombre']}_{j}_jitomate", False)
            sin_queso = st.session_state.get(f"{producto['nombre']}_{j}_queso", False)

            item = {
                "producto": producto["nombre"],
                "precio": producto["precio"],
                "personalizacion": {
                    "sin_chile": sin_chile,
                    "sin_jitomate": sin_jitomate,
                    "sin_queso": sin_queso
                }
            }
            carrito_tmp.append(item)
            total_tmp += producto["precio"]

st.session_state["carrito"] = carrito_tmp
st.session_state["total"] = total_tmp

# ======================================
# BARRA LATERAL CON EMOJIS
# ======================================
st.sidebar.title("🛒 Carrito de compras")

if st.session_state["carrito"]:
    for item in st.session_state["carrito"]:
        extras = [k.replace("sin_", "sin ") for k,v in item["personalizacion"].items() if v]
        extras_txt = ", ".join(extras) if extras else "normal"
        st.sidebar.write(f"{item['producto']} ({extras_txt}) - ${item['precio']}")
    st.sidebar.write(f"**Total: ${st.session_state['total']}**")
else:
    st.sidebar.info("Carrito vacío")

# Botones
vaciar = st.sidebar.button("Vaciar carrito")
generar_pdf = st.sidebar.button("Generar PDF")

# ======================================
# Acción al presionar Vaciar
# ======================================
if vaciar:
    st.session_state["carrito"] = []
    st.session_state["total"] = 0
    for categoria, productos in menu.items():
        for producto in productos:
            st.session_state[f"cant_{producto['nombre']}"] = 0
            for j in range(10):  # máximo 10 unidades por producto
                for extra in ["chile","jitomate","queso"]:
                    k = f"{producto['nombre']}_{j}_{extra}"
                    if k in st.session_state:
                        st.session_state[k] = False
    st.experimental_rerun()

st.sidebar.info("Carrito y cantidades reiniciados.")

# ======================================
# Acción al presionar Generar PDF
# ======================================
if generar_pdf:
    if st.session_state["carrito"]:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Ticket Cafetería UPPE", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
        pdf.ln(10)

        for item in st.session_state["carrito"]:
            extras = [k.replace("sin_", "sin ") for k,v in item["personalizacion"].items() if v]
            extras_txt = ", ".join(extras) if extras else "normal"
            pdf.cell(200, 10, txt=f"{item['producto']} ({extras_txt}) - ${item['precio']}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, txt=f"TOTAL: ${st.session_state['total']}", ln=True)

        data = json.dumps(st.session_state["carrito"], ensure_ascii=False)
        qr = qrcode.make(data)
        qr_path = "qr_temp.png"
        qr.save(qr_path)
        pdf.image(qr_path, x=10, y=pdf.get_y() + 10, w=40)

        pdf_path = "ticket.pdf"
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            st.sidebar.download_button("Descargar PDF", f, file_name="ticket.pdf")

        os.remove(qr_path)
    else:
        st.warning("No hay productos en el carrito para generar PDF.")
