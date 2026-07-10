# ======================================
# SIDEBAR
# ======================================

st.sidebar.title("🛒 Mi Pedido")

# Botones en la parte superior
col1, col2 = st.sidebar.columns(2)

confirmar = col1.button(
    "🧾 Confirmar Pedido",
    use_container_width=True
)

vaciar = col2.button(
    "🗑️ Vaciar Pedido",
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

        st.sidebar.write(f"${subtotal}")

        st.sidebar.write("Personalización")

        sin_chile = st.sidebar.checkbox(
            "Sin chile",
            key=f"sin_chile_{i}"
        )

        sin_jitomate = st.sidebar.checkbox(
            "Sin jitomate",
            key=f"sin_jitomate_{i}"
        )

        extra_queso = st.sidebar.checkbox(
            "Extra queso",
            key=f"extra_queso_{i}"
        )

        item["observaciones"] = []

        if sin_chile:
            item["observaciones"].append("Sin chile")

        if sin_jitomate:
            item["observaciones"].append("Sin jitomate")

        if extra_queso:
            item["observaciones"].append("Extra queso")

        st.sidebar.divider()

    st.sidebar.metric(
        "TOTAL",
        f"${total}"
    )

# ======================================
# CONFIRMAR PEDIDO
# ======================================

if confirmar:

    if len(carrito) == 0:

        st.sidebar.warning(
            "Seleccione al menos un producto."
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

                pdf.set_font("Arial", "I", 10)

                pdf.cell(
                    0,
                    6,
                    f"   - {obs}",
                    new_x="LMARGIN",
                    new_y="NEXT"
                )

                pdf.set_font("Arial", "", 12)

        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)

        pdf.cell(
            0,
            10,
            f"TOTAL: ${total}",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        pdf.ln(5)

        pdf.set_font("Arial", "I", 10)

        pdf.cell(
            0,
            8,
            "Gracias por su preferencia",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C"
        )

        pdf_bytes = bytes(pdf.output())

        st.sidebar.success(
            "Pedido confirmado correctamente."
        )

        st.sidebar.download_button(
            label="📄 Descargar Comanda",
            data=pdf_bytes,
            file_name=f"comanda_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ======================================
# VACIAR PEDIDO
# ======================================

if vaciar:

    for categoria, productos in menu.items():

        for producto in productos:

            st.session_state[
                f"cant_{producto['nombre']}"
            ] = 0

    st.rerun()
