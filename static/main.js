// CloudClass Main JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 2. Add active class to nav links based on current path
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#6366f1';
            link.style.borderBottom = '2px solid #6366f1';
        }
    });

    // 3. Confirmation for sensitive actions
    const deleteBtns = document.querySelectorAll('.btn-danger');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });

    // 4. Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = 'Processing...';
                submitBtn.disabled = true;
            }
        });
    });
});
