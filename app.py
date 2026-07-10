import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(
    page_title="Tótem de Autoservicio",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Tótem de Autoservicio")
st.subheader("Seleccione sus productos")

# ==========================
# MENÚ
# ==========================
menu = {
    "🥪 Tortas": [
        {"nombre": "Torta Cubana", "precio": 95},
        {"nombre": "Torta de Jamón", "precio": 65},
        {"nombre": "Torta Hawaiana", "precio": 85},
        {"nombre": "Torta Especial", "precio": 110}
    ],

    "🫓 Quesadillas": [
        {"nombre": "Quesadilla de Queso", "precio": 35},
        {"nombre": "Quesadilla de Chorizo", "precio": 45},
        {"nombre": "Quesadilla de Champiñones", "precio": 40},
        {"nombre": "Quesadilla Mixta", "precio": 50}
    ],

    "🥤 Bebidas": [
        {"nombre": "Coca Cola", "precio": 25},
        {"nombre": "Agua Natural", "precio": 18},
        {"nombre": "Agua Mineral", "precio": 22},
        {"nombre": "Jugo", "precio": 30}
    ],

    "⭐ Especiales": [
        {"nombre": "Combo Familiar", "precio": 280},
        {"nombre": "Paquete Ejecutivo", "precio": 145},
        {"nombre": "Promoción del Día", "precio": 120}
    ]
}

pedido = []
total = 0

# ==========================
# INTERFAZ DEL TÓTEM
# ==========================
for categoria, productos in menu.items():

    st.header(categoria)

    for producto in productos:

        col1, col2 = st.columns([5, 1])

        with col1:
            seleccionado = st.checkbox(
                f"{producto['nombre']}   -   ${producto['precio']}",
                key=f"check_{producto['nombre']}"
            )

        with col2:
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                step=1,
                key=f"cantidad_{producto['nombre']}",
                label_visibility="collapsed"
            )

        observaciones = ""

        if seleccionado:

            observaciones = st.text_input(
                "Observaciones",
                placeholder="Ejemplo: sin cebolla, extra queso...",
                key=f"obs_{producto['nombre']}"
            )

            importe = cantidad * producto["precio"]

            pedido.append({
                "producto": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"],
                "observaciones": observaciones,
                "importe": importe
            })

            total += importe

    st.divider()

# ==========================
# RESUMEN
# ==========================
if len(pedido) > 0:

    st.subheader("🛒 Resumen del pedido")

    for item in pedido:
        st.write(
            f"{item['cantidad']} x {item['producto']} "
            f"- ${item['importe']}"
        )

    st.metric(
        "Total a pagar",
        f"${total}"
    )

# ==========================
# GENERAR COMANDA
# ==========================
if st.button("🧾 Generar Comanda"):

    if len(pedido) == 0:
        st.warning("Seleccione al menos un producto.")

    else:

        fecha = datetime.now()

        # --------------------------
        # PDF
        # --------------------------
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "COMANDA", ln=True, align="C")

        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0,
            8,
            fecha.strftime("%d/%m/%Y %H:%M"),
            ln=True,
            align="C"
        )

        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Pedido:", ln=True)

        pdf.set_font("Arial", "", 11)

        for item in pedido:

            pdf.cell(
                0,
                8,
                f"{item['cantidad']} x {item['producto']}",
                ln=True
            )

            if item["observaciones"].strip() != "":
                pdf.set_font("Arial", "I", 10)
                pdf.cell(
                    0,
                    6,
                    f"   Obs: {item['observaciones']}",
                    ln=True
                )
                pdf.set_font("Arial", "", 11)

        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            0,
            8,
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

        # Convertir a bytes para descarga
        pdf_bytes = bytes(pdf.output())

        st.success("Comanda generada correctamente.")

        st.download_button(
            label="📄 Descargar Comanda PDF",
            data=pdf_bytes,
            file_name=f"Comanda_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
