(function () {
    function addCodePlusButton() {
        var el = document.getElementById('id_code');
        if (!el || el.tagName !== 'SELECT') {
            return;
        }
        if (document.getElementById('add_id_code')) {
            return;
        }
        var host = el.closest('.related-widget-wrapper') || el.parentElement;
        host.classList.add('related-widget-wrapper');
        var link = document.createElement('a');
        link.id = 'add_id_code';
        link.className = 'related-widget-wrapper-link add-related';
        link.href = '/admin/main/olympiadprogramcode/add/?_to_field=code&_popup=1';
        link.title = 'Yangi olimpiada kodi qo\'shish';
        link.innerHTML = '<i class="fas fa-plus-circle"></i>';
        host.appendChild(link);
    }

    function start() {
        addCodePlusButton();
        setTimeout(addCodePlusButton, 300);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
