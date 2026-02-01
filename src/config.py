"""
投资策略配置模块

该模块定义了投资管理计算器的所有配置参数，包括投资比例和规则配置。
"""

from typing import Dict
from dataclasses import dataclass, field


@dataclass
class InvestmentConfig:
    """投资策略配置类
    
    该类管理所有投资策略相关的比例和规则配置，包括：
    - 投资大框架分配比例（基金组合、银行固收、实体黄金、备用金）
    - 基金组合内部分配比例（中短债、红利低波、标普/纳指、黄金 ETF）
    - 加仓规则配置
    - 止盈规则配置
    """
    
    # 投资大框架分配比例（总和必须为 100%）
    fund_portfolio_ratio: float = 0.30      # 基金组合 30%
    bank_fixed_income_ratio: float = 0.60   # 银行固收 R2 60%
    physical_gold_ratio: float = 0.05       # 实体黄金（积存金）5%
    reserve_fund_ratio: float = 0.05        # 备用金 5%
    
    # 基金组合内部分配比例（总和必须为 100%）
    bond_fund_ratio: float = 0.40           # 中短债基金 40%
    dividend_fund_ratio: float = 0.30       # 红利低波/沪深300 30%
    us_index_fund_ratio: float = 0.15       # 标普/纳指 15%
    gold_etf_ratio: float = 0.15            # 黄金 ETF 联接 C 15%
    
    # 加仓规则配置：{跌幅阈值: 加仓比例}
    add_position_rules: Dict[float, float] = field(default_factory=lambda: {
        -0.05: 0.10,  # 跌 5% 加仓 10%
        -0.10: 0.15,  # 跌 10% 加仓 15%
        -0.15: 0.20,  # 跌 15% 加仓 20%
    })
    
    # 止盈规则配置
    take_profit_threshold: float = 0.30     # 止盈阈值 30%
    take_profit_ratio: float = 0.20         # 止盈比例 20%
    
    def validate(self) -> bool:
        """验证配置有效性
        
        检查投资大框架比例和基金组合比例的总和是否都为 100%。
        使用容差 0.0001 来处理浮点数精度问题。
        
        Returns:
            bool: 如果配置有效返回 True，否则返回 False
        """
        # 验证大框架比例总和为 100%
        framework_sum = (
            self.fund_portfolio_ratio +
            self.bank_fixed_income_ratio +
            self.physical_gold_ratio +
            self.reserve_fund_ratio
        )
        if abs(framework_sum - 1.0) > 0.0001:
            return False
        
        # 验证基金组合比例总和为 100%
        portfolio_sum = (
            self.bond_fund_ratio +
            self.dividend_fund_ratio +
            self.us_index_fund_ratio +
            self.gold_etf_ratio
        )
        if abs(portfolio_sum - 1.0) > 0.0001:
            return False
        
        return True
