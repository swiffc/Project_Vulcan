"""
Knowledge Graph - Deep Memory Consolidation

Implements long-term memory with relationship graphs.
Consolidates short-term RAG data into persistent knowledge structures.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger("core.memory.knowledge_graph")

# Knowledge graph storage
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


class Node:
    """A node in the knowledge graph."""

    def __init__(
        self,
        id: str,
        type: str,
        label: str,
        properties: Dict[str, Any] = None,
        created_at: datetime = None
    ):
        self.id = id
        self.type = type  # strategy, part, standard, material, error, etc.
        self.label = label
        self.properties = properties or {}
        self.created_at = created_at or datetime.utcnow()
        self.last_accessed = self.created_at

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Node":
        node = cls(
            id=data["id"],
            type=data["type"],
            label=data["label"],
            properties=data.get("properties", {}),
            created_at=datetime.fromisoformat(data["created_at"])
        )
        if "last_accessed" in data:
            node.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return node


class Edge:
    """A relationship edge in the knowledge graph."""

    def __init__(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        properties: Dict[str, Any] = None
    ):
        self.source = source
        self.target = target
        self.relation = relation  # uses, similar_to, evolved_from, failed_with, etc.
        self.weight = weight
        self.properties = properties or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Edge":
        edge = cls(
            source=data["source"],
            target=data["target"],
            relation=data["relation"],
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {})
        )
        if "created_at" in data:
            edge.created_at = datetime.fromisoformat(data["created_at"])
        return edge


class KnowledgeGraph:
    """
    Knowledge graph for long-term memory consolidation.

    Stores:
    - Strategies and their relationships
    - Parts and components
    - Standards and their requirements
    - Error patterns and solutions
    - Material specifications
    """

    def __init__(self, graph_file: str = "knowledge_graph.json"):
        self.graph_file = KNOWLEDGE_DIR / graph_file
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self._adjacency: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
        self._load()

    def _load(self):
        """Load graph from disk."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file) as f:
                    data = json.load(f)

                for node_data in data.get("nodes", []):
                    node = Node.from_dict(node_data)
                    self.nodes[node.id] = node

                for edge_data in data.get("edges", []):
                    edge = Edge.from_dict(edge_data)
                    self.edges.append(edge)
                    self._adjacency[edge.source].append((edge.target, edge.relation, edge.weight))

                logger.info(f"Loaded knowledge graph: {len(self.nodes)} nodes, {len(self.edges)} edges")
            except Exception as e:
                logger.error(f"Failed to load knowledge graph: {e}")

    def _save(self):
        """Save graph to disk."""
        try:
            data = {
                "nodes": [n.to_dict() for n in self.nodes.values()],
                "edges": [e.to_dict() for e in self.edges],
                "metadata": {
                    "saved_at": datetime.utcnow().isoformat(),
                    "node_count": len(self.nodes),
                    "edge_count": len(self.edges)
                }
            }
            with open(self.graph_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")

    def add_node(
        self,
        id: str,
        type: str,
        label: str,
        properties: Dict = None
    ) -> Node:
        """Add or update a node."""
        if id in self.nodes:
            node = self.nodes[id]
            node.properties.update(properties or {})
            node.last_accessed = datetime.utcnow()
        else:
            node = Node(id, type, label, properties)
            self.nodes[id] = node

        self._save()
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        properties: Dict = None
    ) -> Edge:
        """Add a relationship edge."""
        # Check if edge already exists
        for edge in self.edges:
            if edge.source == source and edge.target == target and edge.relation == relation:
                edge.weight = max(edge.weight, weight)  # Strengthen connection
                self._save()
                return edge

        edge = Edge(source, target, relation, weight, properties)
        self.edges.append(edge)
        self._adjacency[source].append((target, relation, weight))
        self._save()
        return edge

    def get_node(self, id: str) -> Optional[Node]:
        """Get a node by ID."""
        node = self.nodes.get(id)
        if node:
            node.last_accessed = datetime.utcnow()
        return node

    def get_neighbors(
        self,
        node_id: str,
        relation: str = None,
        depth: int = 1
    ) -> List[Dict]:
        """Get neighboring nodes."""
        visited = set()
        result = []

        def traverse(nid: str, current_depth: int):
            if current_depth > depth or nid in visited:
                return
            visited.add(nid)

            for target, rel, weight in self._adjacency.get(nid, []):
                if relation is None or rel == relation:
                    node = self.nodes.get(target)
                    if node:
                        result.append({
                            "node": node.to_dict(),
                            "relation": rel,
                            "weight": weight,
                            "depth": current_depth
                        })
                        traverse(target, current_depth + 1)

        traverse(node_id, 1)
        return result

    def find_path(self, source: str, target: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find path between two nodes using BFS."""
        if source not in self.nodes or target not in self.nodes:
            return None

        visited = {source}
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path

            if len(path) >= max_depth:
                continue

            for neighbor, _, _ in self._adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_related(
        self,
        node_type: str,
        limit: int = 10
    ) -> List[Node]:
        """Get all nodes of a specific type."""
        nodes = [n for n in self.nodes.values() if n.type == node_type]
        nodes.sort(key=lambda x: x.last_accessed, reverse=True)
        return nodes[:limit]

    def search(self, query: str, node_type: str = None) -> List[Node]:
        """Search nodes by label or properties."""
        query_lower = query.lower()
        results = []

        for node in self.nodes.values():
            if node_type and node.type != node_type:
                continue

            if query_lower in node.label.lower():
                results.append(node)
            elif any(query_lower in str(v).lower() for v in node.properties.values()):
                results.append(node)

        return results

    def consolidate_from_rag(self, rag_results: List[Dict]):
        """
        Consolidate RAG search results into knowledge graph.
        Called periodically to build long-term memory.
        """
        for result in rag_results:
            doc_id = result.get("id", result.get("metadata", {}).get("id"))
            doc_type = result.get("type", result.get("metadata", {}).get("type", "document"))
            content = result.get("content", result.get("document", ""))

            if doc_id:
                self.add_node(
                    id=f"doc_{doc_id}",
                    type=doc_type,
                    label=content[:100] if content else doc_id,
                    properties=result.get("metadata", {})
                )

        logger.info(f"Consolidated {len(rag_results)} RAG results into knowledge graph")

    def add_strategy_knowledge(self, strategy: Dict):
        """Add strategy and its relationships to the graph."""
        strategy_id = f"strategy_{strategy.get('id', strategy.get('name'))}"

        # Add strategy node
        self.add_node(
            id=strategy_id,
            type="strategy",
            label=strategy.get("name", "Unknown"),
            properties={
                "product_type": strategy.get("product_type"),
                "performance_score": strategy.get("performance_score"),
                "version": strategy.get("version")
            }
        )

        # Add material relationship
        material = strategy.get("material", {})
        if material:
            material_id = f"material_{material.get('name', 'unknown')}"
            self.add_node(
                id=material_id,
                type="material",
                label=material.get("name", "Unknown Material"),
                properties=material
            )
            self.add_edge(strategy_id, material_id, "uses_material")

        # Add constraint relationships
        for constraint in strategy.get("constraints", []):
            if constraint.get("standard"):
                std_id = f"standard_{constraint['standard']}"
                self.add_node(
                    id=std_id,
                    type="standard",
                    label=constraint["standard"],
                    properties={}
                )
                self.add_edge(strategy_id, std_id, "follows_standard")

    def add_error_pattern(
        self,
        strategy_id: str,
        error_type: str,
        error_details: Dict
    ):
        """Record error patterns for learning."""
        error_id = f"error_{error_type}"

        self.add_node(
            id=error_id,
            type="error",
            label=error_type,
            properties={"count": error_details.get("count", 1)}
        )

        self.add_edge(
            f"strategy_{strategy_id}",
            error_id,
            "failed_with",
            weight=error_details.get("frequency", 1.0)
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        type_counts = defaultdict(int)
        for node in self.nodes.values():
            type_counts[node.type] += 1

        relation_counts = defaultdict(int)
        for edge in self.edges:
            relation_counts[edge.relation] += 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(type_counts),
            "relation_types": dict(relation_counts)
        }

    def prune_old(self, days: int = 90):
        """Remove nodes not accessed in X days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        old_nodes = [
            nid for nid, node in self.nodes.items()
            if node.last_accessed < cutoff
        ]

        for nid in old_nodes:
            del self.nodes[nid]
            self.edges = [e for e in self.edges if e.source != nid and e.target != nid]

        self._rebuild_adjacency()
        self._save()
        logger.info(f"Pruned {len(old_nodes)} old nodes from knowledge graph")

    def _rebuild_adjacency(self):
        """Rebuild adjacency list from edges."""
        self._adjacency.clear()
        for edge in self.edges:
            self._adjacency[edge.source].append((edge.target, edge.relation, edge.weight))


# Singleton
_knowledge_graph: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get or create knowledge graph singleton."""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph
