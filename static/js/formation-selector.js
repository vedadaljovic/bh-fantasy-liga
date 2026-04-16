document.addEventListener('DOMContentLoaded', function () {
    const formationToggle = document.getElementById('formation-toggle');
    const formationSelector = document.getElementById('formation-selector');
    const formationOptions = document.querySelectorAll('.formation-option');
    const formationClose = document.querySelector('.formation-selector__close');
    const currentFormationSpan = document.getElementById('current-formation');

    // Toggle formation selector visibility
    if (formationToggle) {
        formationToggle.addEventListener('click', function () {
            formationSelector.classList.toggle('active');
            formationToggle.setAttribute('aria-expanded', formationSelector.classList.contains('active'));
        });
    }

    // Close formation selector
    if (formationClose) {
        formationClose.addEventListener('click', function () {
            formationSelector.classList.remove('active');
            formationToggle.setAttribute('aria-expanded', 'false');
        });
    }

    // Handle formation selection
    formationOptions.forEach(option => {
        option.addEventListener('click', function () {
            const selectedFormation = this.getAttribute('data-formation');
            
            formationOptions.forEach(opt => opt.classList.remove('active'));
            
            this.classList.add('active');
            
            if (currentFormationSpan) {
                currentFormationSpan.textContent = selectedFormation;
            }
            
            // POST formation change to backend later
        });
    });

    // Close selector when clicking outside
    document.addEventListener('click', function (event) {
        if (formationSelector && formationSelector.classList.contains('active')) {
            if (!formationSelector.contains(event.target) && !formationToggle.contains(event.target)) {
                formationSelector.classList.remove('active');
                formationToggle.setAttribute('aria-expanded', 'false');
            }
        }
    });
});
