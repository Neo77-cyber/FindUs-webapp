const finalSubmitBtn = document.getElementById('final-submit-btn');
    if (finalSubmitBtn) {
        finalSubmitBtn.addEventListener('click', function() {
            this.innerHTML = 'Publishing...';
            // That's all! Button stays enabled so form submits
        });
    }

    // File upload preview
    document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    const label = this.nextElementSibling;
                    if (label && label.classList.contains('file-upload-label-compact')) {
                        const mainText = label.querySelector('.file-upload-main-compact');
                        const subText = label.querySelector('.file-upload-sub-compact');
                        
                        if (mainText) mainText.textContent = file.name;
                        if (subText) {
                            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                            subText.textContent = `${sizeMB} MB`;
                        }
                        
                        label.style.borderColor = 'var(--primary)';
                        label.style.background = 'var(--bg-secondary)';
                    }
                }
            });
        }
        
        // Pricing toggle - only if on step 2
        const hourlySection = document.getElementById('hourly-section');
        const fixedSection = document.getElementById('fixed-section');
        if (hourlySection && fixedSection) {
            const priceRadios = document.querySelectorAll('input[name*="price_type"]');
            priceRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    hourlySection.style.display = this.value === 'hourly' ? 'block' : 'none';
                    fixedSection.style.display = this.value === 'fixed' ? 'block' : 'none';
                });
                
                if (radio.checked) {
                    hourlySection.style.display = radio.value === 'hourly' ? 'block' : 'none';
                    fixedSection.style.display = radio.value === 'fixed' ? 'block' : 'none';
                }
            });
        }
    });