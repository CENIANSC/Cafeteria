import streamlit as st

st.set_page_config(
    page_title="Tótem de Autoservicio",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Tótem de Autoservicio")

# Menú del restaurante
menu = {
    "Tortas": [
        {"nombre": "Torta Cubana", "precio": 95},
        {"nombre": "Torta de Jamón", "precio": 65},
        {"nombre": "Torta Hawaiana", "precio": 85},
        {"nombre": "Torta Especial", "precio": 110}
    ],
    "Quesadillas": [
        {"nombre": "Quesadilla de Queso", "precio": 35},
        {"nombre": "Quesadilla de Chorizo", "precio": 45},
        {"nombre": "Quesadilla de Champiñones", "precio": 40},
        {"nombre": "Quesadilla Mixta", "precio": 50}
    ],
    "Bebidas": [
        {"nombre": "Coca Cola", "precio": 25},
        {"nombre": "Agua Natural", "precio": 18},
        {"nombre": "Agua Mineral", "precio": 22},
        {"nombre": "Jugo", "precio": 30}
    ],
    "Especiales": [
        {"nombre": "Combo Familiar", "precio": 280},
        {"nombre": "Paquete Ejecutivo", "precio": 145},
        {"nombre": "Promoción del Día", "precio": 120}
    ]
}

pedido = []
total = 0

# Mostrar categorías y productos
for categoria, productos in menu.items():

    st.header(categoria)

    for producto in productos:

        col1, col2, col3 = st.columns([5, 2, 2])

        with col1:
            seleccionado = st.checkbox(
                f"{producto['nombre']} - ${producto['precio']}",
                key=f"check_{producto['nombre']}"
            )

        with col2:
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                step=1,
                key=f"cant_{producto['nombre']}"
            )

        with col3:
            subtotal = cantidad * producto["precio"]
            st.write("")
            st.write(f"Subtotal: ${subtotal}")

        if seleccionado:
            pedido.append({
                "producto": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"],
                "subtotal": subtotal
            })

            total += subtotal

    st.divider()

# Generar comanda
if st.button("🧾 Generar Comanda"):

    if len(pedido) == 0:
        st.warning("Seleccione al menos un producto.")
    else:

        st.subheader("Comanda")

        for item in pedido:
            st.write(
                f"{item['cantidad']} x {item['producto']} "
                f"(${item['precio']}) = ${item['subtotal']}"
            )

        st.divider()

        st.metric(
            label="TOTAL A PAGAR",
            value=f"${total}"
        )

        st.success("Pedido generado correctamente.")
