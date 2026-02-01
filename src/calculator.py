"""
投资计算器核心模块

该模块实现闲钱永不眠管理计算器的核心业务逻辑，包括：
- 可投资金额计算
- 投资分配计算
- 定投计划生成
- 加仓和止盈建议计算
"""

from typing import Dict, Optional, List, Any
from src.config import InvestmentConfig


class InvestmentCalculator:
    """投资计算器核心类
    
    该类负责所有投资计算逻辑，根据用户的财务数据和配置的投资策略，
    计算投资分配方案、定投计划以及加仓/止盈建议。
    """
    
    def __init__(self, config: InvestmentConfig):
        """初始化计算器
        
        Args:
            config: 投资配置对象
        """
        self.config = config
    
    def _calculate_living_expense_gap(
        self, target: float, current: float
    ) -> float:
        """计算生活费缺口
        
        生活费缺口 = MAX(0, 目标生活费 - 当前生活费)
        如果当前生活费已经满足或超过目标，则缺口为 0。
        
        Args:
            target: 生活费 1.5 月固定金额（目标）
            current: 剩余生活费金额（当前实际）
        
        Returns:
            生活费缺口金额（非负数）
        """
        return max(0, target - current)
    
    def _calculate_investable_amount(
        self, income: float, gap: float, debt: float
    ) -> float:
        """计算可投资金额
        
        可投资金额 = 新增收入 - 生活费缺口 - 负债
        该金额可能为负数，表示收入不足以覆盖生活费和负债。
        
        Args:
            income: 新增收入
            gap: 生活费缺口
            debt: 负债金额
        
        Returns:
            可投资金额（可能为负数）
        """
        return income - gap - debt
    
    def _allocate_framework(self, investable_amount: float) -> Dict[str, float]:
        """计算投资大框架分配
        
        根据配置的比例将可投资金额分配到四个大类：
        - 基金组合
        - 银行固收 R2
        - 实体黄金（积存金）
        - 备用金
        
        Args:
            investable_amount: 可投资金额
        
        Returns:
            包含各大类分配金额的字典，所有金额保留两位小数
        """
        return {
            "基金组合": round(investable_amount * self.config.fund_portfolio_ratio, 2),
            "银行固收R2": round(investable_amount * self.config.bank_fixed_income_ratio, 2),
            "实体黄金": round(investable_amount * self.config.physical_gold_ratio, 2),
            "备用金": round(investable_amount * self.config.reserve_fund_ratio, 2)
        }
    
    def _allocate_fund_portfolio(self, fund_portfolio_amount: float) -> Dict[str, float]:
        """计算基金组合内部分配
        
        根据配置的比例将基金组合金额分配到四个基金类别：
        - 中短债基金
        - 红利低波/沪深300
        - 标普/纳指
        - 黄金 ETF 联接 C
        
        Args:
            fund_portfolio_amount: 基金组合总金额
        
        Returns:
            包含各基金类别分配金额的字典，所有金额保留两位小数
        """
        return {
            "中短债基金": round(fund_portfolio_amount * self.config.bond_fund_ratio, 2),
            "红利低波/沪深300": round(fund_portfolio_amount * self.config.dividend_fund_ratio, 2),
            "标普/纳指": round(fund_portfolio_amount * self.config.us_index_fund_ratio, 2),
            "黄金ETF联接C": round(fund_portfolio_amount * self.config.gold_etf_ratio, 2)
        }
    
    def _generate_regular_investment_plan(self, fund_allocation: Dict[str, float]) -> Dict:
        """生成定投计划
        
        根据基金组合分配金额生成每周定投计划：
        - 周二：标普/纳指
        - 周四：中短债基金 + 红利低波/沪深300 + 黄金 ETF 联接 C
        
        Args:
            fund_allocation: 基金组合分配字典
        
        Returns:
            包含定投计划的字典，包括：
            - tuesday_amount: 周二定投金额
            - thursday_amount: 周四定投金额
            - weekly_total: 每周总定投金额
            - funds: 基金列表，每项包含 name、amount、day
        """
        tuesday_amount = fund_allocation["标普/纳指"]
        thursday_amount = (
            fund_allocation["中短债基金"] +
            fund_allocation["红利低波/沪深300"] +
            fund_allocation["黄金ETF联接C"]
        )
        
        return {
            "tuesday_amount": round(tuesday_amount, 2),
            "thursday_amount": round(thursday_amount, 2),
            "weekly_total": round(tuesday_amount + thursday_amount, 2),
            "funds": [
                {"name": "标普/纳指", "amount": round(fund_allocation["标普/纳指"], 2), "day": "周二"},
                {"name": "中短债基金", "amount": round(fund_allocation["中短债基金"], 2), "day": "周四"},
                {"name": "红利低波/沪深300", "amount": round(fund_allocation["红利低波/沪深300"], 2), "day": "周四"},
                {"name": "黄金ETF联接C", "amount": round(fund_allocation["黄金ETF联接C"], 2), "day": "周四"}
            ]
        }
    
    def _calculate_suggestions(self, holdings: Optional[List[Dict]]) -> Dict:
        """计算加仓和止盈建议
        
        根据持仓数据和配置的规则计算加仓和止盈建议。
        仅对以下基金应用规则：红利低波/沪深300、标普/纳指、黄金 ETF 联接 C
        中短债基金不参与加仓和止盈。
        
        Args:
            holdings: 持仓数据列表，每项包含：
                - fund_name: 基金名称
                - holding_cost: 持仓成本
                - current_nav: 当前净值
                - holding_amount: 持仓金额
        
        Returns:
            包含加仓和止盈建议的字典：
            - add_position_suggestions: 加仓建议列表
            - take_profit_suggestions: 止盈建议列表
            - total_add_amount: 总加仓金额
            - total_profit_amount: 总止盈金额
        """
        if not holdings:
            return {
                "add_position_suggestions": [],
                "take_profit_suggestions": [],
                "total_add_amount": 0.0,
                "total_profit_amount": 0.0
            }
        
        # 可以应用加仓和止盈规则的基金
        applicable_funds = {"红利低波/沪深300", "标普/纳指", "黄金ETF联接C"}
        
        add_suggestions = []
        profit_suggestions = []
        total_add = 0.0
        total_profit = 0.0
        
        for holding in holdings:
            fund_name = holding.get("fund_name", "")
            
            # 跳过不适用的基金
            if fund_name not in applicable_funds:
                continue
            
            holding_cost = holding.get("holding_cost", 0)
            current_nav = holding.get("current_nav", 0)
            holding_amount = holding.get("holding_amount", 0)
            
            # 避免除零错误
            if holding_cost == 0:
                continue
            
            # 计算收益率
            return_rate = (current_nav - holding_cost) / holding_cost
            
            # 检查加仓规则（按跌幅从大到小检查）
            sorted_thresholds = sorted(self.config.add_position_rules.keys())
            for threshold in sorted_thresholds:
                if return_rate <= threshold:
                    add_ratio = self.config.add_position_rules[threshold]
                    add_amount = round(holding_amount * add_ratio, 2)
                    add_suggestions.append({
                        "fund_name": fund_name,
                        "return_rate": round(return_rate * 100, 2),
                        "threshold": round(threshold * 100, 2),
                        "add_ratio": round(add_ratio * 100, 2),
                        "add_amount": add_amount
                    })
                    total_add += add_amount
                    break  # 只应用最严重的跌幅规则
            
            # 检查止盈规则
            if return_rate >= self.config.take_profit_threshold:
                profit_amount = round(holding_amount * self.config.take_profit_ratio, 2)
                profit_suggestions.append({
                    "fund_name": fund_name,
                    "return_rate": round(return_rate * 100, 2),
                    "threshold": round(self.config.take_profit_threshold * 100, 2),
                    "profit_ratio": round(self.config.take_profit_ratio * 100, 2),
                    "profit_amount": profit_amount
                })
                total_profit += profit_amount
        
        return {
            "add_position_suggestions": add_suggestions,
            "take_profit_suggestions": profit_suggestions,
            "total_add_amount": round(total_add, 2),
            "total_profit_amount": round(total_profit, 2)
        }
    
    def calculate(
        self,
        target_living_expense: float,
        current_living_expense: float,
        debt: float,
        new_income: float,
        holdings: Optional[List[Dict]] = None
    ) -> Dict:
        """执行完整的投资计算
        
        Args:
            target_living_expense: 生活费 1.5 月固定金额（目标）
            current_living_expense: 剩余生活费金额（当前实际）
            debt: 负债金额
            new_income: 新增收入
            holdings: 持仓数据列表（可选），每项包含：
                - fund_name: 基金名称
                - holding_cost: 持仓成本
                - current_nav: 当前净值
                - holding_amount: 持仓金额
        
        Returns:
            包含所有计算结果的字典：
            - living_expense_gap: 生活费缺口
            - investable_amount: 可投资金额
            - framework_allocation: 投资大框架分配
            - fund_allocation: 基金组合分配
            - regular_investment_plan: 定投计划
            - suggestions: 加仓和止盈建议（如果提供了持仓数据）
            - warning: 警告信息（如果可投资金额 ≤ 0）
        """
        # 1. 计算生活费缺口
        gap = self._calculate_living_expense_gap(target_living_expense, current_living_expense)
        
        # 2. 计算可投资金额
        investable = self._calculate_investable_amount(new_income, gap, debt)
        
        # 3. 初始化结果字典
        result: Dict[str, Any] = {
            "living_expense_gap": round(gap, 2),
            "investable_amount": round(investable, 2)
        }
        
