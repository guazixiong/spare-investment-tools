// 投资管理计算器前端交互逻辑

let holdingCounter = 0;

// 工具切换函数
function switchTool(toolName) {
    // 更新按钮状态
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${toolName}`).classList.add('active');

    // 显示/隐藏工具区域
    document.querySelectorAll('.tool-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    const activeSection = document.getElementById(`${toolName}-tool`);
    activeSection.classList.add('active');
    activeSection.style.display = 'block';

    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 添加持仓输入项
function addHoldingInput() {
    holdingCounter++;
    const container = document.getElementById('holdingsContainer');
    const holdingDiv = document.createElement('div');
    holdingDiv.className = 'holding-item';
    holdingDiv.id = `holding-${holdingCounter}`;
    
    holdingDiv.innerHTML = `
        <button type="button" class="btn-remove-holding" onclick="removeHolding(${holdingCounter})">删除</button>
        <div class="form-row">
            <div class="form-group">
                <label>基金名称：</label>
                <select class="holding-fund-name" required>
                    <option value="">请选择</option>
                    <option value="红利低波/沪深300">红利低波/沪深300</option>
                    <option value="标普/纳指">标普/纳指</option>
                    <option value="黄金ETF联接C">黄金ETF联接C</option>
                </select>
            </div>
            <div class="form-group">
                <label>持仓成本：</label>
                <input type="number" class="holding-cost" min="0" step="0.01" required>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>当前净值：</label>
                <input type="number" class="holding-nav" min="0" step="0.01" required>
            </div>
            <div class="form-group">
                <label>持仓金额（元）：</label>
                <input type="number" class="holding-amount" min="0" step="0.01" required>
            </div>
        </div>
    `;
    
    container.appendChild(holdingDiv);
}

// 删除持仓输入项
function removeHolding(id) {
    const holdingDiv = document.getElementById(`holding-${id}`);
    if (holdingDiv) {
        holdingDiv.remove();
    }
}

// 收集持仓数据
function collectHoldings() {
    const holdings = [];
    const holdingItems = document.querySelectorAll('.holding-item');
    
    holdingItems.forEach(item => {
        const fundName = item.querySelector('.holding-fund-name').value;
        const holdingCost = parseFloat(item.querySelector('.holding-cost').value);
        const currentNav = parseFloat(item.querySelector('.holding-nav').value);
        const holdingAmount = parseFloat(item.querySelector('.holding-amount').value);
        
        if (fundName && !isNaN(holdingCost) && !isNaN(currentNav) && !isNaN(holdingAmount)) {
            holdings.push({
                fund_name: fundName,
                holding_cost: holdingCost,
                current_nav: currentNav,
                holding_amount: holdingAmount
            });
        }
    });
    
    return holdings.length > 0 ? holdings : null;
}

document.addEventListener('DOMContentLoaded', function() {
    // 加载当前配置
    loadCurrentConfig();
    
    const form = document.getElementById('calculatorForm');
    const resultSection = document.getElementById('resultSection');
    const errorMessage = document.getElementById('errorMessage');
    
    // 表单提交处理
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // 隐藏之前的错误信息
            hideError();
            
            // 获取表单数据
            const formData = {
                target_living_expense: parseFloat(document.getElementById('targetLivingExpense').value),
                current_living_expense: parseFloat(document.getElementById('currentLivingExpense').value),
                debt: parseFloat(document.getElementById('debt').value),
                new_income: parseFloat(document.getElementById('newIncome').value)
            };
            
            // 收集持仓数据（如果有）
            const holdings = collectHoldings();
            if (holdings) {
                formData.holdings = holdings;
            }
            
            // 实时验证
            if (!validateInput(formData)) {
                return;
            }
            
            // 发送 API 请求
            try {
                const response = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayResult(result.data);
                } else {
                    displayError(result.error || '计算失败，请重试');
                }
            } catch (error) {
                displayError('网络错误，请检查服务器是否正常运行');
                console.error('Error:', error);
            }
        });
    }
    
    // 输入验证
    function validateInput(data) {
        // 检查非负数
        for (const key in data) {
            if (data[key] < 0) {
                displayError(`${getFieldName(key)} 不能为负数`);
                return false;
            }
            if (isNaN(data[key])) {
                displayError(`${getFieldName(key)} 必须是有效的数字`);
                return false;
            }
        }
        return true;
    }
    
    // 获取字段中文名称
    function getFieldName(key) {
        const names = {
            'target_living_expense': '目标生活费',
            'current_living_expense': '当前生活费余额',
            'debt': '当前负债',
            'new_income': '新增收入'
        };
        return names[key] || key;
    }
    
    // 显示结果
    function displayResult(data) {
        // 显示结果区域
        resultSection.style.display = 'block';
        
        // 基础信息
        document.getElementById('livingExpenseGap').textContent = data.living_expense_gap.toFixed(2);
        document.getElementById('investableAmount').textContent = data.investable_amount.toFixed(2);
        
        // 处理警告信息
        const warningDiv = document.getElementById('warningMessage');
        if (data.warning) {
            warningDiv.textContent = data.warning;
            warningDiv.style.display = 'block';
        } else {
            warningDiv.style.display = 'none';
        }
        
        // 投资大框架分配
        const frameworkDiv = document.getElementById('frameworkAllocation');
        frameworkDiv.innerHTML = '';
        if (data.framework_allocation) {
            for (const [key, value] of Object.entries(data.framework_allocation)) {
                frameworkDiv.innerHTML += `
                    <div class="result-item">
                        <span class="label">${key}：</span>
                        <span class="value">${value.toFixed(2)}</span>
                        <span class="unit">元</span>
                    </div>
                `;
            }
        }
        
        // 基金组合分配
        const fundDiv = document.getElementById('fundAllocation');
        fundDiv.innerHTML = '';
        if (data.fund_allocation) {
            for (const [key, value] of Object.entries(data.fund_allocation)) {
                fundDiv.innerHTML += `
                    <div class="result-item">
                        <span class="label">${key}：</span>
                        <span class="value">${value.toFixed(2)}</span>
                        <span class="unit">元</span>
                    </div>
                `;
            }
        }
        
        // 定投计划
        if (data.regular_investment_plan) {
            const plan = data.regular_investment_plan;
            document.getElementById('tuesdayAmount').textContent = plan.tuesday_amount.toFixed(2);
            document.getElementById('thursdayAmount').textContent = plan.thursday_amount.toFixed(2);
            document.getElementById('weeklyTotal').textContent = plan.weekly_total.toFixed(2);
            
            // 基金列表
            const fundsListDiv = document.getElementById('fundsList');
            fundsListDiv.innerHTML = '<h4 style="margin-top: 15px; margin-bottom: 10px; color: #555;">基金明细：</h4>';
            if (plan.funds && plan.funds.length > 0) {
                plan.funds.forEach(fund => {
                    fundsListDiv.innerHTML += `
                        <div class="fund-item">
                            <span class="fund-name">${fund.name}</span>
                            <span class="fund-amount">${fund.amount.toFixed(2)} 元</span>
                            <span class="fund-day">${fund.day}</span>
                        </div>
                    `;
                });
            }
        }
        
        // 滚动到结果区域
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // 显示加仓和止盈建议
        displaySuggestions(data.suggestions);
    }
    
    // 显示加仓和止盈建议
    function displaySuggestions(suggestions) {
        const suggestionsCard = document.getElementById('suggestionsCard');
        const suggestionsContent = document.getElementById('suggestionsContent');
        
        // 如果没有建议,隐藏卡片
        if (!suggestions || 
            (suggestions.add_position_suggestions.length === 0 && 
             suggestions.take_profit_suggestions.length === 0)) {
            suggestionsCard.style.display = 'none';
            return;
        }
        
        suggestionsCard.style.display = 'block';
        suggestionsContent.innerHTML = '';
        
        // 显示加仓建议
        if (suggestions.add_position_suggestions.length > 0) {
            suggestionsContent.innerHTML += '<h4 style="color: #ffc107; margin-bottom: 10px;">⚠️ 加仓建议</h4>';
            suggestions.add_position_suggestions.forEach(item => {
                suggestionsContent.innerHTML += `
                    <div class="suggestion-item add-position">
                        <div class="fund-name">${item.fund_name}</div>
                        <div class="suggestion-detail">当前收益率: ${item.return_rate.toFixed(2)}%</div>
                        <div class="suggestion-detail">触发阈值: ${item.threshold.toFixed(2)}%</div>
                        <div class="suggestion-detail">建议加仓比例: ${item.add_ratio.toFixed(2)}%</div>
                        <div class="suggestion-amount">建议加仓金额: ${item.add_amount.toFixed(2)} 元</div>
                    </div>
                `;
            });
        }
        
        // 显示止盈建议
        if (suggestions.take_profit_suggestions.length > 0) {
            suggestionsContent.innerHTML += '<h4 style="color: #28a745; margin-bottom: 10px; margin-top: 20px;">✅ 止盈建议</h4>';
            suggestions.take_profit_suggestions.forEach(item => {
                suggestionsContent.innerHTML += `
                    <div class="suggestion-item take-profit">
                        <div class="fund-name">${item.fund_name}</div>
                        <div class="suggestion-detail">当前收益率: ${item.return_rate.toFixed(2)}%</div>
                        <div class="suggestion-detail">触发阈值: ${item.threshold.toFixed(2)}%</div>
                        <div class="suggestion-detail">建议止盈比例: ${item.profit_ratio.toFixed(2)}%</div>
                        <div class="suggestion-amount">建议止盈金额: ${item.profit_amount.toFixed(2)} 元</div>
                    </div>
                `;
            });
        }
        
        // 显示汇总
        if (suggestions.total_add_amount > 0 || suggestions.total_profit_amount > 0) {
            suggestionsContent.innerHTML += `
                <div class="suggestion-summary">
                    <div class="suggestion-summary-item">
                        <span class="label">总加仓金额</span>
                        <span class="value">${suggestions.total_add_amount.toFixed(2)} 元</span>
                    </div>
                    <div class="suggestion-summary-item">
                        <span class="label">总止盈金额</span>
                        <span class="value">${suggestions.total_profit_amount.toFixed(2)} 元</span>
                    </div>
                </div>
            `;
        }
    }
    
    // 显示错误信息
    function displayError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        resultSection.style.display = 'none';
        
        // 滚动到错误信息
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
// 隐藏错误信息
function hideError() {
    errorMessage.style.display = 'none';
}

// 持仓分析表单处理
const portfolioForm = document.getElementById('portfolioForm');
if (portfolioForm) {
    portfolioForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // 隐藏之前的错误信息
        const portfolioErrorMessage = document.getElementById('portfolioErrorMessage');
        portfolioErrorMessage.style.display = 'none';

        // 获取表单数据
        const holdings = {
            bond_fund: parseFloat(document.getElementById('bondFundHolding').value) || 0,
            dividend_fund: parseFloat(document.getElementById('dividendFundHolding').value) || 0,
            us_index_fund: parseFloat(document.getElementById('usIndexFundHolding').value) || 0,
            gold_etf: parseFloat(document.getElementById('goldEtfHolding').value) || 0,
            bank_fixed_income: parseFloat(document.getElementById('bankFixedIncomeHolding').value) || 0,
            physical_gold: parseFloat(document.getElementById('physicalGoldHolding').value) || 0,
            reserve_fund: parseFloat(document.getElementById('reserveFundHolding').value) || 0
        };

        // 验证至少有一项持仓
        const totalHolding = Object.values(holdings).reduce((sum, val) => sum + val, 0);
        if (totalHolding === 0) {
            displayPortfolioError('请至少输入一项持仓金额');
            return;
        }

        // 发送 API 请求
        try {
            const response = await fetch('/api/analyze-portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ holdings: holdings })
            });

            const result = await response.json();

            if (result.success) {
                displayPortfolioResult(result.data);
            } else {
                displayPortfolioError(result.error || '分析失败，请重试');
            }
        } catch (error) {
            displayPortfolioError('网络错误，请检查服务器是否正常运行');
            console.error('Error:', error);
        }
    });
}

// 显示持仓分析结果
function displayPortfolioResult(data) {
    const resultSection = document.getElementById('portfolioResultSection');
    resultSection.style.display = 'block';

    // 总览
    document.getElementById('portfolioTotalAmount').textContent = data.total_amount.toFixed(2);

    // 投资大框架分析
    const frameworkDiv = document.getElementById('frameworkAnalysis');
    frameworkDiv.innerHTML = '';
    if (data.framework_analysis) {
        for (const [key, item] of Object.entries(data.framework_analysis)) {
            const statusClass = getStatusClass(item.status);
            const adjustAmountHtml = item.need_adjustment ? `
                <div class="analysis-row adjust-row">
                    <span class="label">${item.action}：</span>
                    <span class="value adjust-amount">${item.adjust_amount.toFixed(2)} 元</span>
                </div>
            ` : '';
            frameworkDiv.innerHTML += `
                <div class="analysis-item ${statusClass}">
                    <div class="analysis-header">
                        <span class="analysis-name">${item.name}</span>
                        <span class="analysis-status">${item.status}</span>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-row">
                            <span class="label">预期占比：</span>
                            <span class="value">${item.expected_ratio.toFixed(2)}%</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">实际占比：</span>
                            <span class="value">${item.actual_ratio.toFixed(2)}%</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">预期金额：</span>
                            <span class="value">${item.expected_amount.toFixed(2)} 元</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">实际金额：</span>
                            <span class="value">${item.actual_amount.toFixed(2)} 元</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">偏差：</span>
                            <span class="value ${item.deviation > 0 ? 'positive' : item.deviation < 0 ? 'negative' : ''}">
                                ${item.deviation > 0 ? '+' : ''}${item.deviation.toFixed(2)}%
                            </span>
                        </div>
                        ${adjustAmountHtml}
                    </div>
                </div>
            `;
        }
    }

    // 基金组合内部分析
    const fundDiv = document.getElementById('fundPortfolioAnalysis');
    fundDiv.innerHTML = '';
    if (data.fund_portfolio_analysis && Object.keys(data.fund_portfolio_analysis).length > 0) {
        for (const [key, item] of Object.entries(data.fund_portfolio_analysis)) {
            const statusClass = getStatusClass(item.status);
            const adjustAmountHtml = item.need_adjustment ? `
                <div class="analysis-row adjust-row">
                    <span class="label">${item.action}：</span>
                    <span class="value adjust-amount">${item.adjust_amount.toFixed(2)} 元</span>
                </div>
            ` : '';
            fundDiv.innerHTML += `
                <div class="analysis-item ${statusClass}">
                    <div class="analysis-header">
                        <span class="analysis-name">${item.name}</span>
                        <span class="analysis-status">${item.status}</span>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-row">
                            <span class="label">预期占比：</span>
                            <span class="value">${item.expected_ratio.toFixed(2)}%</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">实际占比：</span>
                            <span class="value">${item.actual_ratio.toFixed(2)}%</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">预期金额：</span>
                            <span class="value">${item.expected_amount.toFixed(2)} 元</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">实际金额：</span>
                            <span class="value">${item.actual_amount.toFixed(2)} 元</span>
                        </div>
                        <div class="analysis-row">
                            <span class="label">偏差：</span>
                            <span class="value ${item.deviation > 0 ? 'positive' : item.deviation < 0 ? 'negative' : ''}">
                                ${item.deviation > 0 ? '+' : ''}${item.deviation.toFixed(2)}%
                            </span>
                        </div>
                        ${adjustAmountHtml}
                    </div>
                </div>
            `;
        }
    } else {
        fundDiv.innerHTML = '<p class="no-data">基金组合金额为0，暂无内部分析</p>';
    }

    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 获取状态对应的CSS类
function getStatusClass(status) {
    if (status === '配置合理') {
        return 'status-good';
    } else if (status === '建议增持') {
        return 'status-warning';
    } else if (status === '建议减持') {
        return 'status-danger';
    }
    return '';
}

// 显示持仓分析错误信息
function displayPortfolioError(message) {
    const errorDiv = document.getElementById('portfolioErrorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('portfolioResultSection').style.display = 'none';

    // 滚动到错误信息
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// 投资比例设置表单处理
const configForm = document.getElementById('configForm');
if (configForm) {
    configForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // 隐藏之前的错误信息
        const configErrorMessage = document.getElementById('configErrorMessage');
        configErrorMessage.style.display = 'none';

        // 获取表单数据并转换为小数
        const configData = {
            framework: {
                fund_portfolio: parseFloat(document.getElementById('fundPortfolioRatio').value) / 100,
                bank_fixed_income: parseFloat(document.getElementById('bankFixedIncomeRatio').value) / 100,
                physical_gold: parseFloat(document.getElementById('physicalGoldRatio').value) / 100,
                reserve_fund: parseFloat(document.getElementById('reserveFundRatio').value) / 100
            },
            fund_portfolio: {
                bond_fund: parseFloat(document.getElementById('bondFundRatio').value) / 100,
                dividend_fund: parseFloat(document.getElementById('dividendFundRatio').value) / 100,
                us_index_fund: parseFloat(document.getElementById('usIndexFundRatio').value) / 100,
                gold_etf: parseFloat(document.getElementById('goldEtfRatio').value) / 100
            }
        };

        // 验证比例总和
        const frameworkSum = Object.values(configData.framework).reduce((sum, val) => sum + val, 0);
        if (Math.abs(frameworkSum - 1) > 0.0001) {
            displayConfigError('投资大框架分配比例总和必须为 100%');
            return;
        }

        const fundPortfolioSum = Object.values(configData.fund_portfolio).reduce((sum, val) => sum + val, 0);
        if (Math.abs(fundPortfolioSum - 1) > 0.0001) {
            displayConfigError('基金组合内部分配比例总和必须为 100%');
            return;
        }

        // 发送 API 请求
        try {
            const response = await fetch('/api/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            });

            const result = await response.json();

            if (result.success) {
                displayConfigResult(result.data);
                // 重新加载配置以更新显示
                loadCurrentConfig();
            } else {
                displayConfigError(result.error || '设置失败，请重试');
            }
        } catch (error) {
            displayConfigError('网络错误，请检查服务器是否正常运行');
            console.error('Error:', error);
        }
    });
}

// 显示配置结果
function displayConfigResult(data) {
    const resultSection = document.getElementById('configResultSection');
    resultSection.style.display = 'block';

    document.getElementById('configStatus').textContent = data.message;

    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 显示配置错误信息
function displayConfigError(message) {
    const errorDiv = document.getElementById('configErrorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('configResultSection').style.display = 'none';

    // 滚动到错误信息
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// 加载当前配置并填充表单
async function loadCurrentConfig() {
    try {
        const response = await fetch('/api/config');
        const result = await response.json();
        
        if (result.success) {
            const config = result.data;
            
            // 填充投资大框架分配比例
            if (config.framework) {
                document.getElementById('fundPortfolioRatio').value = (config.framework.fund_portfolio * 100).toFixed(0);
                document.getElementById('bankFixedIncomeRatio').value = (config.framework.bank_fixed_income * 100).toFixed(0);
                document.getElementById('physicalGoldRatio').value = (config.framework.physical_gold * 100).toFixed(0);
                document.getElementById('reserveFundRatio').value = (config.framework.reserve_fund * 100).toFixed(0);
            }
            
            // 填充基金组合内部分配比例
            if (config.fund_portfolio) {
                document.getElementById('bondFundRatio').value = (config.fund_portfolio.bond_fund * 100).toFixed(0);
                document.getElementById('dividendFundRatio').value = (config.fund_portfolio.dividend_fund * 100).toFixed(0);
                document.getElementById('usIndexFundRatio').value = (config.fund_portfolio.us_index_fund * 100).toFixed(0);
                document.getElementById('goldEtfRatio').value = (config.fund_portfolio.gold_etf * 100).toFixed(0);
            }
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}
});
