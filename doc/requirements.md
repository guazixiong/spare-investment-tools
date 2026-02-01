# 需求文档：投资管理计算器

## 简介

投资管理计算器是一个基于 Python 的 Web 服务，用于帮助用户根据投资策略 v2.0 自动计算和管理个人投资分配。该工具将用户的可投资金额按照预定义的比例分配到不同的投资产品中，并提供定投计划和动态调整功能。系统通过 HTTP API 对外提供服务，支持通过配置文件动态调整投资比例。

## 术语表

- **系统（System）**：投资管理计算器 Excel 工具
- **用户（User）**：使用该工具管理个人投资的个人
- **可投资金额（Investable_Amount）**：总资产减去生活费和负债后的金额
- **基金组合（Fund_Portfolio）**：包含中短债、红利低波、标普/纳指、黄金 ETF 的投资组合
- **持仓成本（Holding_Cost）**：基金的平均买入价格
- **当前净值（Current_NAV）**：基金的当前单位净值
- **定投（Regular_Investment）**：定期定额投资策略
- **加仓（Add_Position）**：在价格下跌时增加投资金额
- **止盈（Take_Profit）**：在收益达到目标时卖出部分持仓

## 需求

### 需求 1：HTTP API 接口

**用户故事**：作为用户，我想要通过 HTTP 请求调用投资计算服务，以便我可以从任何客户端获取投资分配建议。

#### 验收标准

1. THE System SHALL 提供 HTTP POST 接口用于接收财务数据并返回投资分配结果
2. THE System SHALL 接受 JSON 格式的请求数据
3. THE System SHALL 返回 JSON 格式的响应数据
4. THE System SHALL 在请求参数缺失或无效时返回 400 错误和错误信息
5. THE System SHALL 在服务器内部错误时返回 500 错误和错误信息
6. THE System SHALL 支持跨域请求（CORS）

### 需求 2：用户输入管理

**用户故事**：作为用户，我想要通过 API 提交我的财务数据，以便系统能够计算我的投资分配。

#### 验收标准

1. THE System SHALL 接受生活费 1.5 月固定金额（目标金额）参数
2. THE System SHALL 接受剩余生活费金额（当前实际金额）参数
3. THE System SHALL 接受负债金额参数
4. THE System SHALL 接受新增收入金额参数
5. WHEN 用户提交任何财务数据 THEN THE System SHALL 验证输入为非负数值
6. WHEN 输入验证失败 THEN THE System SHALL 返回详细的错误信息

### 需求 3：可投资金额计算

**用户故事**：作为用户，我想要系统自动计算我的可投资金额，以便我知道有多少资金可以用于投资。

#### 验收标准

1. THE System SHALL 计算生活费缺口为：MAX(0, 生活费 1.5 月固定金额 - 剩余生活费金额)
2. THE System SHALL 计算可投资金额为：新增收入 - 生活费缺口 - 负债
3. THE System SHALL 在响应中返回生活费缺口金额
4. THE System SHALL 在响应中返回计算后的可投资金额
5. WHEN 可投资金额 ≤ 0 THEN THE System SHALL 在响应中包含警告信息
6. THE System SHALL 在响应中返回资金分配明细（生活费补充、负债偿还、可投资金额）

### 需求 4：投资大框架分配

**用户故事**：作为用户，我想要系统按照策略自动分配我的投资金额到不同类别，以便我了解整体投资结构。

#### 验收标准

1. THE System SHALL 分配可投资金额的 30% 到基金组合
2. THE System SHALL 分配可投资金额的 60% 到银行固收 R2
3. THE System SHALL 分配可投资金额的 5% 到实体黄金（积存金）
4. THE System SHALL 分配可投资金额的 5% 到备用金
5. THE System SHALL 在响应中返回每个类别的具体金额
6. THE System SHALL 验证所有分配比例总和为 100%

### 需求 5：基金组合内部分配

**用户故事**：作为用户，我想要系统自动分配基金组合内部的资金到各个基金，以便我知道每个基金应该投资多少。

#### 验收标准

