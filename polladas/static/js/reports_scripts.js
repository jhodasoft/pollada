function toggleDeliveryList() {
    var list = document.getElementById("delivery-list");
    var button = document.querySelector(".toggle-button");
    if (list.style.display === "none" || list.style.display === "") {
        list.style.display = "block";
        button.textContent = "Ocultar pedidos de Delivery";
    } else {
        list.style.display = "none";
        button.textContent = "Ver pedidos de Delivery pendientes";
    }
}