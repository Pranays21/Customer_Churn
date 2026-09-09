document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const predictForm = document.getElementById('predictForm');
    const tenureSlider = document.getElementById('tenure');
    const tenureVal = document.getElementById('tenureVal');
    const chargesSlider = document.getElementById('MonthlyCharges');
    const chargesVal = document.getElementById('MonthlyChargesVal');
    
    const idlePanel = document.getElementById('idlePanel');
    const loadingPanel = document.getElementById('loadingPanel');
    const resultsCard = document.getElementById('resultsCard');
    
    const riskRing = document.getElementById('riskRing');
    const riskPct = document.getElementById('riskPct');
    const riskLevel = document.getElementById('riskLevel');
    const factorsList = document.getElementById('factorsList');
    
    // Set up Circular Progress Ring
    const radius = riskRing.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    
    riskRing.style.strokeDasharray = `${circumference} ${circumference}`;
    riskRing.style.strokeDashoffset = circumference;

    function setGaugeProgress(percent, riskClass) {
        // Animate stroke offset
        const offset = circumference - (percent / 100) * circumference;
        riskRing.style.strokeDashoffset = offset;
        
        // Update color scheme based on risk
        if (riskClass === 'danger') {
            riskRing.style.stroke = '#ef4444'; // Red
        } else if (riskClass === 'warning') {
            riskRing.style.stroke = '#f59e0b'; // Amber
        } else {
            riskRing.style.stroke = '#10b981'; // Emerald
        }
    }

    // Update range slider values dynamically
    tenureSlider.addEventListener('input', (e) => {
        tenureVal.textContent = e.target.value;
    });

    chargesSlider.addEventListener('input', (e) => {
        chargesVal.textContent = parseFloat(e.target.value).toFixed(2);
    });

    // Handle Form Submission
    predictForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        idlePanel.classList.add('hidden');
        resultsCard.classList.add('hidden');
        loadingPanel.classList.remove('hidden');
        
        // Construct request payload
        const formData = new FormData(predictForm);
        const payload = {};
        
        formData.forEach((value, key) => {
            payload[key] = value;
        });
        
        // Add calculated TotalCharges (Frontend approximation or let backend handle it)
        const tenure = parseInt(payload.tenure);
        const monthly = parseFloat(payload.MonthlyCharges);
        payload['TotalCharges'] = (tenure * monthly).toFixed(2);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Prediction request failed server-side.');
            }

            const result = await response.json();
            
            // Hide loading, show results
            loadingPanel.classList.add('hidden');
            resultsCard.classList.remove('hidden');
            
            // 1. Update Gauge Percentage Text
            riskPct.textContent = `${result.probability}%`;
            
            // 2. Determine CSS class and color scheme
            let badgeClass = 'level-low';
            if (result.risk_level === 'High') {
                badgeClass = 'level-high';
            } else if (result.risk_level === 'Medium') {
                badgeClass = 'level-warning';
            }
            
            // 3. Set Badge Risk text
            riskLevel.className = `risk-badge ${badgeClass}`;
            riskLevel.textContent = `${result.risk_level} Churn Risk`;
            
            // 4. Animate SVG Ring
            setGaugeProgress(result.probability, result.badge_class);
            
            // 5. Inject risk factors
            factorsList.innerHTML = '';
            
            if (result.risk_factors && result.risk_factors.length > 0) {
                result.risk_factors.forEach(factor => {
                    const impactClass = factor.impact.toLowerCase().includes('high') ? 'impact-high' : 'impact-medium';
                    const itemHTML = `
                        <div class="factor-item ${impactClass}">
                            <div class="factor-item-header">
                                <span class="factor-name">${factor.feature}: ${factor.value}</span>
                                <span class="factor-impact">${factor.impact}</span>
                            </div>
                            <p class="factor-desc">${factor.description}</p>
                        </div>
                    `;
                    factorsList.insertAdjacentHTML('beforeend', itemHTML);
                });
            } else {
                factorsList.innerHTML = `
                    <div class="factor-item" style="border-left-color: #10b981;">
                        <div class="factor-item-header">
                            <span class="factor-name">Strong Retention Profile</span>
                            <span class="factor-impact" style="color: #10b981; background: rgba(16,185,129,0.1)">Optimal</span>
                        </div>
                        <p class="factor-desc">This customer possesses features highly correlated with long-term retention (e.g., long tenure, multi-year contracts, and automated payment setup).</p>
                    </div>
                `;
            }
            
        } catch (err) {
            console.error(err);
            loadingPanel.classList.add('hidden');
            idlePanel.classList.remove('hidden');
            alert('An error occurred during risk calculation: ' + err.message);
        }
    });
});
