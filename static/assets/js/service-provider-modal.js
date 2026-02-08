
function openServiceModal() {
    console.log('Opening modal...');
    const modal = document.getElementById('service-modal-overlay');
    const modalContent = document.getElementById('service-modal-content');
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Load form via HTMX
    htmx.ajax('GET', '/create-service/', {
        target: '#service-modal-content',
        swap: 'innerHTML'
    });
}

function closeServiceModal() {
    const modal = document.getElementById('service-modal-overlay');
    modal.classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('service-modal-content').innerHTML = '';
}

// Close button
document.getElementById('close-service-modal').addEventListener('click', closeServiceModal);

// Close when clicking outside modal
document.getElementById('service-modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        closeServiceModal();
    }
});
