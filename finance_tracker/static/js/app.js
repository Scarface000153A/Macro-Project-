/**
 * FinTrack - Personal Finance & Attendance Tracker
 * Client-Side JavaScript Utilities and Chart Integrations
 */

// ==================== MODAL HELPERS ==================== //
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden"; // Prevent background scrolling
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

function closeModalOnOutsideClick(event, modalId) {
    if (event.target.id === modalId) {
        closeModal(modalId);
    }
}

// Close modal on Escape key press
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        document.querySelectorAll(".modal-backdrop.active").forEach((modal) => {
            closeModal(modal.id);
        });
    }
});

// ==================== PASSWORD VISIBILITY TOGGLE ==================== //
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector("i");
    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}

// ==================== FORM VALIDATION ==================== //
function validateRegisterForm() {
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    if (password.length < 6) {
        alert("Password must be at least 6 characters long.");
        return false;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match! Please check and try again.");
        return false;
    }
    return true;
}

// ==================== DOM READY INITIALIZATION ==================== //
document.addEventListener("DOMContentLoaded", () => {
    // 1. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // 2. Animate progress bars cleanly from data-progress attributes
    document.querySelectorAll(".progress-bar-fill[data-progress]").forEach((bar) => {
        const rawProgress = parseFloat(bar.getAttribute("data-progress")) || 0;
        const progress = Math.min(100, Math.max(0, rawProgress));
        bar.style.width = progress + "%";
    });

    // 3. Initialize Dashboard Charts from API (Zero Jinja in JS!)
    const analyticsEl = document.getElementById("dashboard-analytics");
    if (analyticsEl) {
        const totalIncome = parseFloat(analyticsEl.getAttribute("data-income")) || 0;
        const totalExpense = parseFloat(analyticsEl.getAttribute("data-expense")) || 0;
        const currency = analyticsEl.getAttribute("data-currency") || "₹";

        fetch("/api/chart-data")
            .then((res) => res.json())
            .then((data) => {
                const expenseLabels = data.expense.map((item) => item.category);
                const expenseData = data.expense.map((item) => item.total);
                initDashboardCharts(totalIncome, totalExpense, expenseLabels, expenseData, currency);
            })
            .catch((err) => {
                console.error("Error loading chart data:", err);
            });
    }
});

// ==================== DASHBOARD CHARTS (Chart.js) ==================== //
function initDashboardCharts(totalIncome, totalExpense, expenseLabels, expenseData, currencySymbol) {
    // 1. Expense Breakdown Doughnut Chart
    const expenseCtx = document.getElementById("expenseCategoryChart");
    if (expenseCtx && expenseLabels.length > 0) {
        const colorPalette = [
            "#ef4444", "#f97316", "#f59e0b", "#10b981", 
            "#06b6d4", "#3b82f6", "#6366f1", "#8b5cf6", 
            "#d946ef", "#64748b"
        ];

        new Chart(expenseCtx, {
            type: "doughnut",
            data: {
                labels: expenseLabels,
                datasets: [{
                    data: expenseData,
                    backgroundColor: colorPalette.slice(0, expenseLabels.length),
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
                            boxWidth: 14,
                            padding: 12
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || "";
                                const value = context.parsed || 0;
                                return ` ${label}: ${currencySymbol}${value.toFixed(2)}`;
                            }
                        }
                    }
                },
                cutout: "68%"
            }
        });
    }

    // 2. Cash Flow Comparison Bar Chart
    const cashFlowCtx = document.getElementById("cashFlowChart");
    if (cashFlowCtx && (totalIncome > 0 || totalExpense > 0)) {
        new Chart(cashFlowCtx, {
            type: "bar",
            data: {
                labels: ["Income (+)", "Expenses (-)"],
                datasets: [{
                    label: "Total Amount",
                    data: [totalIncome, totalExpense],
                    backgroundColor: [
                        "rgba(16, 185, 129, 0.85)", // Green for income
                        "rgba(239, 68, 68, 0.85)"   // Red for expense
                    ],
                    borderColor: [
                        "#10b981",
                        "#ef4444"
                    ],
                    borderWidth: 1.5,
                    borderRadius: 8,
                    maxBarThickness: 60
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` Total: ${currencySymbol}${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return currencySymbol + value.toLocaleString();
                            },
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 }
                        },
                        grid: {
                            color: "#f1f5f9"
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 600 }
                        }
                    }
                }
            }
        });
    }
}
