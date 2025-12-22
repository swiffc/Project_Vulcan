"""
Reference Tracker Adapter (Phase 12)

Tracks assembly references and dependencies in CAD files.
Maps parent-child relationships and detects circular references.

Pattern: Adapter (analyzes SolidWorks/Inventor assemblies)
Uses: SolidWrap, pywin32 COM

Usage:
    tracker = ReferenceTracker()
    refs = await tracker.get_references("Assembly-01.SLDASM")
    deps = await tracker.get_dependencies("Bracket.SLDPRT")
    circular = tracker.detect_circular_refs()
"""

import logging
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, deque

logger = logging.getLogger("cad_agent.reference_tracker")


@dataclass
class FileReference:
    """A file reference (parent -> child relationship)."""
    parent_file: str
    child_file: str
    instance_count: int = 1
    ref_type: str = "component"  # component, drawing, derived, mirror


@dataclass
class DependencyTree:
    """Dependency tree for a file."""
    root_file: str
    children: List[str] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)
    level: int = 0  # Depth in tree
    total_dependencies: int = 0


class ReferenceTracker:
    """
    Tracks assembly references and dependencies.
    
    Features:
    - Build dependency graph
    - Find all references (where-used)
    - Find all dependencies (what uses this)
    - Detect circular references
    - Calculate assembly depth
    - Export to visualization formats
    
    Use Cases:
    - "What assemblies use Part-123?"
    - "What parts does Assembly-01 need?"
    - "Are there any circular references?"
    - "How deep is this assembly tree?"
    """

    def __init__(self):
        """Initialize reference tracker."""
        self._references: List[FileReference] = []
        self._graph: Dict[str, Set[str]] = defaultdict(set)  # parent -> children
        self._reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # child -> parents
        self._solidwrap = None
        self._sw_app = None

    def _lazy_import_solidwrap(self):
        """Lazy import SolidWrap."""
        if self._solidwrap is None:
            try:
                import solidwrap
                self._solidwrap = solidwrap
                logger.info("SolidWrap loaded for reference tracking")
            except ImportError:
                logger.warning("SolidWrap not installed - limited functionality")

    async def connect_solidworks(self) -> bool:
        """Connect to SolidWorks for live analysis."""
        self._lazy_import_solidwrap()
        
        if not self._solidwrap:
            return False
        
        try:
            self._sw_app = self._solidwrap.connect()
            logger.info("Connected to SolidWorks for reference tracking")
            return True
        except Exception as e:
            logger.error(f"SolidWorks connection failed: {e}")
            return False

    def add_reference(self, parent: str, child: str, instance_count: int = 1, ref_type: str = "component"):
        """
        Add a parent-child reference.
        
        Args:
            parent: Parent file path
            child: Child file path
            instance_count: Number of instances
            ref_type: Type of reference (component, drawing, etc.)
        """
        # Normalize paths
        parent = str(Path(parent).resolve())
        child = str(Path(child).resolve())
        
        # Add to references list
        self._references.append(FileReference(
            parent_file=parent,
            child_file=child,
            instance_count=instance_count,
            ref_type=ref_type
        ))
        
        # Update graphs
        self._graph[parent].add(child)
        self._reverse_graph[child].add(parent)
        
        logger.debug(f"Added reference: {Path(parent).name} -> {Path(child).name}")

    async def analyze_assembly(self, assembly_path: str) -> List[FileReference]:
        """
        Analyze an assembly file and extract all references.
        
        Args:
            assembly_path: Path to assembly file (.SLDASM or .IAM)
            
        Returns:
            List of FileReference objects
            
        Example:
            refs = await tracker.analyze_assembly("Assembly-01.SLDASM")
            for ref in refs:
                print(f"{ref.parent_file} uses {ref.child_file}")
        """
        assembly_path = str(Path(assembly_path).resolve())
        
        if not self._sw_app and not await self.connect_solidworks():
            logger.error("Cannot analyze assembly - SolidWorks not connected")
            return []

        try:
            # Open assembly
            doc = self._sw_app.open_doc(assembly_path)
            
            # Get all components
            components = doc.get_components()
            
            refs = []
            for comp in components:
                comp_path = comp.get_path_name()
                instance_count = comp.get_instance_count()
                
                ref = FileReference(
                    parent_file=assembly_path,
                    child_file=comp_path,
                    instance_count=instance_count,
                    ref_type="component"
                )
                refs.append(ref)
                self.add_reference(assembly_path, comp_path, instance_count)
            
            logger.info(f"Analyzed assembly: {Path(assembly_path).name} ({len(refs)} refs)")
            return refs
            
        except Exception as e:
            logger.error(f"Assembly analysis failed: {e}")
            return []

    def get_dependencies(self, file_path: str) -> List[str]:
        """
        Get all files that this file depends on (children).
        
        Args:
            file_path: File to analyze
            
        Returns:
            List of child file paths
            
        Example:
            deps = tracker.get_dependencies("Assembly-01.SLDASM")
            print(f"Assembly needs {len(deps)} parts")
        """
        file_path = str(Path(file_path).resolve())
        
        # BFS to get all dependencies
        visited = set()
        queue = deque([file_path])
        dependencies = []
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            
            visited.add(current)
            
            # Add children
            children = self._graph.get(current, set())
            for child in children:
                if child not in visited:
                    dependencies.append(child)
                    queue.append(child)
        
        return dependencies

    def get_references(self, file_path: str) -> List[str]:
        """
        Get all files that reference this file (parents).
        
        Args:
            file_path: File to analyze
            
        Returns:
            List of parent file paths (where-used)
            
        Example:
            parents = tracker.get_references("Bracket.SLDPRT")
            print(f"Bracket is used in {len(parents)} assemblies")
        """
        file_path = str(Path(file_path).resolve())
        
        # BFS to get all references
        visited = set()
        queue = deque([file_path])
        references = []
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            
            visited.add(current)
            
            # Add parents
            parents = self._reverse_graph.get(current, set())
            for parent in parents:
                if parent not in visited:
                    references.append(parent)
                    queue.append(parent)
        
        return references

    def detect_circular_refs(self) -> List[Tuple[str, str]]:
        """
        Detect circular references in assembly structure.
        
        Returns:
            List of (file1, file2) tuples forming circular refs
            
        Example:
            circular = tracker.detect_circular_refs()
            if circular:
                print("WARNING: Circular references detected!")
                for file1, file2 in circular:
                    print(f"  {file1} <-> {file2}")
        """
        circular = []
        
        # DFS to detect cycles
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self._graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        circular.append((node, neighbor))
                        return True
                elif neighbor in rec_stack:
                    circular.append((node, neighbor))
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in self._graph:
            if node not in visited:
                has_cycle(node, visited, set())
        
        if circular:
            logger.warning(f"Detected {len(circular)} circular references")
        
        return circular

    def get_assembly_depth(self, root_file: str) -> int:
        """
        Calculate maximum depth of assembly tree.
        
        Args:
            root_file: Root assembly file
            
        Returns:
            Maximum depth (0 = no children, 1 = direct children only, etc.)
        """
        root_file = str(Path(root_file).resolve())
        
        def dfs_depth(node: str, visited: Set[str]) -> int:
            if node in visited:
                return 0
            
            visited.add(node)
            children = self._graph.get(node, set())
            
            if not children:
                return 0
            
            max_child_depth = 0
            for child in children:
                depth = dfs_depth(child, visited.copy())
                max_child_depth = max(max_child_depth, depth)
            
            return max_child_depth + 1
        
        depth = dfs_depth(root_file, set())
        logger.info(f"Assembly depth for {Path(root_file).name}: {depth}")
        return depth

    def build_dependency_tree(self, root_file: str) -> DependencyTree:
        """
        Build complete dependency tree for a file.
        
        Args:
            root_file: Root file to analyze
            
        Returns:
            DependencyTree object
        """
        root_file = str(Path(root_file).resolve())
        
        children = list(self._graph.get(root_file, set()))
        parents = list(self._reverse_graph.get(root_file, set()))
        all_deps = self.get_dependencies(root_file)
        depth = self.get_assembly_depth(root_file)
        
        return DependencyTree(
            root_file=root_file,
            children=children,
            parents=parents,
            level=depth,
            total_dependencies=len(all_deps)
        )

    def export_to_dict(self) -> Dict[str, any]:
        """
        Export reference graph to dictionary format.
        
        Returns:
            Dict with nodes and edges
        """
        return {
            "nodes": list(set(self._graph.keys()) | set(self._reverse_graph.keys())),
            "edges": [
                {"source": ref.parent_file, "target": ref.child_file, "count": ref.instance_count}
                for ref in self._references
            ],
            "total_files": len(set(self._graph.keys()) | set(self._reverse_graph.keys())),
            "total_references": len(self._references)
        }

    def clear(self):
        """Clear all tracked references."""
        self._references.clear()
        self._graph.clear()
        self._reverse_graph.clear()
        logger.info("Reference tracker cleared")


# Singleton instance
_tracker_instance: Optional[ReferenceTracker] = None


def get_reference_tracker() -> ReferenceTracker:
    """Get singleton instance of reference tracker."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ReferenceTracker()
    return _tracker_instance
