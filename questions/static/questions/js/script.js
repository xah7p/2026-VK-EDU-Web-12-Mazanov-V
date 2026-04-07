document.getElementById('questionTitle').addEventListener('input', function() {
    if (this.value.length >= 15) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    } else if (this.value.length > 0) {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
    } else {
        this.classList.remove('is-valid', 'is-invalid');
    }
});

document.getElementById('questionBody').addEventListener('input', function() {
    if (this.value.trim()) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    } else {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
    }
});