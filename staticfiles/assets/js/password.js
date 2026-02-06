// Password toggle functionality
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
      const input = this.parentElement.querySelector('input');
      const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
      input.setAttribute('type', type);
      
      // Toggle icon
      const svg = this.querySelector('svg');
      if (type === 'text') {
        svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
      } else {
        svg.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
      }
    });
  });

  // License field toggle
  function toggleLicenseField() {
    const licenseCheckbox = document.getElementById('has_license');
    const licenseField = document.getElementById('license-field');
    
    if (licenseCheckbox.checked) {
      licenseField.style.display = 'block';
    } else {
      licenseField.style.display = 'none';
      // Clear the license number field when unchecked
      document.getElementById('provider-license').value = '';
    }
  }

  // Form submission handler with spinner
  document.getElementById('craftsman-form').addEventListener('submit', function(e) {
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner-container');
    
    // Show spinner, hide button text
    btnText.style.display = 'none';
    spinner.style.display = 'flex';
    
    // Disable the button to prevent multiple submissions
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';
    submitBtn.style.cursor = 'wait';
  });

  // Initialize license field on page load
  document.addEventListener('DOMContentLoaded', function() {
    toggleLicenseField();
  });