1. THE System SHALL 分配基金组合金额的 40% 到中短债基金
2. THE System SHALL 分配基金组合金额的 30% 到红利低波/沪深300
3. THE System SHALL 分配基金组合金额的 15% 到标普/纳指
4. THE System SHALL 分配基金组合金额的 15% 到黄金 ETF 联接 C
5. THE System SHALL 在响应中返回每个基金的具体投资金额
6. THE System SHALL 验证基金组合内部分配比例总和为 100%

### 需求 6：定投计划生成

**用户故事**：作为用户，我想要系统生成每周的定投计划，以便我知道每周应该定投多少金额到哪些基金。

#### 验收标准

1. THE System SHALL 计算周二定投金额为：标普/纳指分配金额
2. THE System SHALL 计算周四定投金额为：中短债 + 红利低波 + 黄金 ETF 分配金额
3. THE System SHALL 在响应中返回周二定投的基金列表和金额
4. THE System SHALL 在响应中返回周四定投的基金列表和金额
5. THE System SHALL 在响应中返回每周总定投金额

### 需求 6：配置管理

**用户故事**：作为开发者，我想要通过配置类来管理投资比例，以便我可以动态调整投资策略而无需修改核心逻辑代码。

#### 验收标准

1. THE System SHALL 提供配置类用于定义投资大框架的分配比例（基金组合、银行固收、实体黄金、备用金）
2. THE System SHALL 提供配置类用于定义基金组合内部的分配比例（中短债、红利低波、标普/纳指、黄金 ETF）
3. THE System SHALL 提供配置类用于定义加仓规则的阈值和比例
4. THE System SHALL 提供配置类用于定义止盈规则的阈值和比例
5. THE System SHALL 在配置修改后无需重启服务即可生效（支持热重载）
6. THE System SHALL 验证配置的有效性（如比例总和为 100%）

### 需求 7：Web 用户界面

**用户故事**：作为用户，我想要通过 Web 界面输入财务数据并查看投资分配结果，以便我可以方便地使用该工具。

#### 验收标准

1. THE System SHALL 提供静态 HTML 页面作为用户界面
2. THE System SHALL 在界面上提供输入表单用于填写财务数据（生活费、负债、新增收入）
3. THE System SHALL 在用户提交数据后通过 AJAX 调用后端 API
4. THE System SHALL 在界面上动态展示计算结果（可投资金额、投资分配、定投计划）
5. THE System SHALL 在界面上使用清晰的布局区分输入区和结果展示区
6. THE System SHALL 在界面上实时验证用户输入（非负数、必填项）
7. THE System SHALL 在界面上显示错误提示和警告信息

### 需求 8：加仓规则计算

**用户故事**：作为用户，我想要系统根据基金净值变化自动计算加仓金额，以便我在市场下跌时知道应该加仓多少。

#### 验收标准

1. WHEN 基金当前净值 ≤ 持仓成本 - 5% THEN THE System SHALL 计算加仓金额为当前持仓金额 × 10%
2. WHEN 基金当前净值 ≤ 持仓成本 - 10% THEN THE System SHALL 计算额外加仓金额为当前持仓金额 × 15%
3. WHEN 基金当前净值 ≤ 持仓成本 - 15% THEN THE System SHALL 计算额外加仓金额为当前持仓金额 × 20%
4. THE System SHALL 仅对红利低波/沪深300、标普/纳指、黄金 ETF 应用加仓规则
5. THE System SHALL 显示每个符合条件基金的建议加仓金额
6. THE System SHALL 计算总加仓金额

### 需求 9：止盈规则计算

**用户故事**：作为用户，我想要系统根据基金收益率自动计算止盈金额，以便我在收益达标时知道应该卖出多少。

#### 验收标准

1. WHEN 基金整体收益率 ≥ +30% THEN THE System SHALL 计算止盈金额为该基金持仓金额 × 20%
2. THE System SHALL 仅对红利低波/沪深300、标普/纳指、黄金 ETF 应用止盈规则
3. THE System SHALL 显示每个符合条件基金的建议止盈金额
4. THE System SHALL 计算总止盈金额

### 需求 10：持仓数据管理

**用户故事**：作为用户，我想要记录和更新我的基金持仓数据，以便系统能够准确计算加仓和止盈建议。

#### 验收标准

