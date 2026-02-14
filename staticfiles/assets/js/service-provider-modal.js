(function () {
    "use strict";

    // ============================================
    // Multiselect Dropdown
    // ============================================
    function initMultiselect() {
      const triggers = document.querySelectorAll(".multiselect-trigger");
      
      triggers.forEach(trigger => {
        const dropdown = trigger.nextElementSibling;
        if (!dropdown) return;
        
        const checkboxes = dropdown.querySelectorAll(".multiselect-checkbox");
        const searchInput = dropdown.querySelector(".multiselect-search-input");
        const options = dropdown.querySelectorAll(".multiselect-option");

        trigger.addEventListener("click", function (e) {
          e.preventDefault();
          const isExpanded = trigger.getAttribute("aria-expanded") === "true";
          trigger.setAttribute("aria-expanded", !isExpanded);
          dropdown.classList.toggle("active");
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", function (e) {
          if (!trigger.contains(e.target) && !dropdown.contains(e.target)) {
            trigger.setAttribute("aria-expanded", "false");
            dropdown.classList.remove("active");
          }
        });

        // Update trigger text based on selections
        function updateTriggerText() {
          const selected = Array.from(checkboxes)
            .filter((cb) => cb.checked)
            .map((cb) => {
              const label = cb
                .closest(".multiselect-option")
                .querySelector(".multiselect-option-text");
              return label ? label.textContent : "";
            });

          const placeholder = trigger.querySelector(
            ".multiselect-placeholder"
          );
          if (selected.length === 0) {
            placeholder.textContent = "Select options";
            placeholder.style.color = "var(--text-muted)";
          } else if (selected.length === 1) {
            placeholder.textContent = selected[0];
            placeholder.style.color = "var(--text-primary)";
          } else {
            placeholder.textContent = `${selected.length} selected`;
            placeholder.style.color = "var(--text-primary)";
          }
        }

        checkboxes.forEach((checkbox) => {
          checkbox.addEventListener("change", updateTriggerText);
        });

        if (searchInput) {
          searchInput.addEventListener("input", function () {
            const searchTerm = this.value.toLowerCase();
            options.forEach((option) => {
              const text = option
                .querySelector(".multiselect-option-text")
                .textContent.toLowerCase();
              option.style.display = text.includes(searchTerm) ? "flex" : "none";
            });
          });
        }
      });
    }

    
// Delete Service Modal
document.addEventListener('DOMContentLoaded', function() {
const deleteModal = document.getElementById('delete-modal-overlay');
const closeDeleteModalBtn = document.getElementById('close-delete-modal');
const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
const deleteServiceForm = document.getElementById('delete-service-form');
const deleteServiceIdInput = document.getElementById('delete-service-id');
const deleteServiceInfo = document.getElementById('delete-service-info');

// Open delete modal when delete button is clicked
document.querySelectorAll('.provider-action-btn.delete').forEach(btn => {
    btn.addEventListener('click', function() {
        const serviceId = this.dataset.serviceId;
        const serviceTitle = this.dataset.serviceTitle;
        const serviceCategory = this.dataset.serviceCategory;
        
        // Set service info in modal
        deleteServiceInfo.innerHTML = `
            <h4>${serviceTitle}</h4>
            <p>Category: ${serviceCategory}</p>
            <p>ID: ${serviceId}</p>
        `;
        
        // Set service ID in hidden input
        deleteServiceIdInput.value = serviceId;
        
        // Show modal
        deleteModal.style.display = 'flex';
        setTimeout(() => {
            deleteModal.classList.add('active');
        }, 10);
        document.body.style.overflow = 'hidden';
    });
});

// Close modal functions
function closeDeleteModal() {
    deleteModal.classList.remove('active');
    setTimeout(() => {
        deleteModal.style.display = 'none';
    }, 300);
    document.body.style.overflow = '';
}

// Close modal on X button click
if (closeDeleteModalBtn) {
    closeDeleteModalBtn.addEventListener('click', closeDeleteModal);
}

// Close modal on Cancel button click
if (cancelDeleteBtn) {
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
}

// Close modal when clicking outside
deleteModal.addEventListener('click', function(e) {
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

// Handle form submission
if (deleteServiceForm) {
deleteServiceForm.addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent normal form submission
    
    const submitBtn = this.querySelector('.btn-confirm-delete');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = 'Deleting...';
    submitBtn.disabled = true;
    
    // Get form data
    const formData = new FormData(this);
    
    // Send AJAX request
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            closeDeleteModal();
            
            // Show success message
            alert('Service deleted successfully!');
            
            // Option 1: Reload the page
            window.location.reload();
            
            // Option 2: Remove the service card without reloading
            // const serviceCard = document.querySelector(`[data-service-id="${serviceId}"]`).closest('.service-card');
            // if (serviceCard) {
            //     serviceCard.remove();
            // }
        } else {
            alert('Error: ' + (data.error || 'Failed to delete service'));
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    })
    .catch(error => {
        alert('Error deleting service');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
});
}
});

// Edit Service Modal - COMPLETE VERSION
document.addEventListener('DOMContentLoaded', function() {


const editModal = document.getElementById('edit-modal-overlay');
const closeEditBtn = document.getElementById('close-edit-modal');
const cancelEditBtn = document.getElementById('cancel-edit-btn');
const editForm = document.getElementById('edit-service-form');
const saveBtn = document.querySelector('.btn-save-edit');

if (!editModal) {
    
    return;
}

// Price type switching
const priceHourly = document.getElementById('edit-price-hourly');
const priceFixed = document.getElementById('edit-price-fixed');
const hourlyRateGroup = document.getElementById('hourly-rate-group');
const fixedPriceGroup = document.getElementById('fixed-price-group');

function updatePriceFields() {
    if (priceHourly.checked) {
        hourlyRateGroup.style.display = 'block';
        fixedPriceGroup.style.display = 'none';
    } else if (priceFixed.checked) {
        hourlyRateGroup.style.display = 'none';
        fixedPriceGroup.style.display = 'block';
    }
}

if (priceHourly) priceHourly.addEventListener('change', updatePriceFields);
if (priceFixed) priceFixed.addEventListener('change', updatePriceFields);

// Show modal function
function showEditModal() {
    document.body.style.overflow = 'hidden';
    editModal.classList.add('active');
}

// Close modal function
function closeEditModal() {
    editModal.classList.remove('active');
    setTimeout(() => {
        document.body.style.overflow = '';
        // Reset form
        if (editForm) {
            editForm.reset();
            hourlyRateGroup.style.display = 'none';
            fixedPriceGroup.style.display = 'none';
        }
    }, 300);
}

// Close buttons
if (closeEditBtn) {
    closeEditBtn.addEventListener('click', closeEditModal);
}

if (cancelEditBtn) {
    cancelEditBtn.addEventListener('click', closeEditModal);
}

// Close when clicking outside
editModal.addEventListener('click', function(e) {
    if (e.target === editModal) {
        closeEditModal();
    }
});

// Open edit modal
document.querySelectorAll('.provider-action-btn.edit').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const serviceId = this.dataset.serviceId;
        
        
        // Show loading state
        showEditModal();
        
        // Fetch service data
        fetch(`/edit-service/?service_id=${serviceId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const service = data.service;
                    
                    // Fill form fields
                    document.getElementById('edit-service-id').value = service.id;
                    document.getElementById('edit-title').value = service.title;
                    document.getElementById('edit-category').value = service.category;
                    document.getElementById('edit-description').value = service.description;
                    document.getElementById('edit-region').value = service.region || '';
                    document.getElementById('edit-availability').value = service.availability;
                    
                    // Set price type
                    if (service.price_type === 'hourly') {
                        priceHourly.checked = true;
                        document.getElementById('edit-hourly-rate').value = service.hourly_rate;
                    } else {
                        priceFixed.checked = true;
                        document.getElementById('edit-fixed-price').value = service.fixed_price;
                    }
                    
                    // Update price fields visibility
                    updatePriceFields();
                    
                } else {
                    alert('Error: ' + data.error);
                    closeEditModal();
                }
            })
            .catch(error => {
                
                alert('Error loading service details');
                closeEditModal();
            });
    });
});

// Handle form submission
if (editForm) {
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!saveBtn) return;
        
        const originalText = saveBtn.innerHTML;
        const originalState = saveBtn.disabled;
        
        // Show loading
        saveBtn.innerHTML = 'Saving...';
        saveBtn.disabled = true;
        
        const formData = new FormData(this);
        
        fetch('/edit-service/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Service updated successfully!');
                closeEditModal();
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            } else {
                alert('Error: ' + data.error);
                saveBtn.innerHTML = originalText;
                saveBtn.disabled = originalState;
            }
        })
        .catch(error => {
            
            alert('Error saving changes');
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = originalState;
        });
    });
}


});

// FIXED BOOST MODAL JS
document.addEventListener('DOMContentLoaded', function() {

// Function to open the modal
function openBoostModal(serviceId) {
  // Set service ID in form
  document.getElementById('boost-service-id').value = serviceId;
  
  // Generate reference number
  const ref = 'BOOST-' + serviceId + '-' + Date.now().toString().slice(-6);
  const serviceRefElement = document.getElementById('service-ref');
  if (serviceRefElement) {
      serviceRefElement.textContent = ref;
  }
  
  // Reset form
  document.querySelectorAll('.boost-plan').forEach(p => p.classList.remove('selected'));
  const selectedPlanInfo = document.getElementById('selected-plan-info');
  if (selectedPlanInfo) {
      selectedPlanInfo.style.display = 'none';
  }
  
  const fileInput = document.getElementById('payment-proof');
  if (fileInput) fileInput.value = '';
  
  const fileName = document.getElementById('file-name');
  if (fileName) fileName.textContent = '';
  
  const paymentAmount = document.getElementById('payment-amount');
  if (paymentAmount) paymentAmount.textContent = '0';
  
  // Show modal
  const modal = document.getElementById('boost-modal-overlay');
  if (modal) {
      modal.style.display = 'flex';
      setTimeout(() => {
          modal.classList.add('active');
      }, 10);
  }
  
  // Alert user
  alert('Boost initiated! Please select a plan and upload payment proof.');
}

// 1. OPEN MODAL when boost button is clicked - WITH BOOST STATUS CHECK
document.querySelectorAll('.provider-action-btn.boost').forEach(btn => {
  btn.addEventListener('click', function() {
      // Get service ID
      const serviceId = this.getAttribute('data-service-id');
      
      // Check if service already has pending boost
      fetch('/check-boost-status/' + serviceId + '/')
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(data => {
              if (data.has_pending_boost) {
                  // Show alert if pending boost exists
                  alert('You already have a pending boost request for this service. Please wait for approval.');
                  return;
              }
              
              // If no pending boost, open the modal
              openBoostModal(serviceId);
          })
          .catch(error => {
              console.error('Error checking boost status:', error);
              // If check fails, still open modal (server will validate on submit)
              openBoostModal(serviceId);
          });
  });
});

// 2. PLAN SELECTION - when user clicks a plan
document.querySelectorAll('.boost-plan').forEach(plan => {
  plan.addEventListener('click', function() {
      
      // Remove selected from all plans
      document.querySelectorAll('.boost-plan').forEach(p => {
          p.classList.remove('selected');
      });
      
      // Add selected to clicked plan
      this.classList.add('selected');
      
      // Get plan details
      const days = this.getAttribute('data-days');
      const price = this.getAttribute('data-price');
      
      // Update UI
      const selectedPlanName = document.getElementById('selected-plan-name');
      const selectedPlanPrice = document.getElementById('selected-plan-price');
      const selectedPlanDays = document.getElementById('selected-plan-days');
      const selectedPlanInfo = document.getElementById('selected-plan-info');
      
      if (selectedPlanName) {
          selectedPlanName.textContent = this.querySelector('h3').textContent;
      }
      if (selectedPlanPrice) selectedPlanPrice.textContent = '€' + price;
      if (selectedPlanDays) selectedPlanDays.textContent = days;
      if (selectedPlanInfo) selectedPlanInfo.style.display = 'block';
      
      // Update form fields
      const boostDuration = document.getElementById('boost-duration');
      const paymentAmount = document.getElementById('payment-amount');
      
      if (boostDuration) boostDuration.value = days;
      if (paymentAmount) paymentAmount.textContent = price;
  });
});

// 3. FILE UPLOAD - show file name
const paymentProofInput = document.getElementById('payment-proof');
if (paymentProofInput) {
  paymentProofInput.addEventListener('change', function() {
      const fileNameElement = document.getElementById('file-name');
      if (this.files.length > 0 && fileNameElement) {
          const file = this.files[0];
          const fileSize = (file.size / (1024 * 1024)).toFixed(2); // MB
          fileNameElement.textContent = file.name + ' (' + fileSize + ' MB)';
      }
  });
}

// 4. CLOSE MODAL function
function closeModal() {
  const modal = document.getElementById('boost-modal-overlay');
  if (modal) {
      modal.classList.remove('active');
      setTimeout(() => {
          modal.style.display = 'none';
          document.body.style.overflow = '';
      }, 300);
  }
}

// Close buttons
const closeBtn = document.getElementById('close-boost-modal');
const cancelBtn = document.getElementById('cancel-boost-btn');

if (closeBtn) closeBtn.addEventListener('click', closeModal);
if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

// Close when clicking outside modal
const modalOverlay = document.getElementById('boost-modal-overlay');
if (modalOverlay) {
  modalOverlay.addEventListener('click', function(e) {
      if (e.target === this) {
          closeModal();
      }
  });
}

// 5. SUBMIT FORM - when user clicks "Submit Boost Request"
const submitBtn = document.querySelector('.btn-confirm-boost');
if (submitBtn) {
  submitBtn.addEventListener('click', function(e) {
      e.preventDefault();
      
      // CHECK 1: Is a plan selected?
      if (!document.querySelector('.boost-plan.selected')) {
          alert(' Please select a boost plan first');
          return;
      }
      
      // CHECK 2: Is file uploaded?
      const fileInput = document.getElementById('payment-proof');
      if (!fileInput || !fileInput.files.length) {
          alert(' Please upload payment proof');
          return;
      }
      
      // Show loading
      const originalText = this.innerHTML;
      this.innerHTML = 'Submitting...';
      this.disabled = true;
      
      // Get form data
      const form = document.getElementById('boost-service-form');
      const formData = new FormData(form);
      
      // Send to server
      fetch('/boost-service/', {
          method: 'POST',
          body: formData,
          headers: {
              'X-Requested-With': 'XMLHttpRequest'
          }
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              alert(' ' + data.message);
              closeModal();
              // Reload page after 1 second
              setTimeout(() => {
                  window.location.reload();
              }, 1000);
          } else {
              alert(' Error: ' + (data.message || data.error || 'Unknown error'));
              this.innerHTML = originalText;
              this.disabled = false;
          }
      })
      .catch(error => {
          alert(' Network error. Please try again.');
          this.innerHTML = originalText;
          this.disabled = false;
      });
  });
} else {
  console.error('Submit button not found');
}

// Initialize copy buttons
initializeCopyButtons();
});

// Copy to clipboard functions - Define them globally
function showCopyFeedback(text) {
// Remove existing feedback
const existing = document.querySelector('.copy-feedback');
if (existing) existing.remove();

// Create new feedback
const feedback = document.createElement('div');
feedback.className = 'copy-feedback';
feedback.innerHTML = `
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polyline points="20 6 9 17 4 12"></polyline>
</svg>
${text}
`;

document.body.appendChild(feedback);

// Add CSS for the feedback if not already present
if (!document.querySelector('#copy-feedback-style')) {
const style = document.createElement('style');
style.id = 'copy-feedback-style';
style.textContent = `
    .copy-feedback {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
}

// Remove after 2 seconds
setTimeout(() => {
feedback.style.animation = 'slideIn 0.3s ease reverse';
setTimeout(() => feedback.remove(), 300);
}, 2000);
}

// Generic copy function
function copyToClipboard(text) {
navigator.clipboard.writeText(text).then(() => {
showCopyFeedback('Copied to clipboard!');
}).catch(err => {
// Fallback for older browsers
const textarea = document.createElement('textarea');
textarea.value = text;
document.body.appendChild(textarea);
textarea.select();
document.execCommand('copy');
document.body.removeChild(textarea);
showCopyFeedback('Copied to clipboard!');
});
}

// Specific copy functions - Define them globally
function copyReference() {
const refElement = document.getElementById('service-ref');
const reference = 'BOOST-' + (refElement ? refElement.textContent : '');
copyToClipboard(reference);
}

function copyAmount() {
const amountElement = document.getElementById('payment-amount');
const amount = '€' + (amountElement ? amountElement.textContent : '0');
copyToClipboard(amount);
}

function copyAllDetails() {
const details = `
Beneficiary Name: Efosa Aghedo
IBAN: GB37 REVO 0099 7044 2692 40
BIC/SWIFT: REVOGB21
Bank Address: Revolut Ltd, 30 South Colonnade, E14 5HX, London, United Kingdom
Correspondent Bank BIC: CHASDEFX (for EUR transfers)
Reference: BOOST-${document.getElementById('service-ref')?.textContent || ''}
Amount: €${document.getElementById('payment-amount')?.textContent || '0'}

Important Notes:
- Use REVOGB21 as the SWIFT/BIC code
- For EUR transfers, include correspondent bank CHASDEFX
- Always include the reference number
- Transfer in EURO (€)
- Specify "No charges for beneficiary"
`.trim();

copyToClipboard(details);
}

// Initialize copy buttons
function initializeCopyButtons() {
// Attach click events to all copy buttons with data-copy attribute
document.querySelectorAll('.copy-btn[data-copy]').forEach(btn => {
// Remove any existing click listeners to avoid duplicates
btn.replaceWith(btn.cloneNode(true));
});

// Re-attach the events
document.querySelectorAll('.copy-btn[data-copy]').forEach(btn => {
btn.addEventListener('click', function() {
    const text = this.getAttribute('data-copy');
    copyToClipboard(text);
});
});

// Add hover effect to copy buttons
document.querySelectorAll('.copy-btn').forEach(btn => {
btn.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.1)';
});
btn.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1)';
});
});
}

