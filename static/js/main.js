/**
 * Graduate Tracker System - Main JavaScript File
 * Contains all interactive functionality and UI enhancements
 */

// ===== Global Variables =====
const GraduateTracker = {
    config: {
        animationDuration: 300,
        debounceDelay: 300,
        autoSaveInterval: 30000,
        notificationDuration: 5000
    },
    
    state: {
        currentUser: null,
        notifications: [],
        activeModals: [],
        formData: {}
    },
    
    utils: {},
    components: {},
    modules: {}
};

// ===== Utility Functions =====
GraduateTracker.utils = {
    /**
     * Debounce function to limit function calls
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function to limit function calls
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Format date to Arabic locale
     */
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        return new Date(date).toLocaleDateString('ar-SA', { ...defaultOptions, ...options });
    },

    /**
     * Format number to Arabic locale
     */
    formatNumber: function(number) {
        return new Intl.NumberFormat('ar-SA').format(number);
    },

    /**
     * Validate email format
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Validate phone number (Saudi format)
     */
    validatePhone: function(phone) {
        const re = /^(\+966|966|0)?5[0-9]{8}$/;
        return re.test(phone.replace(/\s/g, ''));
    },

    /**
     * Generate random ID
     */
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    },

    /**
     * Show loading state
     */
    showLoading: function(element) {
        element.classList.add('loading');
        element.disabled = true;
    },

    /**
     * Hide loading state
     */
    hideLoading: function(element) {
        element.classList.remove('loading');
        element.disabled = false;
    },

    /**
     * Smooth scroll to element
     */
    scrollTo: function(element, offset = 0) {
        const elementPosition = element.offsetTop - offset;
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    },

    /**
     * Copy text to clipboard
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        }
    }
};

// ===== Notification System =====
GraduateTracker.components.notifications = {
    container: null,

    init: function() {
        this.createContainer();
    },

    createContainer: function() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        }
    },

    show: function(message, type = 'info', duration = null) {
        const notification = document.createElement('div');
        const id = GraduateTracker.utils.generateId();
        
        notification.className = `alert alert-${type} alert-dismissible fade show notification-item`;
        notification.style.cssText = `
            margin-bottom: 10px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        const icon = this.getIcon(type);
        notification.innerHTML = `
            <i class="bi ${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.container.appendChild(notification);

        // Auto remove after duration
        const autoRemoveDuration = duration || GraduateTracker.config.notificationDuration;
        setTimeout(() => {
            this.remove(notification);
        }, autoRemoveDuration);

        return id;
    },

    getIcon: function(type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    },

    remove: function(notification) {
        if (notification && notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    },

    success: function(message, duration) {
        return this.show(message, 'success', duration);
    },

    error: function(message, duration) {
        return this.show(message, 'error', duration);
    },

    warning: function(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info: function(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// ===== Form Enhancement =====
GraduateTracker.components.forms = {
    init: function() {
        this.enhanceAllForms();
        this.setupValidation();
        this.setupAutoSave();
    },

    enhanceAllForms: function() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => this.enhanceForm(form));
    },

    enhanceForm: function(form) {
        // Add loading states to submit buttons
        const submitButtons = form.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            button.addEventListener('click', () => {
                setTimeout(() => {
                    if (form.checkValidity()) {
                        GraduateTracker.utils.showLoading(button);
                    }
                }, 100);
            });
        });

        // Enhanced input interactions
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            this.enhanceInput(input);
        });
    },

    enhanceInput: function(input) {
        // Add floating label effect
        if (input.type !== 'checkbox' && input.type !== 'radio') {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('input-focused');
            });

            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentElement.classList.remove('input-focused');
                }
            });

            // Check if input has value on load
            if (input.value) {
                input.parentElement.classList.add('input-focused');
            }
        }

        // Auto-format phone numbers
        if (input.type === 'tel' || input.name === 'phone') {
            input.addEventListener('input', this.formatPhoneNumber);
        }

        // Auto-format national ID
        if (input.name === 'national_id') {
            input.addEventListener('input', this.formatNationalId);
        }

        // Real-time validation
        input.addEventListener('blur', () => {
            this.validateInput(input);
        });
    },

    formatPhoneNumber: function(event) {
        let value = event.target.value.replace(/\D/g, '');
        
        if (value.startsWith('966')) {
            value = '+' + value;
        } else if (value.startsWith('05')) {
            value = '+966' + value.substring(1);
        } else if (value.startsWith('5') && value.length === 9) {
            value = '+966' + value;
        }
        
        event.target.value = value;
    },

    formatNationalId: function(event) {
        let value = event.target.value.replace(/\D/g, '');
        if (value.length > 10) {
            value = value.substring(0, 10);
        }
        event.target.value = value;
    },

    validateInput: function(input) {
        const value = input.value.trim();
        let isValid = true;
        let message = '';

        // Required field validation
        if (input.required && !value) {
            isValid = false;
            message = 'هذا الحقل مطلوب';
        }

        // Email validation
        if (input.type === 'email' && value && !GraduateTracker.utils.validateEmail(value)) {
            isValid = false;
            message = 'يرجى إدخال بريد إلكتروني صحيح';
        }

        // Phone validation
        if ((input.type === 'tel' || input.name === 'phone') && value && !GraduateTracker.utils.validatePhone(value)) {
            isValid = false;
            message = 'يرجى إدخال رقم هاتف صحيح';
        }

        // National ID validation
        if (input.name === 'national_id' && value && value.length !== 10) {
            isValid = false;
            message = 'رقم الهوية يجب أن يكون 10 أرقام';
        }

        // Update UI
        this.updateInputValidation(input, isValid, message);
        return isValid;
    },

    updateInputValidation: function(input, isValid, message) {
        const feedbackElement = input.parentElement.querySelector('.invalid-feedback') || 
                               input.parentElement.querySelector('.valid-feedback');

        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.textContent = '';
                feedbackElement.style.display = 'none';
            }
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.textContent = message;
                feedbackElement.style.display = 'block';
            } else {
                // Create feedback element
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                feedback.style.display = 'block';
                input.parentElement.appendChild(feedback);
            }
        }
    },

    setupValidation: function() {
        const forms = document.querySelectorAll('form[novalidate]');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                event.stopPropagation();

                const inputs = form.querySelectorAll('input, textarea, select');
                let isFormValid = true;

                inputs.forEach(input => {
                    if (!this.validateInput(input)) {
                        isFormValid = false;
                    }
                });

                if (isFormValid) {
                    form.submit();
                } else {
                    GraduateTracker.components.notifications.error('يرجى تصحيح الأخطاء في النموذج');
                    
                    // Scroll to first invalid input
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        GraduateTracker.utils.scrollTo(firstInvalid, 100);
                        firstInvalid.focus();
                    }
                }
            });
        });
    },

    setupAutoSave: function() {
        const forms = document.querySelectorAll('form[data-autosave]');
        forms.forEach(form => {
            const formId = form.getAttribute('data-autosave');
            const inputs = form.querySelectorAll('input, textarea, select');

            // Load saved data
            this.loadFormData(form, formId);

            // Save on input change
            const debouncedSave = GraduateTracker.utils.debounce(() => {
                this.saveFormData(form, formId);
            }, 1000);

            inputs.forEach(input => {
                input.addEventListener('input', debouncedSave);
                input.addEventListener('change', debouncedSave);
            });
        });
    },

    saveFormData: function(form, formId) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }

        localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    },

    loadFormData: function(form, formId) {
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const inputs = form.querySelectorAll(`[name="${key}"]`);
                    inputs.forEach(input => {
                        if (input.type === 'radio' || input.type === 'checkbox') {
                            if (Array.isArray(data[key])) {
                                input.checked = data[key].includes(input.value);
                            } else {
                                input.checked = input.value === data[key];
                            }
                        } else {
                            input.value = data[key];
                        }
                    });
                });
            } catch (e) {
                console.warn('Could not load saved form data:', e);
            }
        }
    },

    clearFormData: function(formId) {
        localStorage.removeItem(`form_${formId}`);
    }
};

// ===== Table Enhancement =====
GraduateTracker.components.tables = {
    init: function() {
        this.enhanceAllTables();
        this.setupBulkActions();
    },

    enhanceAllTables: function() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => this.enhanceTable(table));
    },

    enhanceTable: function(table) {
        // Add hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.transform = 'scale(1.01)';
                row.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
            });

            row.addEventListener('mouseleave', () => {
                row.style.transform = '';
                row.style.boxShadow = '';
            });
        });

        // Setup sorting if headers are clickable
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
        });
    },

    sortTable: function(table, header) {
        const column = header.getAttribute('data-sort');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAscending = header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aValue = a.querySelector(`[data-value="${column}"]`)?.textContent || 
                          a.cells[header.cellIndex]?.textContent || '';
            const bValue = b.querySelector(`[data-value="${column}"]`)?.textContent || 
                          b.cells[header.cellIndex]?.textContent || '';

            if (isAscending) {
                return bValue.localeCompare(aValue, 'ar');
            } else {
                return aValue.localeCompare(bValue, 'ar');
            }
        });

        // Update DOM
        rows.forEach(row => tbody.appendChild(row));

        // Update sort indicators
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
    },

    setupBulkActions: function() {
        const selectAllCheckboxes = document.querySelectorAll('#selectAll');
        selectAllCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (event) => {
                const table = event.target.closest('table') || 
                             event.target.closest('.card').querySelector('table');
                if (table) {
                    const itemCheckboxes = table.querySelectorAll('.item-checkbox, .graduate-checkbox');
                    itemCheckboxes.forEach(itemCheckbox => {
                        itemCheckbox.checked = event.target.checked;
                    });
                    this.updateBulkActionUI();
                }
            });
        });

        const itemCheckboxes = document.querySelectorAll('.item-checkbox, .graduate-checkbox');
        itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionUI();
                this.updateSelectAllState();
            });
        });
    },

    updateBulkActionUI: function() {
        const checkedItems = document.querySelectorAll('.item-checkbox:checked, .graduate-checkbox:checked');
        const bulkActionElements = document.querySelectorAll('[data-bulk-action]');
        const selectedCountElements = document.querySelectorAll('#selectedCount, .selected-count');

        bulkActionElements.forEach(element => {
            element.style.display = checkedItems.length > 0 ? 'block' : 'none';
        });

        selectedCountElements.forEach(element => {
            if (checkedItems.length === 0) {
                element.textContent = 'لم يتم تحديد أي عنصر';
            } else {
                element.textContent = `تم تحديد ${checkedItems.length} عنصر`;
            }
        });
    },

    updateSelectAllState: function() {
        const selectAllCheckboxes = document.querySelectorAll('#selectAll');
        selectAllCheckboxes.forEach(selectAll => {
            const table = selectAll.closest('table') || 
                         selectAll.closest('.card').querySelector('table');
            if (table) {
                const itemCheckboxes = table.querySelectorAll('.item-checkbox, .graduate-checkbox');
                const checkedItems = table.querySelectorAll('.item-checkbox:checked, .graduate-checkbox:checked');

                if (checkedItems.length === 0) {
                    selectAll.checked = false;
                    selectAll.indeterminate = false;
                } else if (checkedItems.length === itemCheckboxes.length) {
                    selectAll.checked = true;
                    selectAll.indeterminate = false;
                } else {
                    selectAll.checked = false;
                    selectAll.indeterminate = true;
                }
            }
        });
    }
};

// ===== Survey Module =====
GraduateTracker.modules.survey = {
    currentQuestion: 0,
    totalQuestions: 0,
    responses: {},

    init: function() {
        this.setupSurveyForm();
        this.setupProgressTracking();
        this.setupQuestionNavigation();
    },

    setupSurveyForm: function() {
        const surveyForm = document.getElementById('surveyResponseForm');
        if (!surveyForm) return;

        this.totalQuestions = surveyForm.querySelectorAll('.question-card').length;
        
        // Setup question interactions
        const questionCards = surveyForm.querySelectorAll('.question-card');
        questionCards.forEach((card, index) => {
            this.setupQuestionCard(card, index);
        });

        // Setup form submission
        surveyForm.addEventListener('submit', (event) => {
            this.handleSurveySubmission(event);
        });
    },

    setupQuestionCard: function(card, index) {
        const inputs = card.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                this.updateProgress();
                this.saveResponse(input);
                this.animateQuestionCompletion(card);
            });

            input.addEventListener('input', GraduateTracker.utils.debounce(() => {
                this.saveResponse(input);
            }, 500));
        });
    },

    setupProgressTracking: function() {
        this.updateProgress();
    },

    updateProgress: function() {
        const progressBar = document.querySelector('.progress-bar');
        const progressPercentage = document.querySelector('.progress-percentage');
        
        if (!progressBar || !progressPercentage) return;

        const questionCards = document.querySelectorAll('.question-card');
        let answeredQuestions = 0;

        questionCards.forEach(card => {
            const inputs = card.querySelectorAll('input[type="radio"]:checked, input[type="checkbox"]:checked, textarea:not(:empty), input[type="email"]:not(:empty), input[type="tel"]:not(:empty)');
            if (inputs.length > 0) {
                answeredQuestions++;
            }
        });

        const percentage = Math.round((answeredQuestions / this.totalQuestions) * 100);
        
        progressBar.style.width = percentage + '%';
        progressPercentage.textContent = percentage + '%';

        // Add completion animation
        if (percentage === 100) {
            progressBar.classList.add('bg-success');
            setTimeout(() => {
                GraduateTracker.components.notifications.success('تم إكمال جميع الأسئلة!');
            }, 500);
        }
    },

    saveResponse: function(input) {
        const questionCard = input.closest('.question-card');
        const questionNumber = questionCard.getAttribute('data-question');
        
        if (!this.responses[questionNumber]) {
            this.responses[questionNumber] = {};
        }

        if (input.type === 'radio') {
            this.responses[questionNumber][input.name] = input.value;
        } else if (input.type === 'checkbox') {
            if (!this.responses[questionNumber][input.name]) {
                this.responses[questionNumber][input.name] = [];
            }
            if (input.checked) {
                this.responses[questionNumber][input.name].push(input.value);
            } else {
                const index = this.responses[questionNumber][input.name].indexOf(input.value);
                if (index > -1) {
                    this.responses[questionNumber][input.name].splice(index, 1);
                }
            }
        } else {
            this.responses[questionNumber][input.name] = input.value;
        }

        // Save to localStorage
        localStorage.setItem('survey_responses', JSON.stringify(this.responses));
    },

    animateQuestionCompletion: function(card) {
        card.style.borderColor = '#28a745';
        setTimeout(() => {
            card.style.borderColor = '';
        }, 1000);
    },

    setupQuestionNavigation: function() {
        // Add next/previous buttons if needed
        const questionCards = document.querySelectorAll('.question-card');
        questionCards.forEach((card, index) => {
            if (index < questionCards.length - 1) {
                const nextButton = document.createElement('button');
                nextButton.type = 'button';
                nextButton.className = 'btn btn-outline-primary btn-sm mt-3';
                nextButton.innerHTML = '<i class="bi bi-arrow-down me-1"></i> السؤال التالي';
                nextButton.addEventListener('click', () => {
                    const nextCard = questionCards[index + 1];
                    GraduateTracker.utils.scrollTo(nextCard, 100);
                });
                card.querySelector('.card-body').appendChild(nextButton);
            }
        });
    },

    handleSurveySubmission: function(event) {
        const form = event.target;
        const requiredInputs = form.querySelectorAll('input[required]');
        let isValid = true;

        requiredInputs.forEach(input => {
            const name = input.name;
            const checked = form.querySelector(`input[name="${name}"]:checked`);
            
            if (!checked) {
                isValid = false;
                const questionCard = input.closest('.question-card');
                if (questionCard) {
                    questionCard.style.borderColor = '#dc3545';
                    questionCard.style.animation = 'shake 0.5s ease-in-out';
                }
            }
        });

        if (!isValid) {
            event.preventDefault();
            GraduateTracker.components.notifications.error('يرجى الإجابة على جميع الأسئلة المطلوبة');
            
            // Scroll to first unanswered question
            const firstInvalid = form.querySelector('.question-card[style*="border-color: rgb(220, 53, 69)"]');
            if (firstInvalid) {
                GraduateTracker.utils.scrollTo(firstInvalid, 100);
            }
        } else {
            // Clear saved responses on successful submission
            localStorage.removeItem('survey_responses');
            GraduateTracker.components.notifications.success('تم إرسال الاستبيان بنجاح!');
        }
    }
};

// ===== Dashboard Module =====
GraduateTracker.modules.dashboard = {
    charts: {},
    refreshInterval: null,

    init: function() {
        this.setupCharts();
        this.setupRealTimeUpdates();
        this.setupQuickActions();
    },

    setupCharts: function() {
        // Setup Chart.js charts if available
        if (typeof Chart !== 'undefined') {
            this.createStatisticsChart();
            this.createTrendsChart();
        }
    },

    createStatisticsChart: function() {
        const ctx = document.getElementById('statisticsChart');
        if (!ctx) return;

        this.charts.statistics = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['موظفون', 'غير موظفين', 'عمل حر', 'يدرسون'],
                datasets: [{
                    data: [65, 20, 10, 5],
                    backgroundColor: [
                        '#28a745',
                        '#dc3545',
                        '#ffc107',
                        '#17a2b8'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                family: 'Segoe UI'
                            }
                        }
                    }
                }
            }
        });
    },

    createTrendsChart: function() {
        const ctx = document.getElementById('trendsChart');
        if (!ctx) return;

        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [{
                    label: 'معدل التوظيف',
                    data: [65, 68, 70, 72, 75, 78],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    },

    setupRealTimeUpdates: function() {
        // Update dashboard stats every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.updateStats();
        }, 30000);
    },

    updateStats: function() {
        // Simulate real-time updates
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            const currentValue = parseInt(stat.textContent);
            const newValue = currentValue + Math.floor(Math.random() * 3);
            this.animateNumber(stat, currentValue, newValue);
        });
    },

    animateNumber: function(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = GraduateTracker.utils.formatNumber(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },

    setupQuickActions: function() {
        const quickActionButtons = document.querySelectorAll('[data-quick-action]');
        quickActionButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const action = event.target.getAttribute('data-quick-action');
                this.handleQuickAction(action);
            });
        });
    },

    handleQuickAction: function(action) {
        switch (action) {
            case 'export-data':
                this.exportData();
                break;
            case 'send-survey':
                this.showSendSurveyModal();
                break;
            case 'generate-report':
                this.generateReport();
                break;
            default:
                console.log('Unknown quick action:', action);
        }
    },

    exportData: function() {
        GraduateTracker.components.notifications.info('جاري تصدير البيانات...');
        // Simulate export process
        setTimeout(() => {
            GraduateTracker.components.notifications.success('تم تصدير البيانات بنجاح');
        }, 2000);
    },

    showSendSurveyModal: function() {
        // Implementation for survey sending modal
        GraduateTracker.components.notifications.info('فتح نافذة إرسال الاستبيان...');
    },

    generateReport: function() {
        GraduateTracker.components.notifications.info('جاري إنشاء التقرير...');
        // Simulate report generation
        setTimeout(() => {
            GraduateTracker.components.notifications.success('تم إنشاء التقرير بنجاح');
        }, 3000);
    }
};

// ===== Search and Filter Module =====
GraduateTracker.modules.search = {
    init: function() {
        this.setupSearchInputs();
        this.setupFilters();
        this.setupAdvancedSearch();
    },

    setupSearchInputs: function() {
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            const debouncedSearch = GraduateTracker.utils.debounce((event) => {
                this.performSearch(event.target);
            }, 300);

            input.addEventListener('input', debouncedSearch);
        });
    },

    performSearch: function(input) {
        const searchTerm = input.value.toLowerCase();
        const targetSelector = input.getAttribute('data-search');
        const targets = document.querySelectorAll(targetSelector);

        targets.forEach(target => {
            const text = target.textContent.toLowerCase();
            const shouldShow = text.includes(searchTerm);
            
            target.style.display = shouldShow ? '' : 'none';
            
            // Add highlight effect
            if (shouldShow && searchTerm) {
                this.highlightText(target, searchTerm);
            } else {
                this.removeHighlight(target);
            }
        });

        this.updateSearchResults(targets, searchTerm);
    },

    highlightText: function(element, searchTerm) {
        // Simple text highlighting
        const text = element.textContent;
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        const highlightedText = text.replace(regex, '<mark>$1</mark>');
        
        if (element.innerHTML !== highlightedText) {
            element.innerHTML = highlightedText;
        }
    },

    removeHighlight: function(element) {
        const marks = element.querySelectorAll('mark');
        marks.forEach(mark => {
            mark.outerHTML = mark.innerHTML;
        });
    },

    updateSearchResults: function(targets, searchTerm) {
        const visibleTargets = Array.from(targets).filter(target => 
            target.style.display !== 'none'
        );

        const resultCountElement = document.querySelector('.search-results-count');
        if (resultCountElement) {
            if (searchTerm) {
                resultCountElement.textContent = `تم العثور على ${visibleTargets.length} نتيجة`;
                resultCountElement.style.display = 'block';
            } else {
                resultCountElement.style.display = 'none';
            }
        }
    },

    setupFilters: function() {
        const filterSelects = document.querySelectorAll('[data-filter]');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.applyFilters();
            });
        });
    },

    applyFilters: function() {
        const filters = {};
        const filterSelects = document.querySelectorAll('[data-filter]');
        
        filterSelects.forEach(select => {
            const filterType = select.getAttribute('data-filter');
            const filterValue = select.value;
            if (filterValue) {
                filters[filterType] = filterValue;
            }
        });

        this.filterResults(filters);
    },

    filterResults: function(filters) {
        const items = document.querySelectorAll('[data-filterable]');
        
        items.forEach(item => {
            let shouldShow = true;
            
            Object.keys(filters).forEach(filterType => {
                const itemValue = item.getAttribute(`data-${filterType}`);
                if (itemValue && itemValue !== filters[filterType]) {
                    shouldShow = false;
                }
            });
            
            item.style.display = shouldShow ? '' : 'none';
        });
    },

    setupAdvancedSearch: function() {
        const advancedSearchToggle = document.querySelector('#advancedSearchToggle');
        const advancedSearchPanel = document.querySelector('#advancedSearchPanel');
        
        if (advancedSearchToggle && advancedSearchPanel) {
            advancedSearchToggle.addEventListener('click', () => {
                const isVisible = advancedSearchPanel.style.display !== 'none';
                advancedSearchPanel.style.display = isVisible ? 'none' : 'block';
                
                if (!isVisible) {
                    advancedSearchPanel.style.animation = 'fadeInUp 0.3s ease-out';
                }
            });
        }
    }
};

// ===== Animation and UI Effects =====
GraduateTracker.components.animations = {
    init: function() {
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupLoadingAnimations();
    },

    setupScrollAnimations: function() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        const animatedElements = document.querySelectorAll('[data-animate]');
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    },

    setupHoverEffects: function() {
        const hoverElements = document.querySelectorAll('[data-hover]');
        hoverElements.forEach(element => {
            const hoverEffect = element.getAttribute('data-hover');
            
            element.addEventListener('mouseenter', () => {
                this.applyHoverEffect(element, hoverEffect);
            });
            
            element.addEventListener('mouseleave', () => {
                this.removeHoverEffect(element, hoverEffect);
            });
        });
    },

    applyHoverEffect: function(element, effect) {
        switch (effect) {
            case 'lift':
                element.style.transform = 'translateY(-5px)';
                element.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
                break;
            case 'scale':
                element.style.transform = 'scale(1.05)';
                break;
            case 'glow':
                element.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.5)';
                break;
        }
    },

    removeHoverEffect: function(element, effect) {
        element.style.transform = '';
        element.style.boxShadow = '';
    },

    setupLoadingAnimations: function() {
        // Add CSS for loading animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
            
            .animate-in {
                animation: fadeInUp 0.6s ease-out;
            }
        `;
        document.head.appendChild(style);
    }
};

// ===== Accessibility Module =====
GraduateTracker.modules.accessibility = {
    init: function() {
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupFocusManagement();
    },

    setupKeyboardNavigation: function() {
        // Add keyboard support for custom components
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeModals();
                this.clearFocus();
            }
            
            if (event.key === 'Tab') {
                this.manageFocusOrder(event);
            }
        });
    },

    setupScreenReaderSupport: function() {
        // Add ARIA labels and descriptions
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
        interactiveElements.forEach(element => {
            if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
                const text = element.textContent || element.value || element.placeholder;
                if (text) {
                    element.setAttribute('aria-label', text.trim());
                }
            }
        });
    },

    setupFocusManagement: function() {
        // Ensure proper focus management for dynamic content
        const dynamicContainers = document.querySelectorAll('[data-dynamic]');
        dynamicContainers.forEach(container => {
            const observer = new MutationObserver(() => {
                this.updateFocusableElements(container);
            });
            
            observer.observe(container, {
                childList: true,
                subtree: true
            });
        });
    },

    updateFocusableElements: function(container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        focusableElements.forEach((element, index) => {
            element.setAttribute('tabindex', index === 0 ? '0' : '-1');
        });
    },

    closeModals: function() {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const closeButton = modal.querySelector('[data-bs-dismiss="modal"]');
            if (closeButton) {
                closeButton.click();
            }
        });
    },

    clearFocus: function() {
        if (document.activeElement) {
            document.activeElement.blur();
        }
    },

    manageFocusOrder: function(event) {
        // Custom focus management for complex layouts
        const focusableElements = document.querySelectorAll(
            'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        const currentIndex = Array.from(focusableElements).indexOf(document.activeElement);
        
        if (event.shiftKey) {
            // Shift + Tab (backward)
            if (currentIndex === 0) {
                event.preventDefault();
                focusableElements[focusableElements.length - 1].focus();
            }
        } else {
            // Tab (forward)
            if (currentIndex === focusableElements.length - 1) {
                event.preventDefault();
                focusableElements[0].focus();
            }
        }
    }
};

// ===== Main Initialization =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components and modules
    GraduateTracker.components.notifications.init();
    GraduateTracker.components.forms.init();
    GraduateTracker.components.tables.init();
    GraduateTracker.components.animations.init();
    
    GraduateTracker.modules.survey.init();
    GraduateTracker.modules.dashboard.init();
    GraduateTracker.modules.search.init();
    GraduateTracker.modules.accessibility.init();

    // Show welcome notification
    setTimeout(() => {
        GraduateTracker.components.notifications.success('مرحباً بك في نظام تتبع الخريجين!', 3000);
    }, 1000);

    // Setup global error handling
    window.addEventListener('error', (event) => {
        console.error('JavaScript Error:', event.error);
        GraduateTracker.components.notifications.error('حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.');
    });

    // Setup service worker for offline support (if available)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('Service Worker registered successfully');
            })
            .catch(error => {
                console.log('Service Worker registration failed');
            });
    }

    console.log('Graduate Tracker System initialized successfully');
});

// ===== Export for global access =====
window.GraduateTracker = GraduateTracker;

