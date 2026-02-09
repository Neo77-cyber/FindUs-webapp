
document.getElementById('open-service-modal').addEventListener('click', function() {
    document.getElementById('service-modal-overlay').classList.add('active');
});
document.getElementById('close-service-modal').addEventListener('click', function() {
    document.getElementById('service-modal-overlay').classList.remove('active');
});
