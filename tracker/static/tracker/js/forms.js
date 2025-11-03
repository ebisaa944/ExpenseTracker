// ExpenseTracker Forms Management
class ExpenseForms {
    constructor() {
        this.init();
    }

    init() {
        this.initializeFormHandlers();
        this.setupFormValidation();
    }

    // Initialize form handlers
    initializeFormHandlers() {
        // Form submission handling
        this.setupFormSubmissions();
    }

    // Setup form submissions
    setupFormSubmissions() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });
    }

    // Handle form submission
    handleFormSubmit(e) {
        const form = e.target;
        
        if (!this.validateForm(form)) {
            e.preventDefault();
            return;
        }
        
        this.showFormLoading(form);
    }

    // Validate form
    validateForm(form) {
        // Clear previous errors
        this.clearFormErrors(form);
        
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        return isValid;
    }

    // Show field error
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
    }

    // Clear form errors
    clearFormErrors(form) {
        const errorFields = form.querySelectorAll('.is-invalid');
        errorFields.forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        const errorMessages = form.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(message => {
            message.remove();
        });
    }

    // Setup form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // Show form loading
    showFormLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Processing...
            `;
            submitButton.dataset.originalText = originalText;
        }
    }
}

// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.expenseForms = new ExpenseForms();
});