1. THE System SHALL 提供输入区域用于记录每个基金的持仓成本
2. THE System SHALL 提供输入区域用于记录每个基金的当前净值
3. THE System SHALL 提供输入区域用于记录每个基金的当前持仓金额
4. THE System SHALL 计算每个基金的收益率：(当前净值 - 持仓成本) / 持仓成本 × 100%
5. THE System SHALL 显示每个基金的收益率

### 需求 11：动态调整和重新计算

**用户故事**：作为用户，我想要在更新任何输入数据时系统自动重新计算所有投资分配，以便我始终看到最新的投资计划。

#### 验收标准

1. WHEN 用户更新生活费金额 THEN THE System SHALL 自动重新计算所有投资分配
2. WHEN 用户更新负债金额 THEN THE System SHALL 自动重新计算所有投资分配
3. WHEN 用户更新新增收入金额 THEN THE System SHALL 自动重新计算所有投资分配
4. THE System SHALL 在数据更新后立即返回更新后的结果

### 需求 12：数据展示和可视化

**用户故事**：作为用户，我想要清晰地看到我的投资结构和分配情况，以便我能够快速理解我的投资组合。

#### 验收标准

1. THE System SHALL 使用清晰的区域划分展示输入区和计算区
2. THE System SHALL 使用分层结构展示投资大框架和基金组合小框架
3. THE System SHALL 使用不同的颜色或格式区分输入单元格和计算单元格
4. THE System SHALL 显示所有金额时保留两位小数
5. THE System SHALL 显示所有百分比时保留两位小数

### 需求 11：数据验证和错误处理

**用户故事**：作为用户，我想要系统验证我的输入数据并提示错误，以便我能够及时纠正错误的输入。

#### 验收标准

1. WHEN 用户输入非数值数据 THEN THE System SHALL 显示错误提示
2. WHEN 用户输入负数 THEN THE System SHALL 显示错误提示
3. WHEN 可投资金额为负数 THEN THE System SHALL 显示警告信息
4. THE System SHALL 保护计算公式单元格不被意外修改
5. THE System SHALL 在输入单元格旁边提供说明文字

### 需求 12：输入说明和提示

**用户故事**：作为用户，我想要看到清晰的输入说明，以便我知道每个输入项的含义和如何填写。

#### 验收标准

1. THE System SHALL 在生活费 1.5 月固定金额输入区域旁显示说明："目标生活费储备金额（1.5-2 个月）"
2. THE System SHALL 在剩余生活费金额输入区域旁显示说明："当前实际拥有的生活费金额"
3. THE System SHALL 在负债输入区域旁显示说明："当前需要偿还的负债总额"
4. THE System SHALL 在新增收入输入区域旁显示说明："本月新增的可支配收入"
5. THE System SHALL 在输入单元格使用不同颜色标识以区分计算单元格

### 需求 13：持仓占比分析工具

**用户故事**：作为用户，我想要在前端页面使用一个工具来分析我的当前持仓占比是否符合预期配置，以便我能够及时调整投资策略。

#### 验收标准

1. THE System SHALL 在前端页面提供"持仓分析"工具选项，供用户进入持仓占比分析功能
2. THE System SHALL 接受用户输入各基金的当前持仓金额（中短债、红利低波、标普/纳指、黄金ETF、银行固收、实体黄金、备用金）
3. THE System SHALL 通过HTTP API将持仓数据发送到后端服务进行计算
4. THE System SHALL 在后端计算当前各投资类别的实际占比（基金组合、银行固收、实体黄金、备用金）
5. THE System SHALL 在后端计算基金组合内部各基金的实际占比（中短债、红利低波、标普/纳指、黄金ETF）
6. THE System SHALL 在后端将实际占比与预期配置比例进行对比分析
7. THE System SHALL 在响应中返回各投资类别的预期占比、实际占比和偏差值
8. THE System SHALL 在响应中标记偏差超过±5%的类别为需要调整
9. THE System SHALL 在响应中提供调整建议（如"建议增持"、"建议减持"、"配置合理"）
10. THE System SHALL 在前端页面以表格和图表形式直观展示持仓分析结果
11. THE System SHALL 在界面上使用颜色编码区分：绿色（配置合理）、黄色（轻微偏离）、红色（严重偏离）
12. THE System SHALL 在界面上显示总计持仓金额
