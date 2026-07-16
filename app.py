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


# -------------------------------
# Sección lateral: Mi Pedido
# -------------------------------
# Calcular total antes de mostrar
total = sum(item["cantidad"] * item["precio"] for item in carrito)

# Encabezado con costo a la derecha
with st.sidebar:
    col1, col2 = st.columns([2,1])
    with col1:
        st.title("🛒 Mi Pedido")
    with col2:
        st.subheader(f"${total:.2f}")

    # Botones arriba
    col1b, col2b = st.columns(2)
    confirmar = col1b.button("🧾 Confirmar", use_container_width=True)
    vaciar = col2b.button("🗑️ Vaciar", use_container_width=True)

    st.divider()

    if len(carrito) == 0:
        st.write("No hay productos seleccionados.")
    else:
        for i, item in enumerate(carrito):
            subtotal = item["cantidad"] * item["precio"]

            st.markdown(f"### {item['cantidad']} x {item['producto']}")
            st.write(f"${subtotal:.2f}")

            # -------------------------------
            # Personalización por unidad
            # -------------------------------
            item["observaciones"] = []
            for unidad in range(item["cantidad"]):
                with st.expander(f"⚙️ {item['producto']} #{unidad + 1}"):
                    observaciones_unidad = []

                    sin_chile = st.checkbox(
                        "Sin chile", key=f"sin_chile_{i}_{unidad}"
                    )
                    sin_jitomate = st.checkbox(
                        "Sin jitomate", key=f"sin_jitomate_{i}_{unidad}"
                    )
                    extra_queso = st.checkbox(
                        "Extra queso", key=f"extra_queso_{i}_{unidad}"
                    )

                    if sin_chile:
                        observaciones_unidad.append("Sin chile")
                    if sin_jitomate:
                        observaciones_unidad.append("Sin jitomate")
                    if extra_queso:
                        observaciones_unidad.append("Extra queso")

                    item["observaciones"].append(observaciones_unidad)

            st.divider()

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

        pdf_bytes = bytes(pdf.output(dest="S"))

        st.sidebar.success(
        f"Pedido #{numero_pedido} generado correctamente."
        )

        st.sidebar.download_button(
        label=f"📄 Descargar Pedido #{numero_pedido}",
        data=pdf_bytes,
        file_name=f"pedido_{numero_pedido}.pdf",
        mime="application/pdf",
        use_container_width=True
        )

        # =====================================
        # LIMPIAR PANTALLA
        # =====================================

        # eliminar qr temporal
        if os.path.exists(qr_path):
           os.remove(qr_path)

        st.sidebar.info(
           "Descargue el PDF y posteriormente presione 'Vaciar'."
        )

