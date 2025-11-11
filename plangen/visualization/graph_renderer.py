from __future__ import annotations

import json
import os
import time
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx

from .observers import PlanObserver


class GraphRenderer(PlanObserver):
    """
    Observer that renders plan exploration graphs.
    Supports different algorithms and rendering formats.
    """

    def __init__(
        self,
        output_dir: str = "./visualizations",
        auto_render: bool = True,
        render_format: str = "png",
    ) -> None:
        """
        Initialize the graph renderer.

        Args:
            output_dir: Directory to save rendered graphs
            auto_render: Whether to render automatically on each update
            render_format: Output format for saved graphs (png, svg, pdf)
        """
        self.output_dir = output_dir
        self.auto_render = auto_render
        self.render_format = render_format
        self.graph = nx.DiGraph()
        self.algorithm_type = None
        self.update_count = 0

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def update(self, plan_data: dict[str, Any]) -> None:
        """
        Update the graph with new plan data.

        Args:
            plan_data: Dictionary containing updated plan information
        """
        # Extract algorithm type if not already set
        if not self.algorithm_type and "algorithm_type" in plan_data:
            self.algorithm_type = plan_data["algorithm_type"]

        # Update the graph based on algorithm type
        if self.algorithm_type == "TreeOfThought":
            self._update_tree_of_thought_graph(plan_data)
        elif self.algorithm_type == "REBASE":
            self._update_rebase_graph(plan_data)
        elif self.algorithm_type == "BestOfN":
            self._update_best_of_n_graph(plan_data)
        elif self.algorithm_type == "MixtureOfAlgorithms":
            self._update_mixture_of_algorithms_graph(plan_data)
        else:
            # Generic graph update for unknown algorithm types
            self._update_generic_graph(plan_data)

        # Increment update counter
        self.update_count += 1

        # Auto-render if enabled
        if self.auto_render:
            self.render(save=True, display=False)

    def _update_tree_of_thought_graph(self, plan_data: dict[str, Any]) -> None:
        """
        Update graph for TreeOfThought algorithm.

        Args:
            plan_data: Dictionary containing tree of thought update data
        """
        if "new_nodes" in plan_data:
            for node in plan_data["new_nodes"]:
                node_id = node.get("id", f"node_{time.time()}_{id(node)}")
                parent_id = node.get("parent_id")

                # Add node with attributes
                self.graph.add_node(
                    node_id,
                    steps=node.get("steps", []),
                    score=node.get("score", 0),
                    depth=node.get("depth", 0),
                    complete=node.get("complete", False),
                    timestamp=time.time(),
                )

                # Add edge from parent if it exists
                if parent_id and parent_id in self.graph:
                    self.graph.add_edge(parent_id, node_id)

    def _update_rebase_graph(self, plan_data: dict[str, Any]) -> None:
        """
        Update graph for REBASE algorithm.

        Args:
            plan_data: Dictionary containing REBASE update data
        """
        if "iteration" in plan_data:
            iteration = plan_data["iteration"]
            node_id = f"iteration_{iteration}"
            prev_node_id = f"iteration_{iteration-1}" if iteration > 0 else None

            # Add node with attributes
            self.graph.add_node(
                node_id,
                plan=plan_data.get("plan", ""),
                score=plan_data.get("score", 0),
                feedback=plan_data.get("feedback", ""),
                timestamp=time.time(),
                iteration=iteration,
                type="rebase_step",
                label=f"Iteration {iteration}",
            )

            # Add edge from previous iteration if it exists
            if prev_node_id and prev_node_id in self.graph:
                self.graph.add_edge(
                    prev_node_id, 
                    node_id, 
                    label="refinement",
                    improvement=plan_data.get("score", 0) - self.graph.nodes[prev_node_id].get("score", 0),
                )
            
            # Add an initial node if this is the first iteration
            if iteration == 0:
                root_id = "rebase_root"
                if root_id not in self.graph:
                    self.graph.add_node(
                        root_id,
                        label="Problem Statement",
                        type="root",
                        timestamp=time.time(),
                    )
                self.graph.add_edge(root_id, node_id)

    def _update_best_of_n_graph(self, plan_data: dict[str, Any]) -> None:
        """
        Update graph for BestOfN algorithm.

        Args:
            plan_data: Dictionary containing BestOfN update data
        """
        if "plan_id" in plan_data:
            plan_id = plan_data["plan_id"]
            node_id = f"plan_{plan_id}"
            
            # Calculate a normalized score for color intensity
            score = plan_data.get("score", 0)
            is_selected = plan_data.get("is_selected", False)
            
            # Add node with attributes
            self.graph.add_node(
                node_id,
                plan=plan_data.get("plan", ""),
                score=score,
                timestamp=time.time(),
                type="plan",
                label=f"Plan {plan_id}" + (" (Selected)" if is_selected else ""),
                is_selected=is_selected,
                plan_id=plan_id,
                verification=plan_data.get("verification", ""),
            )

            # Connect to central node
            central_id = "best_of_n_root"
            if central_id not in self.graph:
                self.graph.add_node(
                    central_id, 
                    label="Problem Statement",
                    type="root",
                    timestamp=time.time(),
                )

            # Add edge with score information
            self.graph.add_edge(
                central_id, 
                node_id, 
                weight=score,
                label=f"Score: {score:.2f}",
            )
            
        # Update for selecting the best plan
        elif "best_plan_id" in plan_data:
            best_plan_id = plan_data["best_plan_id"]
            best_node_id = f"plan_{best_plan_id}"
            
            # Mark the best plan
            if best_node_id in self.graph:
                self.graph.nodes[best_node_id]["is_selected"] = True
                self.graph.nodes[best_node_id]["label"] = f"Plan {best_plan_id} (Selected)"
                
                # Add a special selected node
                selected_id = "selected_plan"
                self.graph.add_node(
                    selected_id,
                    label="Best Solution",
                    type="selected",
                    timestamp=time.time(),
                )
                
                # Connect the selected node to the best plan
                self.graph.add_edge(
                    best_node_id, 
                    selected_id, 
                    weight=1.0,
                    label="Selected",
                )

    def _update_mixture_of_algorithms_graph(self, plan_data: dict[str, Any]) -> None:
        """
        Update graph for MixtureOfAlgorithms.

        Args:
            plan_data: Dictionary containing MixtureOfAlgorithms update data
        """
        # Handle algorithm selection
        if "selected_algorithm" in plan_data:
            selected_algo = plan_data["selected_algorithm"]
            node_id = f"algo_{selected_algo}_{self.update_count}"
            
            # Add node for the selected algorithm
            self.graph.add_node(
                node_id,
                algorithm=selected_algo,
                timestamp=time.time(),
                type="algorithm",
                label=f"Selected: {selected_algo}",
                reason=plan_data.get("selection_reason", ""),
                score=plan_data.get("score", 0),
            )
            
            # Connect to root or previous algorithm
            prev_node = None
            for node, attrs in self.graph.nodes(data=True):
                if attrs.get("type") == "algorithm" and node != node_id:
                    prev_node = node
                    break
            
            # Add root if needed
            if not prev_node and "root" not in self.graph:
                self.graph.add_node(
                    "root",
                    label="Problem Statement",
                    type="root",
                    timestamp=time.time(),
                )
                self.graph.add_edge("root", node_id)
            elif prev_node:
                self.graph.add_edge(prev_node, node_id)
            else:
                self.graph.add_edge("root", node_id)
                
        # Handle algorithm-specific updates by delegating to respective handlers
        elif "delegated_algorithm" in plan_data and "algorithm_data" in plan_data:
            algo_type = plan_data["delegated_algorithm"]
            algo_data = plan_data["algorithm_data"]
            
            # Add algorithm type to the data for proper delegation
            if "algorithm_type" not in algo_data:
                algo_data["algorithm_type"] = algo_type
                
            # Delegate to the appropriate update method
            if algo_type == "TreeOfThought":
                self._update_tree_of_thought_graph(algo_data)
            elif algo_type == "REBASE":
                self._update_rebase_graph(algo_data)
            elif algo_type == "BestOfN":
                self._update_best_of_n_graph(algo_data)
        
        # Handle final selection
        elif "final_plan" in plan_data:
            final_node_id = "final_solution"
            
            # Add node for the final solution
            self.graph.add_node(
                final_node_id,
                plan=plan_data.get("final_plan", ""),
                score=plan_data.get("final_score", 0),
                timestamp=time.time(),
                type="final",
                label="Final Solution",
            )
            
            # Connect to the last algorithm node
            last_algo_node = None
            for node, attrs in self.graph.nodes(data=True):
                if attrs.get("type") == "algorithm":
                    last_algo_node = node
            
            if last_algo_node:
                self.graph.add_edge(last_algo_node, final_node_id)

    def _update_generic_graph(self, plan_data: dict[str, Any]) -> None:
        """
        Generic graph update for unknown algorithm types.

        Args:
            plan_data: Dictionary containing plan update data
        """
        node_id = f"update_{self.update_count}"
        prev_node_id = (
            f"update_{self.update_count-1}" if self.update_count > 0 else None
        )

        # Add node with timestamp and all data
        self.graph.add_node(
            node_id,
            timestamp=time.time(),
            **{
                k: v
                for k, v in plan_data.items()
                if isinstance(v, (str, int, float, bool))
            },
        )

        # Add edge from previous node if it exists
        if prev_node_id and prev_node_id in self.graph:
            self.graph.add_edge(prev_node_id, node_id)

    def render(
        self, save: bool = True, display: bool = False, filename: str | None = None,
    ) -> None:
        """
        Render the current state of the graph.

        Args:
            save: Whether to save the rendered graph to a file
            display: Whether to display the graph using matplotlib
            filename: Optional custom filename for saving
        """
        # Skip if graph is empty
        if len(self.graph) == 0:
            return

        # Clear any existing figure
        plt.figure(figsize=(12, 8))

        # Customize layout based on algorithm type
        try:
            if self.algorithm_type in {"TreeOfThought", "REBASE"}:
                pos = nx.nx_agraph.graphviz_layout(self.graph, prog="dot")
            elif self.algorithm_type == "BestOfN":
                pos = nx.spring_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)
        except Exception:
            # Fall back to spring layout if graphviz is not available
            pos = nx.spring_layout(self.graph)

        # Create node labels and colors based on algorithm type
        node_labels = {}
        node_colors = []

        for node in self.graph.nodes:
            node_data = self.graph.nodes[node]

            if self.algorithm_type == "TreeOfThought":
                score = node_data.get("score", 0)
                depth = node_data.get("depth", 0)
                complete = node_data.get("complete", False)
                # Truncate steps to first 30 chars if present
                steps_str = (
                    str(node_data.get("steps", []))[:30] + "..."
                    if "steps" in node_data
                    else ""
                )

                label = f"D{depth}\nS:{score:.2f}\n{steps_str}"
                node_labels[node] = label

                # Color complete nodes green, others by score
                if complete:
                    node_colors.append("green")
                else:
                    # Scale from red (0) to yellow (0.5) to blue (1)
                    score_norm = max(0, min(1, score))
                    if score_norm < 0.5:
                        r = 1.0
                        g = score_norm * 2
                        b = 0
                    else:
                        r = (1 - score_norm) * 2
                        g = 1.0
                        b = 0
                    node_colors.append((r, g, b))

            elif self.algorithm_type == "REBASE":
                score = node_data.get("score", 0)
                # Try to extract iteration number, handle non-numeric cases like "iter_root"
                try:
                    iteration = int(node.split("_")[1]) if "_" in node else 0
                except (ValueError, IndexError):
                    iteration = 0
                feedback = (
                    node_data.get("feedback", "")[:20] + "..."
                    if "feedback" in node_data
                    else ""
                )

                label = f"Iter {iteration}\nScore: {score:.2f}\n{feedback}"
                node_labels[node] = label
                node_colors.append("skyblue")

            elif self.algorithm_type == "BestOfN":
                if node.startswith("plan_"):
                    score = node_data.get("score", 0)
                    plan_id = node.split("_")[1]
                    label = f"Plan {plan_id}\nScore: {score:.2f}"
                    node_labels[node] = label
                    node_colors.append("lightgreen")
                else:
                    node_labels[node] = "Root"
                    node_colors.append("gray")
            else:
                # Generic labeling
                label_parts = []
                for key, value in node_data.items():
                    if key not in ["timestamp"] and isinstance(
                        value, (str, int, float, bool),
                    ):
                        label_parts.append(f"{key}: {value}")
                node_labels[node] = "\n".join(label_parts[:3])
                node_colors.append("lightblue")

        # Draw the graph
        nx.draw(
            self.graph,
            pos=pos,
            with_labels=True,
            labels=node_labels,
            node_color=node_colors,
            node_size=2000,
            font_size=8,
            font_weight="bold",
            arrows=True,
        )

        # Add title with algorithm type and timestamp
        plt.title(
            f"{self.algorithm_type or 'Unknown'} Plan Exploration - {time.strftime('%Y-%m-%d %H:%M:%S')}",
        )

        # Save the figure if requested
        if save:
            if not filename:
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = (
                    f"{self.algorithm_type or 'plan'}_{timestamp}.{self.render_format}"
                )

            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(
                filepath, format=self.render_format, dpi=300, bbox_inches="tight",
            )

        # Display the figure if requested
        if display:
            plt.show()
        else:
            plt.close()

    def save_graph_data(self, filename: str | None = None) -> None:
        """
        Save the current graph data as JSON.

        Args:
            filename: Optional custom filename for saving
        """
        if not filename:
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"{self.algorithm_type or 'plan'}_{timestamp}_data.json"

        filepath = os.path.join(self.output_dir, filename)

        # Convert graph to serializable format
        graph_data = {"nodes": [], "edges": []}

        for node in self.graph.nodes:
            node_data = dict(self.graph.nodes[node])
            # Convert non-serializable values to strings
            for key, value in node_data.items():
                if not isinstance(
                    value, (str, int, float, bool, list, dict, type(None)),
                ):
                    node_data[key] = str(value)

            graph_data["nodes"].append({"id": node, "data": node_data})

        for source, target in self.graph.edges:
            graph_data["edges"].append({"source": source, "target": target})

        with open(filepath, "w") as f:
            json.dump(graph_data, f, indent=2)

        return filepath
