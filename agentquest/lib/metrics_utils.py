"""Utils function to aggregate and visualize metrics for a benchmark from multiple driver runs."""

import ipywidgets as widgets
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import clear_output, display

from .base_classes import Metrics


def aggregate_metrics(
    metrics_array: list[Metrics | dict],
    repetition_function_kwargs: dict = {},
    progress_function_kwargs: dict = {},
) -> dict:
    """
    Aggregates metrics objects for a benchmark from multiple driver runs for different tasks.
    Args:
        metrics_array (list[Metrics]): list of metrics objects
        repetition_function_kwargs (dict): Additional arguments for the repetition function. Required for repetition rate. Can vary with the benchmark. E.g. {"theta_a": 1, "num_execution_steps": 10}.
        progress_function_kwargs (dict):  Additional arguments for the progress function. Can vary with the benchmark. Usually, not needed.
    Returns:
        dict: aggregated data with keys success_rate, avg_progress_rate, avg_repetition_rate
    """
    goal_array = []  # list of goals
    success_array = []  # list of bools
    progress_rate_array = []  # list of lists of floats
    repetition_rate_array = []  # list of floats
    for metrics in metrics_array:
        if isinstance(metrics, Metrics):
            exported_metrics = metrics.export(
                repetition_function_kwargs, progress_function_kwargs
            )
        else:
            exported_metrics = metrics
        goal_array.append(exported_metrics.get("goal", None))
        success_array.append(exported_metrics.get("success", False))
        progress_rate_array.append(exported_metrics.get("progress", [0.0]))
        repetition_rate_array.append(exported_metrics.get("repetition_rate", 0.0))

    return {
        "goal_array": goal_array,
        "success_array": success_array,
        "success_rate": success_array.count(True) / len(success_array),
        "progress_rate_array": progress_rate_array,
        "avg_progress_rate": sum([prate[-1] for prate in progress_rate_array])
        / len(progress_rate_array),
        "repetition_rate_array": repetition_rate_array,
        "avg_repetition_rate": sum(repetition_rate_array) / len(repetition_rate_array),
    }


def plot_individual_progress_rates(aggregated_metrics: dict):
    data = aggregated_metrics.get("progress_rate_array", [])

    index = [0]
    plt.figure()
    plt.plot(
        range(1, len(data[index[0]]) + 1), data[index[0]], marker="o", linestyle="-"
    )
    plt.title(
        f"Progress plot {index[0] + 1} for goal: {aggregated_metrics.get('goal_array')[index[0]]}"
    )
    plt.ylabel("Progress rate")
    plt.xlabel("Number of execution steps")
    max_value = max(len(sublist) for sublist in data)
    plt.xticks(range(1, max_value + 1))

    prev_button = widgets.Button(description="Previous")
    next_button = widgets.Button(description="Next")
    display(widgets.HBox([prev_button, next_button]))
    plt.show()

    def update_plot(change: str):
        if change == "next":
            index[0] = (index[0] + 1) % len(data)
        elif change == "prev":
            index[0] = (index[0] - 1) % len(data)

        clear_output(wait=True)
        display(widgets.HBox([prev_button, next_button]))

        plt.figure()
        plt.plot(
            range(1, len(data[index[0]]) + 1), data[index[0]], marker="o", linestyle="-"
        )
        plt.xticks(range(1, max_value + 1))
        plt.title(
            f"Progress plot {index[0] + 1} for goal: {aggregated_metrics.get('goal_array')[index[0]]}"
        )
        plt.ylabel("Progress rate")
        plt.xlabel("Number of execution steps")
        plt.show()

    prev_button.on_click(lambda x: update_plot("prev"))
    next_button.on_click(lambda x: update_plot("next"))


def plot_all_progress_rates(aggregated_metrics: dict):
    data = aggregated_metrics.get("progress_rate_array", [])

    plt.figure()

    colors = plt.cm.get_cmap("tab10", len(data))

    for i, y_values in enumerate(data):
        plt.plot(
            range(1, len(y_values) + 1),
            y_values,
            marker="o",
            linestyle="-",
            label=f"Goal: {aggregated_metrics.get('goal_array')[i]}",
            color=colors(i),
        )
        max_value = max(len(sublist) for sublist in data)
        plt.xticks(range(1, max_value + 1))
    plt.legend(title="Index")

    plt.title("Progress plots for all runs")
    plt.ylabel("Progress rate")
    plt.xlabel("Number of execution steps")

    plt.show()


def plot_individual_actions(metrics_array):
    index = [0]

    def draw_plot():
        action_data = [
            action.value for action, _, _ in metrics_array[index[0]].interactions
        ]

        # Count occurrences of each unique action value
        unique_actions = sorted(set(action_data))  # Ensure sorted order
        counts = [action_data.count(action) for action in unique_actions]

        plt.figure()
        plt.bar(
            unique_actions, counts, width=0.5, align="center"
        )  # Use bar instead of hist
        plt.xticks(unique_actions, rotation=45)
        plt.title(
            f"Action histogram plot {index[0] + 1} for goal: {metrics_array[index[0]].goal}"
        )
        plt.ylabel("Number of repetitions")
        plt.xlabel("Action value")
        plt.show()

    def update_plot(change):
        if change == "next":
            index[0] = (index[0] + 1) % len(metrics_array)
        elif change == "prev":
            index[0] = (index[0] - 1) % len(metrics_array)
        clear_output(wait=True)
        display(widgets.HBox([prev_button, next_button]))
        draw_plot()

    prev_button = widgets.Button(description="Previous")
    next_button = widgets.Button(description="Next")
    prev_button.on_click(lambda x: update_plot("prev"))
    next_button.on_click(lambda x: update_plot("next"))

    display(widgets.HBox([prev_button, next_button]))
    draw_plot()


def plot_repetition_rates(aggregated_metrics: dict):
    data = aggregated_metrics.get("repetition_rate_array")

    plt.figure()
    sns.kdeplot(data, color="orange", fill=True, clip=(min(data), max(data)))
    plt.title("KDE Plot for Repetition Rate Density")
    plt.xlabel("Repetition Rate Value")
    plt.ylabel("Density")

    plt.tight_layout()
    plt.show()
