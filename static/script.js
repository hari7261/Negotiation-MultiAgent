document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('negotiationForm');
    const negotiationResults = document.getElementById('negotiationResults');
    const negotiationStatus = document.getElementById('negotiationStatus');
    const negotiationSummary = document.getElementById('negotiationSummary');
    const negotiationRounds = document.getElementById('negotiationRounds');
    const negotiationAnalysis = document.getElementById('negotiationAnalysis');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const startBtn = document.getElementById('startBtn');
    
    let currentNegotiation = null;
    let loadingOverlay = null;
    let currentStep = 0;
    
    // Create loading overlay
    function createLoadingOverlay() {
        loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Initializing Negotiation...</div>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div class="loading-steps">
                <div class="loading-step" data-step="0">
                    <div class="step-icon"></div>
                    <span>Setting up agents</span>
                </div>
                <div class="loading-step" data-step="1">
                    <div class="step-icon"></div>
                    <span>Initializing parameters</span>
                </div>
                <div class="loading-step" data-step="2">
                    <div class="step-icon"></div>
                    <span>Starting negotiation rounds</span>
                </div>
                <div class="loading-step" data-step="3">
                    <div class="step-icon"></div>
                    <span>Analyzing strategies</span>
                </div>
                <div class="loading-step" data-step="4">
                    <div class="step-icon"></div>
                    <span>Finalizing results</span>
                </div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }
    
    // Show loading with progress simulation
    function showLoading() {
        if (!loadingOverlay) createLoadingOverlay();
        
        loadingOverlay.classList.add('active');
        currentStep = 0;
        
        const steps = [
            { text: "Setting up intelligent agents...", duration: 800 },
            { text: "Configuring negotiation parameters...", duration: 600 },
            { text: "Initiating multi-round negotiations...", duration: 1200 },
            { text: "Analyzing strategic patterns...", duration: 900 },
            { text: "Generating comprehensive report...", duration: 700 }
        ];
        
        const progressFill = loadingOverlay.querySelector('.progress-fill');
        const loadingText = loadingOverlay.querySelector('.loading-text');
        const stepElements = loadingOverlay.querySelectorAll('.loading-step');
        
        function updateStep() {
            if (currentStep < steps.length) {
                // Update text
                loadingText.textContent = steps[currentStep].text;
                
                // Update progress
                const progress = ((currentStep + 1) / steps.length) * 100;
                progressFill.style.width = `${progress}%`;
                
                // Update step indicators
                stepElements.forEach((step, index) => {
                    step.classList.remove('active', 'completed');
                    if (index < currentStep) {
                        step.classList.add('completed');
                    } else if (index === currentStep) {
                        step.classList.add('active');
                    }
                });
                
                currentStep++;
                setTimeout(updateStep, steps[currentStep - 1]?.duration || 500);
            }
        }
        
        updateStep();
    }
    
    // Hide loading
    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
            setTimeout(() => {
                if (loadingOverlay && loadingOverlay.parentNode) {
                    loadingOverlay.parentNode.removeChild(loadingOverlay);
                    loadingOverlay = null;
                }
            }, 300);
        }
    }
    
    // Add input animations and validation
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentNode.classList.remove('focused');
            if (this.value) {
                this.parentNode.classList.add('filled');
            } else {
                this.parentNode.classList.remove('filled');
            }
        });
        
        // Real-time validation
        input.addEventListener('input', function() {
            if (this.type === 'number') {
                const value = parseFloat(this.value);
                if (value < 0) {
                    this.setCustomValidity('Price cannot be negative');
                } else {
                    this.setCustomValidity('');
                }
            }
        });
    });
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const item = document.getElementById('item').value.trim();
        const buyerMax = parseFloat(document.getElementById('buyerMax').value);
        const sellerMin = parseFloat(document.getElementById('sellerMin').value);
        
        // Enhanced validation
        if (!item) {
            showNotification('Please enter an item name', 'error');
            return;
        }
        
        if (isNaN(buyerMax) || isNaN(sellerMin)) {
            showNotification('Please enter valid prices', 'error');
            return;
        }
        
        if (sellerMin > buyerMax) {
            showNotification('Seller minimum price cannot be higher than buyer maximum price!', 'error');
            return;
        }
        
        if (buyerMax <= 0 || sellerMin <= 0) {
            showNotification('Prices must be positive values', 'error');
            return;
        }
        
        // Show loading state
        showLoading();
        startBtn.textContent = 'Negotiating...';
        startBtn.disabled = true;
        startBtn.classList.add('loading');
        
        try {
            const response = await fetch('/start_auto_negotiation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    item,
                    buyer_max: buyerMax,
                    seller_min: sellerMin
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                showNotification(`Error: ${error.error}`, 'error');
                return;
            }
            
            currentNegotiation = await response.json();
            
            // Simulate processing time for better UX
            setTimeout(() => {
                hideLoading();
                displayNegotiationResults();
                showNotification('Negotiation completed successfully!', 'success');
            }, 1000);
            
        } catch (error) {
            console.error('Error starting negotiation:', error);
            hideLoading();
            showNotification('Error starting negotiation. Please check your connection.', 'error');
        } finally {
            setTimeout(() => {
                startBtn.textContent = 'Start Automatic Negotiation';
                startBtn.disabled = false;
                startBtn.classList.remove('loading');
            }, 1000);
        }
    });
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentNode.parentNode.remove()">×</button>
            </div>
        `;
        
        // Add notification styles if not exists
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    max-width: 400px;
                    padding: 1rem;
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-lg);
                    z-index: 1001;
                    animation: slideInRight 0.3s ease-out;
                    backdrop-filter: blur(10px);
                }
                .notification.success {
                    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                    border: 1px solid #86efac;
                    color: #065f46;
                }
                .notification.error {
                    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                    border: 1px solid #fca5a5;
                    color: #991b1b;
                }
                .notification.info {
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    border: 1px solid #93c5fd;
                    color: #1e40af;
                }
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }
                .notification-icon {
                    font-size: 1.25rem;
                }
                .notification-message {
                    flex: 1;
                    font-weight: 500;
                }
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 1.25rem;
                    cursor: pointer;
                    padding: 0;
                    color: inherit;
                    opacity: 0.7;
                }
                .notification-close:hover {
                    opacity: 1;
                }
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
    
    function getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            info: 'ℹ️',
            warning: '⚠️'
        };
        return icons[type] || icons.info;
    }
    
    downloadPdfBtn.addEventListener('click', async () => {
        if (!currentNegotiation) return;
        
        downloadPdfBtn.textContent = 'Generating PDF...';
        downloadPdfBtn.disabled = true;
        downloadPdfBtn.classList.add('loading');
        
        try {
            const response = await fetch('/generate_pdf_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    negotiation: currentNegotiation
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `negotiation_report_${currentNegotiation.item.replace(/\s+/g, '_')}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showNotification('PDF report downloaded successfully!', 'success');
            } else {
                showNotification('Error generating PDF report', 'error');
            }
        } catch (error) {
            console.error('Error downloading PDF:', error);
            showNotification('Error downloading PDF report', 'error');
        } finally {
            downloadPdfBtn.textContent = 'Download PDF Report';
            downloadPdfBtn.disabled = false;
            downloadPdfBtn.classList.remove('loading');
        }
    });
    
    function displayNegotiationResults() {
        // Show results section with animation
        negotiationResults.classList.remove('hidden');
        
        // Display status with enhanced styling
        const statusClass = currentNegotiation.status === 'agreed' ? 'success' : 'failed';
        const statusIcon = currentNegotiation.status === 'agreed' ? '🎉' : '💔';
        negotiationStatus.innerHTML = `
            <div class="status-banner ${statusClass}">
                <h3>${statusIcon} Negotiation ${currentNegotiation.status === 'agreed' ? 'Successful!' : 'Failed'}</h3>
                ${currentNegotiation.status === 'agreed' ? 
                    `<p>Deal agreed at <strong>$${currentNegotiation.final_price.toFixed(2)}</strong></p>
                     <p>Savings: $${Math.abs(currentNegotiation.final_price - ((parseFloat(document.getElementById('buyerMax').value) + parseFloat(document.getElementById('sellerMin').value)) / 2)).toFixed(2)} from average price</p>` : 
                    `<p>${currentNegotiation.reason || 'No agreement reached between parties'}</p>`}
            </div>
        `;
        
        // Display enhanced summary
        negotiationSummary.innerHTML = `
            <div class="summary-section">
                <h3>📊 Executive Summary</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <strong>Item:</strong> ${currentNegotiation.item || 'N/A'}
                    </div>
                    <div class="summary-item">
                        <strong>Buyer Max:</strong> $${parseFloat(document.getElementById('buyerMax').value).toFixed(2)}
                    </div>
                    <div class="summary-item">
                        <strong>Seller Min:</strong> $${parseFloat(document.getElementById('sellerMin').value).toFixed(2)}
                    </div>
                    <div class="summary-item">
                        <strong>Negotiation Range:</strong> $${(parseFloat(document.getElementById('buyerMax').value) - parseFloat(document.getElementById('sellerMin').value)).toFixed(2)}
                    </div>
                    <div class="summary-item">
                        <strong>Total Rounds:</strong> ${currentNegotiation.rounds ? currentNegotiation.rounds.length : 0}
                    </div>
                    <div class="summary-item">
                        <strong>Duration:</strong> ~${Math.max(1, Math.floor(currentNegotiation.rounds?.length * 0.5) || 1)} minutes
                    </div>
                </div>
                <p class="summary-description">${currentNegotiation.summary || 'The negotiation involved strategic back-and-forth between intelligent agents representing buyer and seller interests, with a mediator facilitating fair resolution.'}</p>
            </div>
        `;
        
        // Display rounds with enhanced animations
        let roundsHtml = '<div class="rounds-section"><h3>🔄 Negotiation Timeline</h3>';
        if (currentNegotiation.rounds && currentNegotiation.rounds.length > 0) {
            currentNegotiation.rounds.forEach((round, index) => {
                const agentClass = round.agent;
                const agentIcon = getAgentIcon(round.agent);
                const delay = index * 100; // Stagger animations
                
                roundsHtml += `
                    <div class="round-item ${agentClass}" style="animation-delay: ${delay}ms;">
                        <div class="round-header">
                            <span class="round-number">Round ${round.round}</span>
                            <span class="agent-name">${agentIcon} ${round.agent.charAt(0).toUpperCase() + round.agent.slice(1)}</span>
                            ${round.price ? `<span class="price">$${round.price.toFixed(2)}</span>` : ''}
                        </div>
                        <div class="round-message">${round.message}</div>
                        ${round.strategy ? `<div class="round-strategy"><em>Strategy: ${round.strategy}</em></div>` : ''}
                    </div>
                `;
            });
        } else {
            roundsHtml += '<p class="no-rounds">No negotiation rounds recorded.</p>';
        }
        roundsHtml += '</div>';
        negotiationRounds.innerHTML = roundsHtml;
        
        // Display enhanced analysis
        negotiationAnalysis.innerHTML = `
            <div class="analysis-section">
                <h3>🧠 Strategic Analysis</h3>
                <div class="analysis-content">
                    <p>${currentNegotiation.analysis || 'This negotiation demonstrated typical market dynamics with both parties employing strategic positioning to achieve favorable outcomes. The AI agents utilized advanced negotiation tactics including anchoring, concession patterns, and deadline pressure.'}</p>
                    
                    <div class="analysis-metrics">
                        <div class="metric">
                            <span class="metric-label">Negotiation Efficiency:</span>
                            <span class="metric-value">${calculateEfficiency()}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Fair Value Index:</span>
                            <span class="metric-value">${calculateFairness()}/10</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Complexity Score:</span>
                            <span class="metric-value">${calculateComplexity()}/10</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Show download button with animation
        downloadPdfBtn.classList.remove('hidden');
        
        // Smooth scroll to results
        setTimeout(() => {
            negotiationResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 500);
        
        // Add extra CSS for new elements
        addAnalysisStyles();
    }
    
    function getAgentIcon(agent) {
        const icons = {
            buyer: '🛒',
            seller: '🏪',
            mediator: '⚖️'
        };
        return icons[agent] || '🤖';
    }
    
    function calculateEfficiency() {
        if (!currentNegotiation.rounds) return 85;
        const rounds = currentNegotiation.rounds.length;
        return Math.max(60, Math.min(100, 100 - (rounds * 5)));
    }
    
    function calculateFairness() {
        if (!currentNegotiation.final_price) return 7;
        const buyerMax = parseFloat(document.getElementById('buyerMax').value);
        const sellerMin = parseFloat(document.getElementById('sellerMin').value);
        const midpoint = (buyerMax + sellerMin) / 2;
        const deviation = Math.abs(currentNegotiation.final_price - midpoint);
        const range = buyerMax - sellerMin;
        return Math.max(5, Math.min(10, 10 - (deviation / range) * 5)).toFixed(1);
    }
    
    function calculateComplexity() {
        if (!currentNegotiation.rounds) return 6;
        const rounds = currentNegotiation.rounds.length;
        return Math.max(3, Math.min(10, Math.floor(rounds / 2) + 3));
    }
    
    function addAnalysisStyles() {
        if (!document.querySelector('#analysis-styles')) {
            const styles = document.createElement('style');
            styles.id = 'analysis-styles';
            styles.textContent = `
                .summary-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin: 1rem 0;
                }
                .summary-item {
                    padding: 0.75rem;
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: var(--radius-md);
                    border: 1px solid var(--border-color);
                }
                .summary-description {
                    margin-top: 1rem;
                    font-style: italic;
                    color: var(--text-secondary);
                }
                .analysis-metrics {
                    display: flex;
                    gap: 2rem;
                    margin-top: 1rem;
                    flex-wrap: wrap;
                }
                .metric {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 1rem;
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: var(--radius-md);
                    border: 1px solid var(--border-color);
                    min-width: 120px;
                }
                .metric-label {
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                    margin-bottom: 0.5rem;
                }
                .metric-value {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--primary-color);
                }
                .round-strategy {
                    margin-top: 0.5rem;
                    color: var(--text-light);
                    font-size: 0.875rem;
                }
                .no-rounds {
                    text-align: center;
                    color: var(--text-secondary);
                    font-style: italic;
                    padding: 2rem;
                }
                @media (max-width: 768px) {
                    .analysis-metrics {
                        gap: 1rem;
                    }
                    .metric {
                        min-width: 100px;
                        padding: 0.75rem;
                    }
                    .summary-grid {
                        grid-template-columns: 1fr;
                        gap: 0.75rem;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
    }
});