// ExpenseTracker Enhanced Forms Management
class ExpenseForms {
    constructor() {
        this.formStates = new Map();
        this.init();
    }

    init() {
        this.initializeFormHandlers();
        this.setupFormValidation();
        this.setupDynamicFormFields();
        this.setupFormAnimations();
        this.setupAutoSave();
    }

    // Initialize form handlers
    initializeFormHandlers() {
        this.setupFormSubmissions();
        this.setupInputHandlers();
        this.setupFormModals();
        this.setupQuickEntryForms();
    }

    // Setup form submissions with enhanced UX
    setupFormSubmissions() {
        const forms = document.querySelectorAll('form[data-ajax-form]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleAjaxFormSubmit(e);
            });
        });

        // Regular form submissions
        const regularForms = document.querySelectorAll('form:not([data-ajax-form])');
        regularForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });
    }

    // Setup input handlers for real-time feedback
    setupInputHandlers() {
        // Real-time validation
        const validatedInputs = document.querySelectorAll('[data-real-time-validate]');
        validatedInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validateField(e.target);
            });
            
            input.addEventListener('input', this.debounce((e) => {
                this.validateField(e.target, true);
            }, 500));
        });

        // Character counters
        const countedInputs = document.querySelectorAll('[data-char-count]');
        countedInputs.forEach(input => {
            this.setupCharacterCounter(input);
        });

        // Amount formatting
        const amountInputs = document.querySelectorAll('input[type="number"][data-amount]');
        amountInputs.forEach(input => {
            this.setupAmountFormatting(input);
        });
    }

    // Setup dynamic form fields
    setupDynamicFormFields() {
        // Dynamic field addition/removal
        const dynamicContainers = document.querySelectorAll('[data-dynamic-fields]');
        dynamicContainers.forEach(container => {
            this.setupDynamicFieldContainer(container);
        });

        // Conditional field display
        const conditionalFields = document.querySelectorAll('[data-condition]');
        conditionalFields.forEach(field => {
            this.setupConditionalField(field);
        });
    }

    // Setup form animations
    setupFormAnimations() {
        // Form step animations
        const multiStepForms = document.querySelectorAll('[data-multi-step]');
        multiStepForms.forEach(form => {
            this.setupMultiStepForm(form);
        });

        // Field focus animations
        const focusableFields = document.querySelectorAll('.form-control, .form-select');
        focusableFields.forEach(field => {
            this.setupFieldFocusEffects(field);
        });
    }

    // Setup auto-save functionality
    setupAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        autoSaveForms.forEach(form => {
            this.setupFormAutoSave(form);
        });
    }

    // Handle AJAX form submission
    async handleAjaxFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        
        if (!this.validateForm(form)) {
            return;
        }

        this.showFormLoading(form);
        
        try {
            const formData = new FormData(form);
            const response = await this.submitFormData(form.action, formData, form.method);
            
            if (response.success) {
                this.showFormSuccess(form, response.message);
                this.clearFormAutoSave(form);
                
                // Close modal if exists
                const modal = form.closest('.modal');
                if (modal) {
                    bootstrap.Modal.getInstance(modal).hide();
                }
                
                // Refresh data if needed
                if (form.dataset.refreshOnSuccess) {
                    this.refreshData();
                }
            } else {
                this.showFormError(form, response.errors || response.message);
            }
        } catch (error) {
            this.showFormError(form, 'An error occurred while submitting the form.');
            console.error('Form submission error:', error);
        } finally {
            this.hideFormLoading(form);
        }
    }

    // Handle regular form submission
    handleFormSubmit(e) {
        const form = e.target;
        
        if (!this.validateForm(form)) {
            e.preventDefault();
            return;
        }
        
        this.showFormLoading(form);
    }

    // Enhanced form validation
    validateForm(form) {
        this.clearFormErrors(form);
        
        let isValid = true;
        const fields = form.querySelectorAll('[data-validate]');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        // Custom validation rules
        const customRules = form.querySelectorAll('[data-custom-validate]');
        customRules.forEach(field => {
            if (!this.validateCustomRule(field)) {
                isValid = false;
            }
        });

        if (!isValid) {
            this.animateFormError(form);
        }
        
        return isValid;
    }

    // Validate individual field with multiple rules
    validateField(field, realTime = false) {
        let isValid = true;
        const value = field.value.trim();
        const rules = field.dataset.validate ? field.dataset.validate.split(' ') : [];

        // Clear previous errors
        this.clearFieldError(field);

        // Required validation
        if ((field.required || rules.includes('required')) && !value) {
            this.showFieldError(field, 'This field is required');
            isValid = false;
        }

        // Email validation
        if (isValid && rules.includes('email') && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            }
        }

        // Number validation
        if (isValid && rules.includes('number') && value) {
            if (isNaN(value) || Number(value) <= 0) {
                this.showFieldError(field, 'Please enter a valid number');
                isValid = false;
            }
        }

        // Min length validation
        if (isValid && rules.includes('minlength') && value) {
            const minLength = parseInt(field.dataset.minLength) || 2;
            if (value.length < minLength) {
                this.showFieldError(field, `Minimum ${minLength} characters required`);
                isValid = false;
            }
        }

        // Max length validation
        if (isValid && rules.includes('maxlength') && value) {
            const maxLength = parseInt(field.dataset.maxLength) || 255;
            if (value.length > maxLength) {
                this.showFieldError(field, `Maximum ${maxLength} characters allowed`);
                isValid = false;
            }
        }

        // Show success state for real-time validation
        if (realTime && isValid && value) {
            this.showFieldSuccess(field);
        }

        return isValid;
    }

    // Validate custom rules
    validateCustomRule(field) {
        const rule = field.dataset.customValidate;
        const value = field.value.trim();
        let isValid = true;

        switch (rule) {
            case 'amount-positive':
                if (parseFloat(value) <= 0) {
                    this.showFieldError(field, 'Amount must be greater than 0');
                    isValid = false;
                }
                break;
                
            case 'future-date':
                const selectedDate = new Date(value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate < today) {
                    this.showFieldError(field, 'Date cannot be in the past');
                    isValid = false;
                }
                break;
                
            case 'category-unique':
                // This would typically check against existing categories
                if (value && this.isDuplicateCategory(value)) {
                    this.showFieldError(field, 'Category already exists');
                    isValid = false;
                }
                break;
        }

        return isValid;
    }

    // Show enhanced field error
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.innerHTML = `
            <i class="fas fa-exclamation-circle me-1"></i>
            ${message}
        `;
        errorElement.style.display = 'block';
        
        // Add error animation
        this.animateFieldError(field);
    }

    // Show field success state
    showFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        
        let successElement = field.parentNode.querySelector('.valid-feedback');
        if (!successElement) {
            successElement = document.createElement('div');
            successElement.className = 'valid-feedback';
            field.parentNode.appendChild(successElement);
        }
        
        successElement.innerHTML = `
            <i class="fas fa-check-circle me-1"></i>
            Looks good!
        `;
        successElement.style.display = 'block';
    }

    // Clear field error
    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
        
        const successElement = field.parentNode.querySelector('.valid-feedback');
        if (successElement) {
            successElement.style.display = 'none';
        }
    }

    // Clear all form errors
    clearFormErrors(form) {
        const errorFields = form.querySelectorAll('.is-invalid');
        errorFields.forEach(field => {
            this.clearFieldError(field);
        });
    }

    // Setup character counter
    setupCharacterCounter(input) {
        const maxLength = input.maxLength || parseInt(input.dataset.charCount) || 255;
        const counter = document.createElement('div');
        counter.className = 'char-counter text-muted small mt-1';
        counter.innerHTML = `
            <span class="current-count">0</span> / <span class="max-count">${maxLength}</span>
        `;
        
        input.parentNode.appendChild(counter);
        
        const updateCounter = () => {
            const current = input.value.length;
            const currentEl = counter.querySelector('.current-count');
            currentEl.textContent = current;
            
            if (current > maxLength * 0.8) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
            
            if (current > maxLength) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        };
        
        input.addEventListener('input', updateCounter);
        updateCounter();
    }

    // Setup amount formatting
    setupAmountFormatting(input) {
        input.addEventListener('blur', (e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                e.target.value = value.toFixed(2);
            }
        });
        
        input.addEventListener('focus', (e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                e.target.value = value.toString();
            }
        });
    }

    // Setup dynamic field container
    setupDynamicFieldContainer(container) {
        const addButton = container.querySelector('[data-add-field]');
        const template = container.querySelector('[data-field-template]');
        
        if (addButton && template) {
            addButton.addEventListener('click', () => {
                const newField = template.cloneNode(true);
                newField.classList.remove('d-none');
                newField.removeAttribute('data-field-template');
                
                // Update field names and IDs
                const fields = newField.querySelectorAll('[name], [id]');
                const index = container.querySelectorAll('.dynamic-field:not([data-field-template])').length;
                
                fields.forEach(field => {
                    if (field.name) field.name = field.name.replace(/\[\d+\]/, `[${index}]`);
                    if (field.id) field.id = field.id.replace(/\d+/, index);
                });
                
                // Add remove button
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn btn-sm btn-outline-danger remove-field';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.addEventListener('click', () => {
                    newField.remove();
                });
                
                newField.appendChild(removeBtn);
                container.insertBefore(newField, addButton.parentNode);
            });
        }
    }

    // Setup conditional field display
    setupConditionalField(field) {
        const condition = field.dataset.condition;
        const [targetName, targetValue] = condition.split('=');
        const targetField = field.closest('form').querySelector(`[name="${targetName}"]`);
        
        if (targetField) {
            const updateVisibility = () => {
                if (targetField.value === targetValue) {
                    field.closest('.conditional-field').style.display = 'block';
                } else {
                    field.closest('.conditional-field').style.display = 'none';
                }
            };
            
            targetField.addEventListener('change', updateVisibility);
            updateVisibility();
        }
    }

    // Setup multi-step form
    setupMultiStepForm(form) {
        const steps = form.querySelectorAll('.form-step');
        const nextButtons = form.querySelectorAll('[data-next-step]');
        const prevButtons = form.querySelectorAll('[data-prev-step]');
        const progress = form.querySelector('.form-progress');
        
        let currentStep = 0;
        
        nextButtons.forEach(button => {
            button.addEventListener('click', () => {
                if (this.validateStep(steps[currentStep])) {
                    this.goToStep(form, currentStep + 1);
                }
            });
        });
        
        prevButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.goToStep(form, currentStep - 1);
            });
        });
    }

    // Go to specific step in multi-step form
    goToStep(form, stepIndex) {
        const steps = form.querySelectorAll('.form-step');
        const progress = form.querySelector('.form-progress');
        
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
            step.classList.toggle('d-none', index !== stepIndex);
        });
        
        if (progress) {
            const progressPercent = ((stepIndex + 1) / steps.length) * 100;
            progress.style.width = `${progressPercent}%`;
        }
    }

    // Validate step in multi-step form
    validateStep(step) {
        const fields = step.querySelectorAll('[required]');
        let isValid = true;
        
        fields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        return isValid;
    }

    // Setup field focus effects
    setupFieldFocusEffects(field) {
        const container = field.closest('.form-floating') || field.parentNode;
        
        field.addEventListener('focus', () => {
            container.classList.add('focused');
        });
        
        field.addEventListener('blur', () => {
            if (!field.value) {
                container.classList.remove('focused');
            }
        });
    }

    // Setup form auto-save
    setupFormAutoSave(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        const formId = form.id || `form-${Date.now()}`;
        
        // Load saved data
        this.loadFormState(form, formId);
        
        inputs.forEach(input => {
            input.addEventListener('input', this.debounce(() => {
                this.saveFormState(form, formId);
            }, 1000));
        });
        
        // Auto-save periodically
        setInterval(() => {
            if (this.isFormDirty(form, formId)) {
                this.saveFormState(form, formId);
            }
        }, 30000);
    }

    // Save form state
    saveFormState(form, formId) {
        const formData = new FormData(form);
        const formState = {};
        
        for (let [key, value] of formData.entries()) {
            formState[key] = value;
        }
        
        localStorage.setItem(`form-${formId}`, JSON.stringify(formState));
        this.formStates.set(formId, formState);
        
        // Show auto-save indicator
        this.showAutoSaveIndicator(form);
    }

    // Load form state
    loadFormState(form, formId) {
        const saved = localStorage.getItem(`form-${formId}`);
        if (saved) {
            const formState = JSON.parse(saved);
            
            for (let [key, value] of Object.entries(formState)) {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'password') {
                    field.value = value;
                }
            }
            
            this.formStates.set(formId, formState);
        }
    }

    // Clear form auto-save
    clearFormAutoSave(form) {
        const formId = form.id || Object.keys(this.formStates).find(key => 
            this.formStates.get(key) === form
        );
        
        if (formId) {
            localStorage.removeItem(`form-${formId}`);
            this.formStates.delete(formId);
        }
    }

    // Check if form is dirty
    isFormDirty(form, formId) {
        const currentState = this.formStates.get(formId);
        if (!currentState) return true;
        
        const formData = new FormData(form);
        const newState = {};
        
        for (let [key, value] of formData.entries()) {
            newState[key] = value;
        }
        
        return JSON.stringify(currentState) !== JSON.stringify(newState);
    }

    // Show auto-save indicator
    showAutoSaveIndicator(form) {
        let indicator = form.querySelector('.auto-save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'auto-save-indicator text-muted small mt-2';
            form.appendChild(indicator);
        }
        
        indicator.innerHTML = `
            <i class="fas fa-save me-1"></i>
            Auto-saved at ${new Date().toLocaleTimeString()}
        `;
        
        indicator.classList.add('visible');
        setTimeout(() => {
            indicator.classList.remove('visible');
        }, 3000);
    }

    // Show form loading with enhanced UI
    showFormLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Processing...
            `;
            submitButton.dataset.originalText = originalText;
        }
        
        // Disable all form inputs
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            if (input !== submitButton) {
                input.disabled = true;
            }
        });
        
        form.classList.add('form-loading');
    }

    // Hide form loading
    hideFormLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton && submitButton.dataset.originalText) {
            submitButton.disabled = false;
            submitButton.innerHTML = submitButton.dataset.originalText;
        }
        
        // Enable all form inputs
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            input.disabled = false;
        });
        
        form.classList.remove('form-loading');
    }

    // Show form success
    showFormSuccess(form, message) {
        this.showFormMessage(form, message, 'success');
        
        // Auto-clear form if enabled
        if (form.dataset.clearOnSuccess) {
            setTimeout(() => {
                form.reset();
                form.classList.remove('was-validated');
                this.clearFormErrors(form);
            }, 2000);
        }
    }

    // Show form error
    showFormError(form, errors) {
        if (typeof errors === 'string') {
            this.showFormMessage(form, errors, 'error');
        } else if (typeof errors === 'object') {
            // Show field-specific errors
            Object.entries(errors).forEach(([fieldName, errorMessage]) => {
                const field = form.querySelector(`[name="${fieldName}"]`);
                if (field) {
                    this.showFieldError(field, errorMessage);
                }
            });
        }
    }

    // Show form message
    showFormMessage(form, message, type) {
        let messageEl = form.querySelector('.form-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.className = 'form-message alert mt-3';
            form.appendChild(messageEl);
        }
        
        messageEl.className = `form-message alert alert-${type === 'success' ? 'success' : 'danger'} mt-3`;
        messageEl.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'} me-2"></i>
            ${message}
        `;
        messageEl.style.display = 'block';
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 5000);
        }
    }

    // Animate form error
    animateFormError(form) {
        form.classList.add('form-error-shake');
        setTimeout(() => {
            form.classList.remove('form-error-shake');
        }, 500);
    }

    // Animate field error
    animateFieldError(field) {
        field.classList.add('field-error-shake');
        setTimeout(() => {
            field.classList.remove('field-error-shake');
        }, 300);
    }

    // Setup form modals
    setupFormModals() {
        const modalTriggers = document.querySelectorAll('[data-form-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                const modalId = trigger.dataset.formModal;
                const modal = document.getElementById(modalId);
                if (modal) {
                    const form = modal.querySelector('form');
                    if (form) {
                        this.setupModalForm(form, modal);
                    }
                }
            });
        });
    }

    // Setup modal forms
    setupModalForm(form, modal) {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        
        form.addEventListener('submit', (e) => {
            if (form.dataset.ajaxForm) {
                e.preventDefault();
                this.handleAjaxFormSubmit(e).then(() => {
                    if (form.classList.contains('submitted-successfully')) {
                        modalInstance.hide();
                    }
                });
            }
        });
        
        // Clear form when modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            form.reset();
            this.clearFormErrors(form);
            form.classList.remove('was-validated');
        });
    }

    // Setup quick entry forms
    setupQuickEntryForms() {
        const quickForms = document.querySelectorAll('[data-quick-entry]');
        quickForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleQuickEntry(form);
            });
        });
    }

    // Handle quick entry form
    async handleQuickEntry(form) {
        if (!this.validateForm(form)) return;
        
        this.showFormLoading(form);
        
        try {
            const formData = new FormData(form);
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.showFormSuccess(form, 'Entry added successfully!');
            form.reset();
            
            // Trigger data refresh
            if (window.expenseTracker) {
                window.expenseTracker.refreshData();
            }
        } catch (error) {
            this.showFormError(form, 'Failed to add entry');
        } finally {
            this.hideFormLoading(form);
        }
    }

    // Utility: Submit form data via AJAX
    async submitFormData(url, formData, method = 'POST') {
        // This is a simulation - replace with actual fetch call
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Form submitted successfully!'
                });
            }, 1500);
        });
        
        /* Actual implementation would be:
        const response = await fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        });
        return await response.json();
        */
    }

    // Utility: Get CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    // Utility: Check for duplicate category (simulated)
    isDuplicateCategory(categoryName) {
        const existingCategories = ['Food', 'Transport', 'Entertainment'];
        return existingCategories.includes(categoryName);
    }

    // Utility: Refresh data
    refreshData() {
        if (window.expenseTracker) {
            window.expenseTracker.refreshChartData();
        }
    }

    // Utility: Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.expenseForms = new ExpenseForms();
});

