function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

function showPasswordModal() {
    document.getElementById('passwordModal').style.display = 'flex';
    // Reset form
    document.getElementById('passwordForm').reset();
    // Set all back to password type
    document.getElementById('currentPassword').type = 'password';
    document.getElementById('newPassword').type = 'password';
    document.getElementById('confirmPassword').type = 'password';
}

function closePasswordModal() {
    document.getElementById('passwordModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('passwordModal');
    if (event.target == modal) {
        closePasswordModal();
    }

}