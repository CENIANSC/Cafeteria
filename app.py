pip install qrcode[pil]

import os
import json
import qrcode

import streamlit as st
from fpdf import FPDF
from datetime import datetime

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
        {"nombre": "Torta Cubana", "precio": 95},
        {"nombre": "Torta Jamón", "precio": 65},
        {"nombre": "Torta Hawaiana", "precio": 85},
        {"nombre": "Torta Especial", "precio": 110},
        {"nombre": "Torta Milanesa", "precio": 95},
        {"nombre": "Torta Pastor", "precio": 90},
    ],

    "🫓 Quesadillas": [
        {"nombre": "Quesadilla Queso", "precio": 35},
        {"nombre": "Quesadilla Chorizo", "precio": 45},
        {"nombre": "Quesadilla Champiñones", "precio": 40},
        {"nombre": "Quesadilla Mixta", "precio": 55},
        {"nombre": "Quesadilla Pastor", "precio": 50},
    ],

    "🥤 Bebidas": [
        {"nombre": "Coca Cola", "precio": 25},
        {"nombre": "Agua Natural", "precio": 18},
        {"nombre": "Agua Mineral", "precio": 22},
        {"nombre": "Jugo", "precio": 30},
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
# CARRITO AUTOMÁTICO
# ======================================

carrito = []

for categoria, productos in menu.items():

    for producto in productos:

        cantidad = st.session_state.get(
            f"cant_{producto['nombre']}",
            0
        )

        if cantidad > 0:

            carrito.append({
                "producto": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"]
            })

# ======================================
# SIDEBAR
# ======================================

st.sidebar.title("🛒 Mi Pedido")

# Botones arriba
col1, col2 = st.sidebar.columns(2)

confirmar = col1.button(
    "🧾 Confirmar",
    use_container_width=True
)

vaciar = col2.button(
    "🗑️ Vaciar",
    use_container_width=True
)

st.sidebar.divider()

total = 0

if len(carrito) == 0:

    st.sidebar.write("No hay productos seleccionados.")

else:

    for i, item in enumerate(carrito):

        subtotal = item["cantidad"] * item["precio"]
        total += subtotal

        st.sidebar.markdown(
            f"### {item['cantidad']} x {item['producto']}"
        )

        st.sidebar.write(
            f"${subtotal}"
        )


        # -------------------------------
        # Personalización desplegable
        # -------------------------------

        with st.sidebar.expander(
            "⚙️ Personalización"
        ):

            sin_chile = st.checkbox(
                "Sin chile",
                key=f"sin_chile_{i}"
            )

            sin_jitomate = st.checkbox(
                "Sin jitomate",
                key=f"sin_jitomate_{i}"
            )

            extra_queso = st.checkbox(
                "Extra queso",
                key=f"extra_queso_{i}"
            )

            item["observaciones"] = []

            if sin_chile:
                item["observaciones"].append(
                    "Sin chile"
                )

            if sin_jitomate:
                item["observaciones"].append(
                    "Sin jitomate"
                )

            if extra_queso:
                item["observaciones"].append(
                    "Extra queso"
                )


        st.sidebar.divider()


    st.sidebar.metric(
        "TOTAL",
        f"${total}"
    )

# ======================================
# GENERAR PEDIDO
# ======================================

if confirmar:

    if len(carrito) == 0:

        st.sidebar.warning(
            "Seleccione al menos un producto."
        )

    else:

        # =====================================
        # GENERAR NUMERO CONSECUTIVO DIARIO
        # =====================================

        fecha = datetime.now()
        fecha_actual = fecha.strftime("%Y-%m-%d")

        archivo_contador = "contador_pedidos.json"

        if os.path.exists(archivo_contador):

            with open(
                archivo_contador,
                "r",
                encoding="utf-8"
            ) as f:

                datos = json.load(f)

            if datos["fecha"] == fecha_actual:
                consecutivo = datos["contador"] + 1
            else:
                consecutivo = 1

        else:

            consecutivo = 1

        with open(
            archivo_contador,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "fecha": fecha_actual,
                    "contador": consecutivo
                },
                f
            )

        numero_pedido = f"{consecutivo:03d}"

        # =====================================
        # GENERAR QR
        # =====================================

        qr = qrcode.make(
            f"PEDIDO-{numero_pedido}"
        )

        qr_path = f"qr_{numero_pedido}.png"

        qr.save(qr_path)

        # =====================================
        # CREAR PDF
        # =====================================

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 18)

        pdf.cell(
            0,
            10,
            f"PEDIDO #{numero_pedido}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C"
        )

        pdf.set_font("Arial", "", 10)

        pdf.cell(
            0,
            8,
            fecha.strftime("%d/%m/%Y %H:%M"),
            new_x="LMARGIN",
            new_y="NEXT",
            align="C"
        )

        pdf.ln(5)

        pdf.set_font("Arial", "", 12)

        for item in carrito:

            pdf.cell(
                0,
                8,
                f"{item['cantidad']} x {item['producto']}",
                new_x="LMARGIN",
                new_y="NEXT"
            )

            for obs in item["observaciones"]:

                pdf.set_font(
                    "Arial",
                    "I",
                    10
                )

                pdf.cell(
                    0,
                    6,
                    f"   - {obs}",
                    new_x="LMARGIN",
                    new_y="NEXT"
                )

                pdf.set_font(
                    "Arial",
                    "",
                    12
                )

        pdf.ln(5)

        pdf.set_font(
            "Arial",
            "B",
            14
        )

        pdf.cell(
            0,
            10,
            f"TOTAL: ${total}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C"
        )

        pdf.ln(4)

        pdf.set_font(
            "Arial",
            "B",
            12
        )

        pdf.cell(
            0,
            10,
            "REALIZAR PAGO EN CAJA",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C"
        )

        pdf.ln(5)

        pdf.image(
            qr_path,
            x=80,
            w=50
        )

        pdf.ln(55)

        pdf.set_font(
            "Arial",
            "",
            10
        )

        pdf.cell(
            0,
            8,
            f"Codigo QR del pedido #{numero_pedido}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C"
        )

        pdf_bytes = pdf.output(
            dest="S"
        ).encode("latin1")

        nombre_pdf = (
            f"pedido_{numero_pedido}.pdf"
        )

        st.sidebar.download_button(
            label="📄 Descargar Pedido",
            data=pdf_bytes,
            file_name=nombre_pdf,
            mime="application/pdf"
        )

        # =====================================
        # LIMPIAR PANTALLA
        # =====================================

        claves_eliminar = []

        for clave in st.session_state.keys():

            if (
                clave.startswith("cant_")
                or clave.startswith("sin_chile_")
                or clave.startswith("sin_jitomate_")
                or clave.startswith("extra_queso_")
            ):

                claves_eliminar.append(
                    clave
                )

        for clave in claves_eliminar:
            del st.session_state[clave]

        # eliminar qr temporal
        if os.path.exists(qr_path):
            os.remove(qr_path)

        st.success(
            f"Pedido #{numero_pedido} registrado correctamente."
        )

        st.rerun()

# ======================================
# LIMPIAR PEDIDO
# ======================================

if vaciar:

    claves_eliminar = []

    for clave in st.session_state.keys():

        if clave.startswith("cant_"):
            claves_eliminar.append(clave)

        if clave.startswith("sin_chile_"):
            claves_eliminar.append(clave)

        if clave.startswith("sin_jitomate_"):
            claves_eliminar.append(clave)

        if clave.startswith("extra_queso_"):
            claves_eliminar.append(clave)

    for clave in claves_eliminar:
        del st.session_state[clave]

    st.rerun()
