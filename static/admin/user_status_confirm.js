// Admin User sahifasi: "Talaba holati" (status) o'zgartirilganda oddiy ogohlantirish chiqaradi.
// Foydalanuvchi "OK" bossa o'zgaradi, "Bekor" bossa eski qiymatga qaytadi.
(function () {
    'use strict';

    function init() {
        var statusField = document.getElementById('id_status');
        if (!statusField) {
            return;
        }

        // Joriy (boshlang'ich) qiymatni eslab qolamiz
        var previousValue = statusField.value;

        statusField.addEventListener('focus', function () {
            previousValue = statusField.value;
        });

        statusField.addEventListener('change', function () {
            var newValue = statusField.value;
            if (newValue === previousValue) {
                return;
            }

            var labelMap = { 'iqtidorli': 'Iqtidorli', 'oddiy': 'Oddiy' };
            var newLabel = labelMap[newValue] || newValue;

            var ok = window.confirm(
                'Talaba holatini "' + newLabel + '" ga o\'zgartirmoqchimisiz?'
            );

            if (ok) {
                previousValue = newValue;
            } else {
                statusField.value = previousValue;
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
