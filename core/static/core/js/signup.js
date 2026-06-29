const emailInput = document.getElementById('id_email');

if (emailInput) {
    emailInput.addEventListener('input', function() {
        if (!this.value) {
            this.classList.remove('is-valid', 'is-invalid');
            return;
        }

        if (this.checkValidity()) {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
            return;
        }

        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
    });
}