# 4. 如果可投资金额 ≤ 0，添加警告并返回
        if investable <= 0:
            result["warning"] = "可投资金额不足，无法进行投资分配"
            result["framework_allocation"] = {}
            result["fund_allocation"] = {}
            result["regular_investment_plan"] = {
                "tuesday_amount": 0.0,
                "thursday_amount": 0.0,
                "weekly_total": 0.0,
                "funds": []
            }
            result["suggestions"] = {
                "add_position_suggestions": [],
                "take_profit_suggestions": [],
                "total_add_amount": 0.0,
                "total_profit_amount": 0.0
            }
            return result

        # 5. 计算投资大框架分配
        framework = self._allocate_framework(investable)
        result["framework_allocation"] = framework
        
        # 6. 计算基金组合分配
        fund_allocation = self._allocate_fund_portfolio(framework["基金组合"])
        result["fund_allocation"] = fund_allocation
        
        # 7. 生成定投计划
        result["regular_investment_plan"] = self._generate_regular_investment_plan(fund_allocation)
        
        # 8. 计算加仓和止盈建议（如果提供了持仓数据）
        result["suggestions"] = self._calculate_suggestions(holdings)
        
        return result

    def analyze_portfolio(self, holdings: Dict[str, float]) -> Dict:
        """分析持仓占比

        根据用户当前的持仓数据，计算实际占比并与预期配置进行对比分析。

        Args:
            holdings: 持仓数据字典，包含各投资类别的当前持仓金额：
                - bond_fund: 中短债基金持仓金额
                - dividend_fund: 红利低波持仓金额
                - us_index_fund: 标普/纳指持仓金额
                - gold_etf: 黄金ETF持仓金额
                - bank_fixed_income: 银行固收持仓金额
                - physical_gold: 实体黄金持仓金额
                - reserve_fund: 备用金持仓金额

        Returns:
            包含持仓分析结果的字典：
            - total_amount: 总持仓金额
            - framework_analysis: 投资大框架分析（基金组合、银行固收、实体黄金、备用金）
            - fund_portfolio_analysis: 基金组合内部分析（中短债、红利低波、标普/纳指、黄金ETF）
        """
        # 提取持仓金额，默认值为0
        bond_fund = holdings.get("bond_fund", 0)
        dividend_fund = holdings.get("dividend_fund", 0)
        us_index_fund = holdings.get("us_index_fund", 0)
        gold_etf = holdings.get("gold_etf", 0)
        bank_fixed_income = holdings.get("bank_fixed_income", 0)
        physical_gold = holdings.get("physical_gold", 0)
        reserve_fund = holdings.get("reserve_fund", 0)

        # 计算总持仓金额
        total_amount = (
            bond_fund + dividend_fund + us_index_fund + gold_etf +
            bank_fixed_income + physical_gold + reserve_fund
        )

        # 如果总持仓为0，返回空结果
        if total_amount == 0:
            return {
                "total_amount": 0.0,
                "framework_analysis": {},
                "fund_portfolio_analysis": {}
            }

        # 计算基金组合总金额
        fund_portfolio_amount = bond_fund + dividend_fund + us_index_fund + gold_etf

        # 投资大框架分析
        framework_categories = {
            "fund_portfolio": {
                "name": "基金组合",
                "amount": fund_portfolio_amount,
                "expected_ratio": self.config.fund_portfolio_ratio
            },
            "bank_fixed_income": {
                "name": "银行固收R2",
                "amount": bank_fixed_income,
                "expected_ratio": self.config.bank_fixed_income_ratio
            },
            "physical_gold": {
                "name": "实体黄金",
                "amount": physical_gold,
                "expected_ratio": self.config.physical_gold_ratio
            },
            "reserve_fund": {
                "name": "备用金",
                "amount": reserve_fund,
                "expected_ratio": self.config.reserve_fund_ratio
            }
        }

        framework_analysis = {}
        for key, category in framework_categories.items():
            actual_ratio = category["amount"] / total_amount
            deviation = actual_ratio - category["expected_ratio"]

            # 计算预期金额和调整金额
            expected_amount = total_amount * category["expected_ratio"]
            diff_amount = category["amount"] - expected_amount

            # 判断状态
            if abs(deviation) <= 0.05:
                status = "配置合理"
                need_adjustment = False
                action = "无需调整"
                adjust_amount = 0.0
            elif deviation > 0.05:
                status = "建议减持"
                need_adjustment = True
                action = "建议减持"
                adjust_amount = round(diff_amount, 2)
            else:
                status = "建议增持"
                need_adjustment = True
                action = "建议增持"
                adjust_amount = round(abs(diff_amount), 2)

            framework_analysis[key] = {
                "name": category["name"],
                "expected_ratio": round(category["expected_ratio"] * 100, 2),
                "actual_ratio": round(actual_ratio * 100, 2),
                "expected_amount": round(expected_amount, 2),
                "actual_amount": round(category["amount"], 2),
                "deviation": round(deviation * 100, 2),
                "diff_amount": round(diff_amount, 2),
                "status": status,
                "action": action,
                "adjust_amount": adjust_amount,
                "need_adjustment": need_adjustment
            }

        # 基金组合内部分析（仅当基金组合金额大于0时）
        fund_portfolio_analysis = {}
        if fund_portfolio_amount > 0:
            fund_categories = {
                "bond_fund": {
                    "name": "中短债基金",
                    "amount": bond_fund,
                    "expected_ratio": self.config.bond_fund_ratio
                },
                "dividend_fund": {
                    "name": "红利低波/沪深300",
                    "amount": dividend_fund,
                    "expected_ratio": self.config.dividend_fund_ratio
                },
                "us_index_fund": {
                    "name": "标普/纳指",
                    "amount": us_index_fund,
                    "expected_ratio": self.config.us_index_fund_ratio
                },
                "gold_etf": {
                    "name": "黄金ETF联接C",
                    "amount": gold_etf,
                    "expected_ratio": self.config.gold_etf_ratio
                }
            }

            for key, fund in fund_categories.items():
                actual_ratio = fund["amount"] / fund_portfolio_amount
                deviation = actual_ratio - fund["expected_ratio"]

                # 计算预期金额和调整金额
                expected_amount = fund_portfolio_amount * fund["expected_ratio"]
                diff_amount = fund["amount"] - expected_amount

                # 判断状态
                if abs(deviation) <= 0.05:
                    status = "配置合理"
                    need_adjustment = False
                    action = "无需调整"
                    adjust_amount = 0.0
                elif deviation > 0.05:
                    status = "建议减持"
                    need_adjustment = True
                    action = "建议减持"
                    adjust_amount = round(diff_amount, 2)
                else:
                    status = "建议增持"
                    need_adjustment = True
                    action = "建议增持"
                    adjust_amount = round(abs(diff_amount), 2)

                fund_portfolio_analysis[key] = {
                    "name": fund["name"],
                    "expected_ratio": round(fund["expected_ratio"] * 100, 2),
                    "actual_ratio": round(actual_ratio * 100, 2),
                    "expected_amount": round(expected_amount, 2),
                    "actual_amount": round(fund["amount"], 2),
                    "deviation": round(deviation * 100, 2),
                    "diff_amount": round(diff_amount, 2),
                    "status": status,
                    "action": action,
                    "adjust_amount": adjust_amount,
                    "need_adjustment": need_adjustment
                }

        return {
            "total_amount": round(total_amount, 2),
            "framework_analysis": framework_analysis,
            "fund_portfolio_analysis": fund_portfolio_analysis
        }