// Event delegation for copy buttons (backup)
document.addEventListener('click', function(e) {
// Handle copy buttons with data-copy attribute
if (e.target.closest('.copy-btn[data-copy]')) {
const btn = e.target.closest('.copy-btn[data-copy]');
const text = btn.getAttribute('data-copy');
copyToClipboard(text);
e.preventDefault();
}
});

    // ============================================
    // File Upload Preview
    // ============================================
    function initFileUpload() {
      const fileInput = document.getElementById("id_service_image");
      const fileLabel = document.querySelector(
        ".file-upload-label-compact"
      );

      if (!fileInput || !fileLabel) return;

      fileInput.addEventListener("change", function () {
        const file = this.files[0];
        if (!file) return;

        const fileMain = fileLabel.querySelector(
          ".file-upload-main-compact"
        );
        const fileSub = fileLabel.querySelector(".file-upload-sub-compact");

        if (fileMain) {
          fileMain.textContent = file.name;
          fileLabel.style.borderColor = "var(--primary)";
          fileLabel.style.background = "var(--bg-secondary)";
        }

        if (fileSub) {
          const fileSizeKB = (file.size / 1024).toFixed(1);
          const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
          const sizeText =
            file.size < 1024 * 1024
              ? `${fileSizeKB} KB`
              : `${fileSizeMB} MB`;
          fileSub.textContent = sizeText;
        }
      });
    }

    // ============================================
    // Collapsible Sections Auto-Expand
    // ============================================
    function initCollapsibles() {
      const collapsibles = document.querySelectorAll(".form-collapsible");

      collapsibles.forEach((collapsible) => {
        const trigger = collapsible.querySelector(
          ".form-collapsible-trigger"
        );

        if (trigger) {
          trigger.addEventListener("click", function () {
            // Scroll into view on mobile when opening
            if (
              window.innerWidth <= 768 &&
              !collapsible.hasAttribute("open")
            ) {
              setTimeout(() => {
                collapsible.scrollIntoView({
                  behavior: "smooth",
                  block: "start",
                });
              }, 300);
            }
          });
        }
      });
    }

    // ============================================
    // Form Validation Helper
    // ============================================

    // ============================================
    // Testimonial Carousel
    // ============================================
    function initTestimonialCarousel() {
      const container = document.querySelector(".testimonials-grid");
      const prevBtn = document.querySelector(".testimonial-prev");
      const nextBtn = document.querySelector(".testimonial-next");

      if (!container) return;

      const cards = container.querySelectorAll(".testimonial-card");
      const cardWidth = cards[0]?.offsetWidth || 340;
      const gap = 24; // 1.5rem
      const scrollAmount = cardWidth + gap;

      let autoSlideInterval;
      const AUTO_SLIDE_DELAY = 5000; // 5 seconds

      function scrollPrev() {
        container.scrollBy({ left: -scrollAmount, behavior: "smooth" });
      }

      function scrollNext() {
        // If at the end, scroll back to start
        if (
          container.scrollLeft + container.clientWidth >=
          container.scrollWidth - 10
        ) {
          container.scrollTo({ left: 0, behavior: "smooth" });
        } else {
          container.scrollBy({ left: scrollAmount, behavior: "smooth" });
        }
      }

      function startAutoSlide() {
        stopAutoSlide();
        autoSlideInterval = setInterval(scrollNext, AUTO_SLIDE_DELAY);
      }

      function stopAutoSlide() {
        if (autoSlideInterval) {
          clearInterval(autoSlideInterval);
          autoSlideInterval = null;
        }
      }

      // Navigation button listeners
      if (prevBtn) {
        prevBtn.addEventListener("click", () => {
          scrollPrev();
          startAutoSlide(); // Reset timer after manual nav
        });
      }

      if (nextBtn) {
        nextBtn.addEventListener("click", () => {
          scrollNext();
          startAutoSlide(); // Reset timer after manual nav
        });
      }

      // Pause auto-slide on hover
      container.addEventListener("mouseenter", stopAutoSlide);
      container.addEventListener("mouseleave", startAutoSlide);

      // Start auto-slide
      startAutoSlide();
    }

    // ============================================
    // Service Modal & Multi-step Form
    // ============================================
    function initServiceModal() {
      const modal = document.getElementById("service-modal-overlay");
      const openBtns = document.querySelectorAll(".open-service-modal, #open-service-modal");
      const closeBtn = document.getElementById("close-service-modal");
      const form = document.getElementById("multi-step-service-form");
      
      if (!modal || !form) return;

      // Steps
      const steps = form.querySelectorAll(".service-form-step");
      const indicators = document.querySelectorAll(".step-indicator");
      const nextBtn = document.getElementById("btn-next");
      const prevBtn = document.getElementById("btn-prev");
      const submitBtn = document.getElementById("btn-submit-form");
      
      let currentStep = 1;

      function showStep(step) {
        steps.forEach(s => s.classList.remove("active"));
        indicators.forEach(i => {
          const iStep = parseInt(i.dataset.step);
          i.classList.remove("active", "completed");
          if (iStep === step) i.classList.add("active");
          if (iStep < step) i.classList.add("completed");
        });

        const targetStep = form.querySelector(`.service-form-step[data-step="${step}"]`);
        if (targetStep) targetStep.classList.add("active");

        // Footer buttons state
        prevBtn.style.display = step === 1 ? "none" : "block";
        if (step === steps.length) {
          nextBtn.style.display = "none";
          submitBtn.style.display = "flex";
        } else {
          nextBtn.style.display = "flex";
          submitBtn.style.display = "none";
        }
      }

      function validateStep(step) {
        const stepEl = form.querySelector(`.service-form-step[data-step="${step}"]`);
        const fields = stepEl.querySelectorAll("[required]");
        let isValid = true;

        fields.forEach(field => {
          const isInvalid = !field.value || (field.type === "checkbox" && !field.checked);
          
          // Check if field is inside a currency input wrapper
          const currencyWrapper = field.closest(".modal-currency-input");
          
          if (currencyWrapper) {
            // Add/remove error class on the wrapper
            if (isInvalid) {
              currencyWrapper.classList.add("error");
              isValid = false;
            } else {
              currencyWrapper.classList.remove("error");
            }
          } else {
            // Standard field - apply border color directly
            if (isInvalid) {
              field.style.borderColor = "var(--error, #dc2626)";
              isValid = false;
            } else {
              field.style.borderColor = "";
            }
          }
        });

        return isValid;
      }

      // Open Modal
      openBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.preventDefault();
          modal.classList.add("active");
          document.body.style.overflow = "hidden"; // Prevent scroll
          showStep(1);
          currentStep = 1;
        });
      });

      // Close Modal
      const closeModal = () => {
        modal.classList.remove("active");
        document.body.style.overflow = "";
      };

      closeBtn.addEventListener("click", closeModal);
      modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
      });

      // Next Step
      nextBtn.addEventListener("click", () => {
        if (validateStep(currentStep)) {
          currentStep++;
          showStep(currentStep);
        }
      });

      // Previous Step
      prevBtn.addEventListener("click", () => {
        currentStep--;
        showStep(currentStep);
      });

      // Final Submit
      submitBtn.addEventListener("click", () => {
        if (validateStep(currentStep)) {
          form.submit();
        }
      });
    }

    // ============================================
    // Initialize on DOM ready
    // ============================================
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        initMultiselect();
        initFileUpload();
        initCollapsibles();
        initTestimonialCarousel();
        initServiceModal();
      });
    } else {
      initMultiselect();
      initFileUpload();
      initCollapsibles();
      initTestimonialCarousel();
      initServiceModal();
    }
  })();