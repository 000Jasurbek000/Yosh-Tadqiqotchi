// Register Form Handler
const registerForm = document.getElementById('registerForm');
const fullNameInput = document.getElementById('fullName');
const phoneInput = document.getElementById('phone');
const regionSelect = document.getElementById('region');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirmPassword');
const termsCheckbox = document.getElementById('terms');
const successMessage = document.getElementById('successMessage');

// Form Submission Handler
registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const fullName = fullNameInput.value.trim();
    const phone = phoneInput.value.trim();
    const region = regionSelect.value;
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const terms = termsCheckbox.checked;
    
    // Basic validation
    if (!fullName || !phone || !region || !password || !confirmPassword) {
        showErrorMessage('Iltimos, barcha maydonlarni to\'ldiring');
        return;
    }
    
    // Validate full name (at least 2 words)
    if (fullName.split(' ').length < 2) {
        showErrorMessage('Iltimos, to\'liq ismingizni kiriting (Familiya Ism Otasining ismi)');
        return;
    }
    
    // Validate phone number
    if (!isValidPhone(phone)) {
        showErrorMessage('Telefon raqam noto\'g\'ri formatda (+998 XX XXX XX XX)');
        return;
    }
    
    // Validate password length
    if (password.length < 8) {
        showErrorMessage('Parol kamida 8 ta belgidan iborat bo\'lishi kerak');
        return;
    }
    
    // Check if passwords match
    if (password !== confirmPassword) {
        showErrorMessage('Parollar bir-biriga mos kelmaydi');
        return;
    }
    
    // Check if terms are accepted
    if (!terms) {
        showErrorMessage('Foydalanish shartlarini qabul qilishingiz kerak');
        return;
    }
    
    // Simulate registration process
    console.log('Registration attempt:', { fullName, phone, region, password });
    
    // Show success message
    showSuccessMessage();
    
    // Reset form
    registerForm.reset();
    
    // Simulate redirect after 2 seconds
    setTimeout(() => {
        console.log('Redirecting to login page...');
        // window.location.href = 'login.html';
    }, 2000);
});

// Phone Number Validation
function isValidPhone(phone) {
    // Remove all spaces and special characters
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    
    // Check if it starts with +998 and has 12 digits total
    const phoneRegex = /^\+998\d{9}$/;
    return phoneRegex.test(cleanPhone);
}

// Phone Number Auto-formatting
phoneInput.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, ''); // Remove non-digits
    
    // Start with +998
    if (!value.startsWith('998')) {
        if (value.length > 0) {
            value = '998' + value;
        } else {
            value = '998';
        }
    }
    
    // Format: +998 XX XXX XX XX
    let formatted = '+998';
    if (value.length > 3) {
        formatted += ' ' + value.substring(3, 5);
    }
    if (value.length > 5) {
        formatted += ' ' + value.substring(5, 8);
    }
    if (value.length > 8) {
        formatted += ' ' + value.substring(8, 10);
    }
    if (value.length > 10) {
        formatted += ' ' + value.substring(10, 12);
    }
    
    e.target.value = formatted;
});

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
    }, 5000);
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

// Password Strength Indicator
passwordInput.addEventListener('input', (e) => {
    const password = e.target.value;
    const strength = calculatePasswordStrength(password);
    
    // You can add visual feedback here if needed
    console.log('Password strength:', strength);
});

function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    return strength; // 0-5
}

// Confirm Password Real-time Validation
confirmPasswordInput.addEventListener('input', (e) => {
    const password = passwordInput.value;
    const confirmPassword = e.target.value;
    
    if (confirmPassword.length > 0) {
        if (password === confirmPassword) {
            e.target.style.borderColor = 'rgb(34 197 94)'; // green
        } else {
            e.target.style.borderColor = 'rgb(239 68 68)'; // red
        }
    } else {
        e.target.style.borderColor = ''; // reset
    }
});

// Load remembered email on page load
window.addEventListener('DOMContentLoaded', () => {
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
        emailInput.value = rememberedEmail;
        rememberCheckbox.checked = true;
    }
});


// Input Focus Effects
[fullNameInput, phoneInput, regionSelect, passwordInput, confirmPasswordInput].forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('ring-2', 'ring-pink-600');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.classList.remove('ring-2', 'ring-pink-600');
    });
});
