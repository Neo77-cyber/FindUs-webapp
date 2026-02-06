

  document.addEventListener('DOMContentLoaded', function() {
   
    document.querySelectorAll('.toggle-password').forEach(button => {
      button.addEventListener('click', function() {
        const input = this.parentElement.querySelector('input');
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        
        
        const svg = this.querySelector('svg');
        if (type === 'text') {
          svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
        } else {
          svg.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
        }
      });
    });

    
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
      signupForm.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('.auth-submit');
        const btnText = submitBtn.querySelector('.btn-text');
        const spinner = submitBtn.querySelector('.spinner-container');
        
       
        const requiredInputs = this.querySelectorAll('input[required]');
        let isValid = true;
        
        requiredInputs.forEach(input => {
          if (!input.value.trim()) {
            isValid = false;
            
            input.classList.add('error');
            
            let errorDiv = input.parentElement.parentElement.querySelector('.error-feedback');
            if (!errorDiv) {
              errorDiv = document.createElement('div');
              errorDiv.className = 'error-feedback';
              errorDiv.textContent = 'This field is required';
              input.parentElement.parentElement.appendChild(errorDiv);
            }
          } else {
            input.classList.remove('error');
            
            const errorDiv = input.parentElement.parentElement.querySelector('.error-feedback');
            if (errorDiv && errorDiv.textContent === 'This field is required') {
              errorDiv.remove();
            }
          }
        });
        
        if (!isValid) {
          e.preventDefault();
          return;
        }
        
        
        if (btnText) btnText.style.display = 'none';
        if (spinner) spinner.style.display = 'flex';
        
        
        submitBtn.disabled = true;
        submitBtn.classList.add('processing');
        submitBtn.style.opacity = '0.7';
        submitBtn.style.cursor = 'wait';
        
        
        setTimeout(() => {
          if (submitBtn.disabled) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('processing');
            submitBtn.style.opacity = '1';
            submitBtn.style.cursor = 'pointer';
            if (btnText) btnText.style.display = 'inline';
            if (spinner) spinner.style.display = 'none';
            alert('Submission is taking too long. Please try again.');
          }
        }, 10000); 
      });
    }

    
    const emailInput = document.getElementById('signup-email');
    if (emailInput) {
      emailInput.addEventListener('blur', function() {
        const email = this.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
          this.classList.add('error');
          let errorDiv = this.parentElement.querySelector('.error-feedback');
          if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-feedback';
            this.parentElement.appendChild(errorDiv);
          }
          errorDiv.textContent = 'Please enter a valid email address';
        } else if (email && emailRegex.test(email)) {
          this.classList.remove('error');
          const errorDiv = this.parentElement.querySelector('.error-feedback');
          if (errorDiv && errorDiv.textContent === 'Please enter a valid email address') {
            errorDiv.remove();
          }
        }
      });
    }

    
    const passwordInput = document.getElementById('signup-password');
    if (passwordInput) {
      passwordInput.addEventListener('input', function() {
        const password = this.value;
        
        if (password.length > 0 && password.length < 8) {
          this.classList.add('error');
          let errorDiv = this.parentElement.parentElement.querySelector('.error-feedback');
          if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-feedback';
            this.parentElement.parentElement.appendChild(errorDiv);
          }
          errorDiv.textContent = 'Password must be at least 8 characters';
        } else if (password.length >= 8) {
          this.classList.remove('error');
          const errorDiv = this.parentElement.parentElement.querySelector('.error-feedback');
          if (errorDiv && errorDiv.textContent === 'Password must be at least 8 characters') {
            errorDiv.remove();
          }
        }
      });
    }

    
    const password2Input = document.getElementById('signup-password2');
    if (passwordInput && password2Input) {
      password2Input.addEventListener('input', function() {
        const password1 = passwordInput.value;
        const password2 = this.value;
        
        if (password2 && password1 !== password2) {
          this.classList.add('error');
          let errorDiv = this.parentElement.parentElement.querySelector('.error-feedback');
          if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-feedback';
            this.parentElement.parentElement.appendChild(errorDiv);
          }
          errorDiv.textContent = 'Passwords do not match';
        } else if (password2 && password1 === password2) {
          this.classList.remove('error');
          const errorDiv = this.parentElement.parentElement.querySelector('.error-feedback');
          if (errorDiv && errorDiv.textContent === 'Passwords do not match') {
            errorDiv.remove();
          }
        }
      });
    }
  });

  
  document.addEventListener('input', function(e) {
    if (e.target.matches('input, select, textarea')) {
      e.target.classList.remove('error');
      const errorDiv = e.target.parentElement.querySelector('.error-feedback');
      if (errorDiv && !errorDiv.textContent.includes('already registered')) {
        errorDiv.remove();
      }
    }
  });
