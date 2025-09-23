document.addEventListener('DOMContentLoaded', (event) => {
    const tipoPedidoRadios = document.querySelectorAll('input[name="tipo_pedido"]');
    const deliveryFields = document.getElementById('delivery-fields');

    function toggleDeliveryFields() {
        // Asegura que hay un radio button seleccionado antes de proceder
        const selectedRadio = document.querySelector('input[name="tipo_pedido"]:checked');
        if (selectedRadio) {
            const selectedValue = selectedRadio.value;
            if (selectedValue === 'delivery') {
                deliveryFields.style.display = 'block';
            } else {
                deliveryFields.style.display = 'none';
            }
        }
    }

    // Agrega un evento 'change' a cada botón de radio
    tipoPedidoRadios.forEach(radio => {
        radio.addEventListener('change', toggleDeliveryFields);
    });

    // Llama a la función al cargar la página para establecer el estado inicial
    toggleDeliveryFields();
});