// Add enhanced form styles
const formStyles = `
.form-loading {
    position: relative;
    opacity: 0.7;
    pointer-events: none;
}

.form-loading::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    z-index: 1000;
}

.form-error-shake {
    animation: formShake 0.5s ease-in-out;
}

.field-error-shake {
    animation: fieldShake 0.3s ease-in-out;
}

@keyframes formShake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

@keyframes fieldShake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-3px); }
    75% { transform: translateX(3px); }
}

.auto-save-indicator {
    opacity: 0;
    transition: opacity 0.3s ease;
}

.auto-save-indicator.visible {
    opacity: 1;
}

.form-message {
    display: none;
}

.char-counter.text-warning {
    font-weight: bold;
}

.char-counter.text-danger {
    font-weight: bold;
    color: #dc3545 !important;
}

.form-step {
    transition: all 0.3s ease;
}

.form-step:not(.active) {
    display: none;
}

.form-progress {
    transition: width 0.3s ease;
}

.conditional-field {
    transition: all 0.3s ease;
}

.dynamic-field {
    position: relative;
    margin-bottom: 1rem;
    padding-right: 2.5rem;
}

.remove-field {
    position: absolute;
    right: 0;
    top: 0;
}

.form-floating.focused label {
    color: #4361ee;
    transform: scale(0.85) translateY(-0.5rem) translateX(0.15rem);
}

.quick-entry-form {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.quick-entry-form .form-control {
    border-radius: 6px;
}

@media (max-width: 768px) {
    .form-floating > label {
        font-size: 14px;
    }
    
    .quick-entry-form {
        padding: 1rem;
    }
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = formStyles;
document.head.appendChild(styleSheet);