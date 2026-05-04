---
name: tiancai-timeline-convergence
version: 1.0.0
category: systems-thinking
source: 《天才俱乐部》
author: extracted_from_novel
description: |
  识别关键节点，理解小改变如何引发大影响。
  应用于战略规划和预测，监控早期信号以预测系统性变化。
tags: [systems-thinking, causality, prediction, strategy]
---

# 时间线收敛推理

## 核心理论

> "每次梦境改变都会影响现实（世界线收敛）"
> 
> — 《天才俱乐部》

## 应用场景

- 战略规划中的关键节点识别
- 复杂系统中的敏感点分析
- 长期预测与趋势分析
- 危机预警与干预策略

## 操作步骤

1. **识别系统中的敏感节点**
   - 绘制系统图，标识所有组成部分
   - 分析各组成部分之间的依赖关系
   - 找出对系统影响最大的关键节点

2. **理解因果链的传播机制**
   - 场景A：直接因果（诱因→结果）
   - 场景B：倒果因（因管制时序）
   - 场景C：迭代收敛（反复优化）
   - 场景D：并发收敛（多线程合并）

3. **评估不同干预的杠杆效应**
   - 计算收益 = (最终结果 - 无干预结果) / 成本
   - 权衡风险与收益比
   - 考虑时间因素

4. **监控早期信号以预测系统性变化**
   - 设立关键指标预警阈值
   - 建立趋势分析体系
   - 制定应急响应预案

## 示例代码

```python
# 时间线收敛推理的Python实现示例
import networkx as nx
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum

class ConvergenceType(Enum):
    DIRECT_CAUSAL = "direct_causal"      # 直接因果
    REVERSE_CAUSAL = "reverse_causal"    # 倒果因
    ITERATIVE = "iterative"              # 迭代收敛
    CONCURRENT = "concurrent"            # 并发收敛

@dataclass
class Node:
    """系统节点"""
    id: str
    name: str
    sensitivity: float  # 敏感度 0-1
    impact_radius: List[str]  # 影响范围
    
@dataclass
class Intervention:
    """干预策略"""
    id: str
    target_node: str
    action: str
    cost: float
    expected_impact: float
    risk_level: float  # 0-1
    
class TimelineConvergenceAnalyzer:
    """
    时间线收敛推理分析器
    
    用于识别系统中的敏感节点，预测小改变的大影响
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self.convergence_history = []
        
    def add_node(self, node: Node):
        """添加系统节点"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, 
                           name=node.name, 
                           sensitivity=node.sensitivity)
        
    def add_dependency(self, from_node: str, to_node: str, weight: float = 1.0):
        """
        添加节点依赖关系
        
        Args:
            from_node: 因节点
            to_node: 果节点
            weight: 依赖强度 0-1
        """
        self.graph.add_edge(from_node, to_node, weight=weight)
        
    def identify_sensitive_nodes(self, threshold: float = 0.7) -> List[Node]:
        """
        识别敏感节点
        
        通过结合节点自身敏感度和在图中的中心性
        
        Args:
            threshold: 敏感度阈值
            
        Returns:
            敏感节点列表
        """
        sensitive = []
        
        # 计算每个节点的中心性（影响范围）
        centrality = nx.pagerank(self.graph)
        
        for node_id, node in self.nodes.items():
            # 综合评分 = 自身敏感度 * 图中心性
            sensitivity_score = node.sensitivity * centrality.get(node_id, 0.5)
            
            if sensitivity_score >= threshold:
                sensitive.append(node)
                
        return sorted(sensitive, key=lambda n: n.sensitivity, reverse=True)
        
    def predict_convergence(self, intervention: Intervention) -> Dict:
        """
        预测干预的收敛结果
        
        分析对特定节点的干预如何传播并最终收敛
        
        Args:
            intervention: 干预策略
            
        Returns:
            收敛预测结果
        """
        target = intervention.target_node
        
        # 计算影响范围（可达节点）
        reachable = nx.descendants(self.graph, target)
        
        # 估算影响强度（递减）
        impact_strength = intervention.expected_impact
        for node in reachable:
            # 每经过一层，影响力递减
            path_length = nx.shortest_path_length(self.graph, target, node)
            decayed_impact = impact_strength * (0.5 ** path_length)
            
        # 收益/风险比例
        roi = (intervention.expected_impact - intervention.cost) / intervention.risk_level if intervention.risk_level > 0 else float('inf')
        
        return {
            'intervention_id': intervention.id,
            'target_node': target,
            'impact_radius': len(reachable),
            'affected_nodes': list(reachable),
            'roi': roi,
            'risk_level': intervention.risk_level,
            'convergence_type': self._determine_convergence_type(intervention, reachable)
        }
        
    def _determine_convergence_type(self, intervention: Intervention, affected: Set[str]) -> ConvergenceType:
        """确定收敛类型"""
        if len(affected) == 0:
            return ConvergenceType.ITERATIVE
        elif len(affected) == 1:
            return ConvergenceType.DIRECT_CAUSAL
        elif intervention.risk_level > 0.8:
            return ConvergenceType.REVERSE_CAUSAL
        else:
            return ConvergenceType.CONCURRENT
            
    def get_convergence_history(self) -> List[Dict]:
        """获取收敛历史记录"""
        return self.convergence_history.copy()


# 使用示例
def example_usage():
    """时间线收敛推理使用示例"""
    
    # 创建分析器
    analyzer = TimelineConvergenceAnalyzer()
    
    # 添加节点
    nodes = [
        Node("tech", "科技发展", 0.9, ["econ", "social"]),
        Node("econ", "经济形势", 0.8, ["politics", "culture"]),
        Node("social", "社会结构", 0.7, ["culture"]),
        Node("politics", "政治格局", 0.85, ["tech", "econ"]),
        Node("culture", "文化趋势", 0.6, ["tech", "social"])
    ]
    
    for node in nodes:
        analyzer.add_node(node)
        
    # 添加依赖关系
    analyzer.add_dependency("tech", "econ", 0.8)
    analyzer.add_dependency("tech", "social", 0.6)
    analyzer.add_dependency("econ", "politics", 0.7)
    analyzer.add_dependency("econ", "culture", 0.5)
    analyzer.add_dependency("social", "culture", 0.4)
    analyzer.add_dependency("politics", "tech", 0.9)
    analyzer.add_dependency("politics", "econ", 0.6)
    analyzer.add_dependency("culture", "tech", 0.3)
    analyzer.add_dependency("culture", "social", 0.5)
    
    # 识别敏感节点
    sensitive = analyzer.identify_sensitive_nodes(threshold=0.7)
    print("敏感节点:")
    for node in sensitive:
        print(f"  - {node.name} (敏感度: {node.sensitivity})")
        
    # 模拟干预
    intervention = Intervention(
        id="tech_boost",
        target_node="tech",
        action="大幅提高科技投入",
        cost=1000,
        expected_impact=2.0,
        risk_level=0.3
    )
    
    prediction = analyzer.predict_convergence(intervention)
    print(f"\n干预预测:")
    print(f"  影响范围: {prediction['impact_radius']} 个节点")
    print(f"  收益/风险比: {prediction['roi']:.2f}")
    print(f"  收敛类型: {prediction['convergence_type']}")

if __name__ == "__main__":
    example_usage()
