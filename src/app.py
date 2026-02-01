"""
闲钱永不眠管理计算器 Flask 应用

该模块提供 HTTP API 接口和静态文件服务。
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.calculator import InvestmentCalculator
from src.config import InvestmentConfig

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# 创建 Flask 应用
app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)  # 启用 CORS 支持

# 初始化配置和计算器
config = InvestmentConfig()
if not config.validate():
    raise ValueError("配置验证失败：投资比例总和必须为 100%")

calculator = InvestmentCalculator(config)


@app.route('/')
def index():
    """提供静态 HTML 页面"""
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """投资计算 API
    
    请求体示例：
    {
        "target_living_expense": 15000,
        "current_living_expense": 10000,
        "debt": 2000,
        "new_income": 20000,
        "holdings": [  // 可选
            {
                "fund_name": "红利低波/沪深300",
                "holding_cost": 1.0,
                "current_nav": 0.92,
                "holding_amount": 10000
            }
        ]
    }
    
    响应示例：
    {
        "success": true,
        "data": {
            "living_expense_gap": 5000.00,
            "investable_amount": 13000.00,
            ...
        }
    }
    """
    try:
        # 1. 解析 JSON 请求体
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
        
        # 2. 验证必填字段
        required_fields = ['target_living_expense', 'current_living_expense', 'debt', 'new_income']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'缺少必填字段: {", ".join(missing_fields)}'
            }), 400
        
        # 3. 验证数值类型和非负性
        for field in required_fields:
            value = data[field]
            if not isinstance(value, (int, float)):
                return jsonify({
                    'success': False,
                    'error': f'字段 {field} 必须是数值类型'
                }), 400
            if value < 0:
                return jsonify({
                    'success': False,
                    'error': f'字段 {field} 不能为负数'
                }), 400
        
        # 4. 提取参数
        target_living_expense = float(data['target_living_expense'])
        current_living_expense = float(data['current_living_expense'])
        debt = float(data['debt'])
        new_income = float(data['new_income'])
        holdings = data.get('holdings', None)
        
        # 5. 调用计算器执行计算
        result = calculator.calculate(
            target_living_expense=target_living_expense,
            current_living_expense=current_living_expense,
            debt=debt,
            new_income=new_income,
            holdings=holdings
        )
        
        # 6. 返回成功响应
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        # 7. 处理异常并返回 500 错误
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置 API"""
    return jsonify({
        'success': True,
        'data': {
            'framework': {
                'fund_portfolio': config.fund_portfolio_ratio,
                'bank_fixed_income': config.bank_fixed_income_ratio,
                'physical_gold': config.physical_gold_ratio,
                'reserve_fund': config.reserve_fund_ratio
            },
            'fund_portfolio': {
                'bond_fund': config.bond_fund_ratio,
                'dividend_fund': config.dividend_fund_ratio,
                'us_index_fund': config.us_index_fund_ratio,
                'gold_etf': config.gold_etf_ratio
            },
            'add_position_rules': config.add_position_rules,
            'take_profit': {
                'threshold': config.take_profit_threshold,
                'ratio': config.take_profit_ratio
            }
        }
    })


