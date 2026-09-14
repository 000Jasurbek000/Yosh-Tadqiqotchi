(function () {
    function restoreNativeCodeSelect() {
        var el = document.getElementById('id_code');
        if (!el || el.tagName !== 'SELECT') {
            return;
        }
        el.classList.add('admin-native-select');
        if (window.jQuery && window.jQuery.fn && window.jQuery.fn.select2) {
            try {
                window.jQuery(el).select2('destroy');
            } catch (e) {}
        }
        el.style.display = 'block';
        el.removeAttribute('data-select2-id');
        el.classList.remove('select2-hidden-accessible');
        var wrap = el.closest('.field-code') || el.parentElement;
        if (wrap) {
            wrap.querySelectorAll('.select2-container').forEach(function (node) {
                node.remove();
            });
        }
    }

    function start() {
        restoreNativeCodeSelect();
        [50, 200, 600, 1200].forEach(function (ms) {
            setTimeout(restoreNativeCodeSelect, ms);
        });
        var form = document.getElementById('olympiadprogram_form') || document.querySelector('.field-code');
        if (form && window.MutationObserver) {
            var observer = new MutationObserver(restoreNativeCodeSelect);
            observer.observe(form, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
