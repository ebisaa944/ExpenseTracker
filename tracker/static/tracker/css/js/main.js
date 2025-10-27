/**
 * BudgetWise: Frontend Logic for Expense Tracker
 * Handles API calls, CSRF tokens, DOM manipulation, and summary calculations.
 */

const BudgetWise = (() => {
    // --- DOM Elements ---
    const elements = {
        form: document.getElementById('expense-form'),
        list: document.getElementById('transaction-list'),
        netBalance: document.getElementById('net-balance'),
        totalIncome: document.getElementById('total-income'),
        totalExpense: document.getElementById('total-expense'),
        messageBox: document.getElementById('message-box'),
        categorySelect: document.getElementById('category'),
        typeSelect: document.getElementById('type'),
    };

    // --- Configuration ---
    const API_URL = '/api/expenses/';
    const CATEGORIES = {
        INCOME: ['Salary', 'Investment', 'Gift', 'Other Income'],
        EXPENSE: ['Groceries', 'Rent', 'Utilities', 'Transport', 'Entertainment', 'Debt', 'Other Expense']
    };

    // --- Utility Functions ---

    // Retrieves the CSRF token from the Django cookie
    function getCsrfToken() {
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    return decodeURIComponent(cookie.substring(name.length + 1));
                }
            }
        }
        return null;
    }

    // Displays feedback messages to the user
    function displayMessage(text, type = 'error') {
        elements.messageBox.textContent = text;
        elements.messageBox.classList.remove('hidden', 'bg-red-100', 'bg-green-100', 'border-red-500', 'border-green-500', 'text-red-700', 'text-green-700');

        if (type === 'error') {
            elements.messageBox.classList.add('bg-red-100', 'border-red-500', 'text-red-700', 'border');
        } else if (type === 'success') {
            elements.messageBox.classList.add('bg-green-100', 'border-green-500', 'text-green-700', 'border');
        }
        
        setTimeout(() => elements.messageBox.classList.add('hidden'), 5000);
    }

    // Populates the Category dropdown based on the selected Type
    function populateCategories() {
        const type = elements.typeSelect.value;
        const currentCategories = CATEGORIES[type];

        elements.categorySelect.innerHTML = '';
        currentCategories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            elements.categorySelect.appendChild(option);
        });
    }

    // Formats a number as currency
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    }

    // --- API Calls ---

    // Fetches all expenses from the API
    async function fetchExpenses() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            renderTransactions(data);
            calculateSummary(data);
        } catch (error) {
            console.error("Error fetching expenses:", error);
            displayMessage("Failed to load transactions. Please check your API connection.", 'error');
        }
    }

    // Sends a new expense to the API
    async function addExpense(expense) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            displayMessage("CSRF token missing. Cannot submit transaction.", 'error');
            return;
        }

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(expense)
            });

            const responseData = await response.json();

            if (!response.ok) {
                // Display specific validation errors from Django
                const errorDetails = JSON.stringify(responseData);
                console.error("API Validation Error:", responseData);
                displayMessage(`Submission failed. Server error: ${errorDetails}`, 'error');
                return;
            }

            // Successfully added, refresh list
            displayMessage("Transaction added successfully!", 'success');
            elements.form.reset();
            fetchExpenses();

        } catch (error) {
            console.error("Error adding expense:", error);
            displayMessage("An unexpected error occurred while adding the transaction.", 'error');
        }
    }

    // Deletes an expense via the API
    async function deleteExpense(id) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            displayMessage("CSRF token missing. Cannot delete transaction.", 'error');
            return;
        }

        if (!confirm('Are you sure you want to delete this transaction?')) {
            return;
        }

        try {
            const response = await fetch(`${API_URL}${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.status === 204) { // 204 No Content is success for DELETE
                displayMessage("Transaction deleted successfully.", 'success');
                fetchExpenses();
            } else {
                displayMessage("Failed to delete transaction.", 'error');
            }

        } catch (error) {
            console.error("Error deleting expense:", error);
            displayMessage("An unexpected error occurred during deletion.", 'error');
        }
    }

    // --- Rendering and Calculations ---

    function calculateSummary(expenses) {
        let income = 0;
        let expense = 0;

        expenses.forEach(t => {
            // Note: DRF may return amount as string, ensure it's a number
            const amount = parseFloat(t.amount); 
            if (t.type === 'INCOME') {
                income += amount;
            } else if (t.type === 'EXPENSE') {
                expense += amount;
            }
        });

        const netBalance = income - expense;

        elements.totalIncome.textContent = formatCurrency(income);
        elements.totalExpense.textContent = formatCurrency(expense);
        
        elements.netBalance.textContent = formatCurrency(netBalance);
        elements.netBalance.classList.toggle('text-red-600', netBalance < 0);
        elements.netBalance.classList.toggle('text-green-600', netBalance >= 0);
    }

    function renderTransaction(transaction) {
        const isIncome = transaction.type === 'INCOME';
        const sign = isIncome ? '+' : '-';
        const amountClass = isIncome ? 'text-green-600' : 'text-red-600';

        const itemDiv = document.createElement('div');
        itemDiv.className = `transaction-item p-4 rounded-lg shadow-sm flex justify-between items-center bg-white ${isIncome ? 'income' : 'expense'}`;
        itemDiv.dataset.id = transaction.id;

        const date = new Date(transaction.date).toLocaleDateString();

        itemDiv.innerHTML = `
            <div class="flex-1 min-w-0">
                <p class="text-lg font-semibold text-gray-800 truncate">${transaction.title}</p>
                <p class="text-sm text-gray-500">${transaction.category} • ${date}</p>
            </div>
            <div class="text-right ml-4">
                <span class="text-lg font-bold ${amountClass}">
                    ${sign}${formatCurrency(transaction.amount)}
                </span>
            </div>
            <button class="delete-btn ml-4 text-gray-400 hover:text-red-500 transition duration-150" aria-label="Delete transaction">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                </svg>
            </button>
        `;

        const deleteButton = itemDiv.querySelector('.delete-btn');
        deleteButton.addEventListener('click', () => deleteExpense(transaction.id));

        return itemDiv;
    }

    function renderTransactions(transactions) {
        elements.list.innerHTML = ''; // Clear existing list

        if (transactions.length === 0) {
            elements.list.innerHTML = '<p class="text-gray-500 text-center py-4">No transactions recorded yet.</p>';
            return;
        }

        // Sort by date descending
        transactions.sort((a, b) => new Date(b.date) - new Date(a.date));

        transactions.forEach(transaction => {
            elements.list.appendChild(renderTransaction(transaction));
        });
    }

    // --- Event Handlers ---

    async function handleFormSubmit(event) {
        event.preventDefault();

        const data = new FormData(elements.form);
        const amount = parseFloat(data.get('amount'));

        if (isNaN(amount) || amount <= 0) {
            displayMessage("Please enter a valid amount.", 'error');
            return;
        }

        // Construct the expense object
        const newExpense = {
            title: data.get('title'), // Corrected to 'title' to match DRF field
            amount: amount,
            date: data.get('date'),
            type: data.get('type'),
            category: data.get('category'),
        };

        await addExpense(newExpense);
    }

    // --- Initialization ---

    function init() {
        // 1. Set the default date to today for convenience
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('date').value = today;

        // 2. Set up event listeners
        elements.form.addEventListener('submit', handleFormSubmit);
        elements.typeSelect.addEventListener('change', populateCategories);

        // 3. Initial population of categories and data load
        populateCategories();
        fetchExpenses();
    }

    return {
        init: init
    };

})();