@app.route('/api/analyze-portfolio', methods=['POST'])
def analyze_portfolio():
    """持仓占比分析 API

    请求体示例：
    {
        "holdings": {
            "bond_fund": 10000,
            "dividend_fund": 8000,
            "us_index_fund": 5000,
            "gold_etf": 3000,
            "bank_fixed_income": 50000,
            "physical_gold": 5000,
            "reserve_fund": 5000
        }
    }

    响应示例：
    {
        "success": true,
        "data": {
            "total_amount": 86000.00,
            "framework_analysis": {...},
            "fund_portfolio_analysis": {...}
        }
    }
    """
    try:
        # 1. 解析 JSON 请求体
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        # 2. 验证必填字段
        if 'holdings' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必填字段: holdings'
            }), 400

        holdings = data['holdings']
        if not isinstance(holdings, dict):
            return jsonify({
                'success': False,
                'error': 'holdings 必须是对象类型'
            }), 400

        # 3. 验证持仓金额字段
        valid_fields = [
            'bond_fund', 'dividend_fund', 'us_index_fund', 'gold_etf',
            'bank_fixed_income', 'physical_gold', 'reserve_fund'
        ]

        validated_holdings = {}
        total_amount = 0.0

        for field in valid_fields:
            if field in holdings:
                value = holdings[field]
                if not isinstance(value, (int, float)):
                    return jsonify({
                        'success': False,
                        'error': f'持仓金额 {field} 必须是数值类型'
                    }), 400
                if value < 0:
                    return jsonify({
                        'success': False,
                        'error': f'持仓金额 {field} 不能为负数'
                    }), 400
                validated_holdings[field] = float(value)
                total_amount += float(value)
            else:
                validated_holdings[field] = 0.0

        # 4. 验证总持仓金额大于0
        if total_amount == 0:
            return jsonify({
                'success': False,
                'error': '总持仓金额不能为0，请至少输入一项持仓金额'
            }), 400

        # 5. 调用计算器执行分析
        result = calculator.analyze_portfolio(validated_holdings)

        # 6. 返回成功响应
        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        # 7. 处理异常并返回 500 错误
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@app.route('/api/config', methods=['PUT'])
def update_config():
    """更新配置 API
    
    请求体示例：
    {
        "framework": {
            "fund_portfolio": 0.30,
            "bank_fixed_income": 0.60,
            "physical_gold": 0.05,
            "reserve_fund": 0.05
        },
        "fund_portfolio": {
            "bond_fund": 0.40,
            "dividend_fund": 0.30,
            "us_index_fund": 0.15,
            "gold_etf": 0.15
        }
    }
    
    响应示例：
    {
        "success": true,
        "data": {
            "message": "配置更新成功"
        }
    }
    """
    try:
        # 1. 解析 JSON 请求体
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
            
        # 2. 验证比例总和
        if 'framework' in data:
            framework_sum = sum(data['framework'].values())
            if abs(framework_sum - 1.0) > 0.0001:
                return jsonify({
                    'success': False,
                    'error': '投资大框架比例总和必须为 100%'
                }), 400
                
        if 'fund_portfolio' in data:
            portfolio_sum = sum(data['fund_portfolio'].values())
            if abs(portfolio_sum - 1.0) > 0.0001:
                return jsonify({
                    'success': False,
                    'error': '基金组合比例总和必须为 100%'
                }), 400
        
        # 3. 更新配置
        global config, calculator
        
        # 更新投资大框架比例
        if 'framework' in data:
            if 'fund_portfolio' in data['framework']:
                config.fund_portfolio_ratio = data['framework']['fund_portfolio']
            if 'bank_fixed_income' in data['framework']:
                config.bank_fixed_income_ratio = data['framework']['bank_fixed_income']
            if 'physical_gold' in data['framework']:
                config.physical_gold_ratio = data['framework']['physical_gold']
            if 'reserve_fund' in data['framework']:
                config.reserve_fund_ratio = data['framework']['reserve_fund']
        
        # 更新基金组合比例
        if 'fund_portfolio' in data:
            if 'bond_fund' in data['fund_portfolio']:
                config.bond_fund_ratio = data['fund_portfolio']['bond_fund']
            if 'dividend_fund' in data['fund_portfolio']:
                config.dividend_fund_ratio = data['fund_portfolio']['dividend_fund']
            if 'us_index_fund' in data['fund_portfolio']:
                config.us_index_fund_ratio = data['fund_portfolio']['us_index_fund']
            if 'gold_etf' in data['fund_portfolio']:
                config.gold_etf_ratio = data['fund_portfolio']['gold_etf']
        
        # 重新创建计算器实例
        calculator = InvestmentCalculator(config)
        
        # 4. 返回成功响应
        return jsonify({
            'success': True,
            'data': {
                'message': '配置更新成功'
            }
        }), 200
        
    except Exception as e:
        # 5. 处理异常并返回 500 错误
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
