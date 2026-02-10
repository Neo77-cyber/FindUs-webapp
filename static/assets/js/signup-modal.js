
        
         document.getElementById('modal-login-form').onsubmit = async function(e) {
             e.preventDefault();
             
             const form = e.target;
             const formData = new FormData(form);
             const messagesDiv = document.getElementById('modal-messages');
             
             try {
                 const response = await fetch(form.action, {
                     method: 'POST',
                     body: formData,
                     headers: {
                         'X-Requested-With': 'XMLHttpRequest'
                     }
                 });
                 
                 if (response.redirected) {
                    
                     window.location.reload();
                 } else {
                    
                     const text = await response.text();
                     messagesDiv.innerHTML = `
                         <div class="alert alert-error">
                             Invalid username or password
                         </div>
                     `;
                 }
             } catch (error) {
                 messagesDiv.innerHTML = `
                     <div class="alert alert-error">
                         Network error. Please try again.
                     </div>
                 `;
             }
         };
         
         
         
         document.getElementById('modal-login-form').onsubmit = async function(e) {
         e.preventDefault();
         
         const form = e.target;
         const submitBtn = document.getElementById('modal-submit-btn');
         const btnText = document.getElementById('btn-text');
         const btnSpinner = document.getElementById('btn-spinner');
         const messagesDiv = document.getElementById('modal-messages');
         
         
         submitBtn.disabled = true;
         btnText.style.display = 'none';
         btnSpinner.style.display = 'inline';
         
         
         messagesDiv.innerHTML = '';
         
         try {
             const formData = new FormData(form);
             const response = await fetch(form.action, {
                 method: 'POST',
                 body: formData,
                 headers: {
                     'X-Requested-With': 'XMLHttpRequest'
                 }
             });
             
             if (response.redirected) {
                 
                 window.location.reload();
             } else {
                 
                 const text = await response.text();
                 messagesDiv.innerHTML = `
                     <div class="alert alert-error">
                         Invalid username or password
                     </div>
                 `;
                 
                 // Reset button
                 submitBtn.disabled = false;
                 btnText.style.display = 'inline';
                 btnSpinner.style.display = 'none';
             }
         } catch (error) {
             messagesDiv.innerHTML = `
                 <div class="alert alert-error">
                     Network error. Please try again.
                 </div>
             `;
             
             // Reset button
             submitBtn.disabled = false;
             btnText.style.display = 'inline';
             btnSpinner.style.display = 'none';
         }
         };
         
     