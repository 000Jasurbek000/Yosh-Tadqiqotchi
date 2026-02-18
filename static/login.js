// Login Form Handler
const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const rememberCheckbox = document.getElementById('remember');
const successMessage = document.getElementById('successMessage');

// Form Submission Handler
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const remember = rememberCheckbox.checked;
    
    // Basic validation
    if (!email || !password) {
        showErrorMessage('Please fill in all fields');
        return;
    }
    
    if (!isValidEmail(email)) {
        showErrorMessage('Please enter a valid email address');
        return;
    }
    
    if (password.length < 6) {
        showErrorMessage('Password must be at least 6 characters');
        return;
    }
    
    // Simulate login process
    console.log('Login attempt:', { email, remember });
    
    // Save email if remember me is checked
    if (remember) {
        localStorage.setItem('rememberedEmail', email);
    } else {
        localStorage.removeItem('rememberedEmail');
    }
    
    // Show success message
    showSuccessMessage();
    
    // Reset form
    loginForm.reset();
    
    // Simulate redirect after 1.5 seconds
    setTimeout(() => {
        console.log('Redirecting to dashboard...');
    }, 1500);
});

// Email Validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show Error Message
function showErrorMessage(message) {
    const errorDiv = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    errorText.textContent = message;
    errorDiv.classList.remove('hidden', 'scale-95');
    errorDiv.classList.add('scale-100');
    
    setTimeout(() => {
        errorDiv.classList.remove('scale-100');
        errorDiv.classList.add('scale-95');
        setTimeout(() => {
            errorDiv.classList.add('hidden');
        }, 300);
    }, 4000);
}

// Show Success Message
function showSuccessMessage() {
    successMessage.classList.remove('hidden', 'scale-95');
    successMessage.classList.add('scale-100');
    
    setTimeout(() => {
        successMessage.classList.remove('scale-100');
        successMessage.classList.add('scale-95');
        setTimeout(() => {
            successMessage.classList.add('hidden');
        }, 300);
    }, 3000);
}

// Load remembered email on page load
window.addEventListener('DOMContentLoaded', () => {
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
        emailInput.value = rememberedEmail;
        rememberCheckbox.checked = true;
    }
});

// Input Focus Effects
[emailInput, passwordInput].forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('ring-2', 'ring-pink-600');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.classList.remove('ring-2', 'ring-pink-600');
    });
});
