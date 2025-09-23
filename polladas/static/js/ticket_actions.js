document.addEventListener('DOMContentLoaded', function() {

    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const ticketContainer = document.querySelector('.ticket-container');
            const actionsContainer = document.querySelector('.actions');

            // Obtiene el nombre del cliente del atributo de datos
            const clientName = downloadBtn.getAttribute('data-client-name');
            
            // Reemplaza los espacios y caracteres especiales con guiones bajos
            const normalizedName = clientName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
            
            // Crea el nombre del archivo final
            const fileName = `ticket_parrillada_${normalizedName}.png`;

            // Oculta los botones temporalmente
            actionsContainer.style.display = 'none';

            html2canvas(ticketContainer, { scale: 2 }).then(canvas => {
                const link = document.createElement('a');
                link.download = fileName;
                link.href = canvas.toDataURL('image/png');
                link.click();

                // Vuelve a mostrar los botones
                actionsContainer.style.display = 'flex';
            });
        });
    }

    // Funcionalidad del botón "Pedir otro Ticket"
    const newTicketBtn = document.getElementById('new-ticket-btn');
    if (newTicketBtn) {
        newTicketBtn.addEventListener('click', function() {
            window.location.href = this.getAttribute('data-url');
        });
    }

});