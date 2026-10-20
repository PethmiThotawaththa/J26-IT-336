
from pathlib import Path
import random

import numpy as np
import pandas as pd
from deap import algorithms, base, creator, tools


# ============================================================
# 1. CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "data" / "demo"
OUTPUT_DIR = ROOT / "outputs"

TASKS_FILE = DEMO_DIR / "maintenance_tasks.csv"
REQUIREMENTS_FILE = DEMO_DIR / "task_requirements.csv"
AVAILABILITY_FILE = DEMO_DIR / "resource_availability.csv"

OUTPUT_FILE = OUTPUT_DIR / "nsga2_allocation.csv"
PARETO_FILE = OUTPUT_DIR / "nsga2_pareto_solutions.csv"

RANDOM_SEED = 42
POPULATION_SIZE = 80
GENERATIONS = 60
CROSSOVER_PROBABILITY = 0.8
MUTATION_PROBABILITY = 0.2
MUTATION_GENE_PROBABILITY = 0.15

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ============================================================
# 2. LOAD AND VALIDATE INPUTS
# ============================================================

def load_inputs():
    tasks = pd.read_csv(TASKS_FILE)
    requirements = pd.read_csv(REQUIREMENTS_FILE)
    availability = pd.read_csv(AVAILABILITY_FILE)

    required_columns = [
        (
            "maintenance_tasks.csv",
            tasks,
            {"task_id", "priority", "data_status"},
        ),
        (
            "task_requirements.csv",
            requirements,
            {
                "task_id",
                "resource_name",
                "required_quantity",
                "unit",
                "data_status",
            },
        ),
        (
            "resource_availability.csv",
            availability,
            {
                "resource_name",
                "available_quantity",
                "unit",
                "data_status",
            },
        ),
    ]

    for filename, frame, expected_columns in required_columns:
        missing = expected_columns - set(frame.columns)

        if missing:
            raise ValueError(
                f"{filename} is missing columns: {sorted(missing)}"
            )

        if frame.empty:
            raise ValueError(f"{filename} contains no records.")

        status = (
            frame["data_status"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        if not status.eq("SIMULATED").all():
            raise ValueError(
                f"{filename} must contain SIMULATED data only. "
                "Do not mix actual, estimated, or unknown records."
            )

    if tasks["task_id"].duplicated().any():
        raise ValueError("Task IDs must be unique.")

    if availability["resource_name"].duplicated().any():
        raise ValueError("Availability must have one row per resource.")

    if requirements.duplicated(
        ["task_id", "resource_name"]
    ).any():
        raise ValueError(
            "Each task/resource combination must be unique."
        )

    if requirements["task_id"].isna().any():
        raise ValueError("Requirement task IDs cannot be empty.")

    if requirements["resource_name"].isna().any():
        raise ValueError("Requirement resource names cannot be empty.")

    if not set(requirements["task_id"]).issubset(
        set(tasks["task_id"])
    ):
        raise ValueError("Some requirements reference unknown tasks.")

    tasks["priority"] = pd.to_numeric(
        tasks["priority"], errors="raise"
    )
    requirements["required_quantity"] = pd.to_numeric(
        requirements["required_quantity"], errors="raise"
    )
    availability["available_quantity"] = pd.to_numeric(
        availability["available_quantity"], errors="raise"
    )

    for frame, column, description in [
        (tasks, "priority", "Priorities"),
        (requirements, "required_quantity", "Required quantities"),
        (availability, "available_quantity", "Available quantities"),
    ]:
        values = frame[column].to_numpy(dtype=float)

        if not np.isfinite(values).all():
            raise ValueError(f"{description} must be finite numbers.")

        if (values < 0).any():
            raise ValueError(f"{description} cannot be negative.")

    if tasks["priority"].sum() <= 0:
        print(
            "Notice: all priorities are zero; "
            "the optimizer will use equal task weights."
        )

    resource_units = availability.set_index(
        "resource_name"
    )["unit"].to_dict()

    required_resources = set(requirements["resource_name"])
    available_resources = set(resource_units)

    missing_resources = required_resources - available_resources

    if missing_resources:
        raise ValueError(
            "Resources missing from availability: "
            f"{sorted(missing_resources)}"
        )

    for _, row in requirements.iterrows():
        expected_unit = resource_units[row["resource_name"]]

        if str(row["unit"]).strip() != str(expected_unit).strip():
            raise ValueError(
                f"Unit mismatch for {row['resource_name']}: "
                f"requirement={row['unit']}, "
                f"availability={expected_unit}"
            )

    return tasks, requirements, availability


# ============================================================
# 3. BUILD THE NSGA-II OPTIMIZER
# ============================================================

def build_optimizer(tasks, requirements, availability):
    requirements = requirements.reset_index(drop=True).copy()

    task_ids = requirements["task_id"].tolist()
    resource_names = requirements["resource_name"].tolist()

    demands = requirements["required_quantity"].to_numpy(
        dtype=float
    )

    supply = availability.set_index(
        "resource_name"
    )["available_quantity"].to_dict()

    task_priorities = tasks.set_index(
        "task_id"
    )["priority"].to_dict()

    task_row_indices = {
        task_id: [
            i for i, requirement_task_id in enumerate(task_ids)
            if requirement_task_id == task_id
        ]
        for task_id in tasks["task_id"]
    }

    if not hasattr(creator, "NSGA2Fitness"):
        creator.create(
            "NSGA2Fitness",
            base.Fitness,
            weights=(-1.0, -1.0),
        )

    if not hasattr(creator, "NSGA2Individual"):
        creator.create(
            "NSGA2Individual",
            list,
            fitness=creator.NSGA2Fitness,
        )

    toolbox = base.Toolbox()

    toolbox.register("gene", random.random)
    toolbox.register(
        "individual",
        tools.initRepeat,
        creator.NSGA2Individual,
        toolbox.gene,
        n=len(requirements),
    )
    toolbox.register(
        "population",
        tools.initRepeat,
        list,
        toolbox.individual,
    )

    def decode(individual):
        """Decode fractions into allocations that respect supply."""
        allocated = np.clip(
            np.asarray(individual, dtype=float),
            0.0,
            1.0,
        ) * demands

        for resource_name, available_quantity in supply.items():
            indices = [
                i for i, name in enumerate(resource_names)
                if name == resource_name
            ]

            total = allocated[indices].sum()

            if total > available_quantity and total > 0:
                allocated[indices] *= available_quantity / total

        return allocated

    def evaluate(individual):
        allocated = decode(individual)

        # Proportional shortage for every requirement.
        shortages = np.zeros(len(requirements))
        positive = demands > 0

        shortages[positive] = (
            demands[positive] - allocated[positive]
        ) / demands[positive]

        # Average proportional shortage within each task.
        task_shortages = {}

        for task_id, indices in task_row_indices.items():
            positive_indices = [
                i for i in indices if demands[i] > 0
            ]

            if positive_indices:
                task_shortages[task_id] = float(
                    shortages[positive_indices].mean()
                )
            else:
                task_shortages[task_id] = 0.0

        # Objective 1: priority-weighted task shortage.
        total_priority = sum(task_priorities.values())

        if total_priority > 0:
            objective_1 = sum(
                task_priorities[task_id] / total_priority
                * task_shortages[task_id]
                for task_id in task_shortages
            )
        else:
            objective_1 = float(
                np.mean(list(task_shortages.values()))
            )

        # Objective 2: worst average task shortage.
        objective_2 = max(
            task_shortages.values(),
            default=0.0,
        )

        return float(objective_1), float(objective_2)

    def mutate(individual, indpb=MUTATION_GENE_PROBABILITY):
        for i in range(len(individual)):
            if random.random() < indpb:
                individual[i] += random.gauss(0.0, 0.20)
                individual[i] = min(
                    1.0,
                    max(0.0, individual[i]),
                )

        return (individual,)

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate)
    toolbox.register("select", tools.selNSGA2)

    return toolbox, decode, requirements


# ============================================================
# 4. SELECT A COMPROMISE SOLUTION
# ============================================================

def select_compromise(candidates, toolbox):
    """
    Select a compromise using normalized distances from the
    ideal point. Both objectives are minimized.

    This is a decision rule, not proof that the selected solution
    is universally best.
    """
    unique = {}

    for individual in candidates:
        key = tuple(individual)
        fitness = np.asarray(
            toolbox.evaluate(individual),
            dtype=float,
        )
        unique[key] = (individual, fitness)

    solutions = list(unique.values())

    if not solutions:
        raise RuntimeError("No candidate solutions were produced.")

    fitness_values = np.vstack(
        [fitness for _, fitness in solutions]
    )

    minimum = fitness_values.min(axis=0)
    maximum = fitness_values.max(axis=0)
    ranges = maximum - minimum

    normalized = np.zeros_like(fitness_values)

    for column in range(fitness_values.shape[1]):
        if ranges[column] > 1e-12:
            normalized[:, column] = (
                fitness_values[:, column] - minimum[column]
            ) / ranges[column]

    distances = np.sqrt(
        np.sum(normalized ** 2, axis=1)
    )

    return solutions[int(np.argmin(distances))][0]


# ============================================================
# 5. SAVE PARETO ALTERNATIVES
# ============================================================

def save_pareto_solutions(candidates, toolbox):
    rows = []

    for candidate in candidates:
        objective_1, objective_2 = toolbox.evaluate(candidate)

        rows.append({
            "objective_1_weighted_shortage": float(objective_1),
            "objective_2_worst_task_shortage": float(objective_2),
            "allocation_fractions": ";".join(
                f"{float(value):.6f}" for value in candidate
            ),
            "data_status": "SIMULATED",
        })

    columns = [
        "objective_1_weighted_shortage",
        "objective_2_worst_task_shortage",
        "allocation_fractions",
        "data_status",
    ]

    result = pd.DataFrame(rows, columns=columns)

    if not result.empty:
        result = result.sort_values(
            [
                "objective_1_weighted_shortage",
                "objective_2_worst_task_shortage",
            ]
        ).reset_index(drop=True)

        result = result.drop_duplicates(
            subset=[
                "objective_1_weighted_shortage",
                "objective_2_worst_task_shortage",
            ]
        ).reset_index(drop=True)

        result.insert(
            0,
            "solution_id",
            np.arange(1, len(result) + 1),
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(PARETO_FILE, index=False)

    print(f"Unique Pareto objective pairs saved: {len(result)}")

    return result
# ============================================================
# 6. SAVE SELECTED ALLOCATION AND CHECK CAPACITY
# ============================================================

def save_results(tasks, requirements, allocated, availability):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = requirements.copy()
    results["allocated_quantity"] = allocated

    results["shortage_quantity"] = (
        results["required_quantity"]
        - results["allocated_quantity"]
    ).clip(lower=0.0)

    results["allocation_status"] = np.where(
        results["shortage_quantity"] <= 1e-8,
        "FULLY_ALLOCATED",
        "SHORTAGE",
    )

    results["data_status"] = "SIMULATED"

    task_columns = [
        column for column in [
            "task_id",
            "road_id",
            "road_section",
            "repair_type",
            "priority",
            "planned_start",
        ]
        if column in tasks.columns
    ]

    results = results.merge(
        tasks[task_columns].drop_duplicates("task_id"),
        on="task_id",
        how="left",
        suffixes=("", "_task"),
        validate="many_to_one",
    )

    results.to_csv(OUTPUT_FILE, index=False)

    supply = availability.set_index(
        "resource_name"
    )["available_quantity"].to_dict()

    capacity_ok = True

    for resource_name, group in results.groupby("resource_name"):
        total_allocated = group["allocated_quantity"].sum()
        available_quantity = float(supply[resource_name])

        if total_allocated > available_quantity + 1e-6:
            capacity_ok = False
            print(
                f"CAPACITY ERROR: {resource_name}: "
                f"allocated={total_allocated:.6f}, "
                f"available={available_quantity:.6f}"
            )

    if not capacity_ok:
        raise RuntimeError(
            "The selected allocation exceeded a resource capacity."
        )

    return results


# ============================================================
# 7. MAIN
# ============================================================

def main():
    tasks, requirements, availability = load_inputs()

    toolbox, decode, requirements = build_optimizer(
        tasks,
        requirements,
        availability,
    )

    population = toolbox.population(n=POPULATION_SIZE)

    # Evaluate the initial population.
    for individual in population:
        individual.fitness.values = toolbox.evaluate(individual)

    population = toolbox.select(population, len(population))

    pareto_front = tools.ParetoFront()

    statistics = tools.Statistics(
        lambda individual: individual.fitness.values
    )
    statistics.register("min", np.min, axis=0)
    statistics.register("avg", np.mean, axis=0)

    population, logbook = algorithms.eaMuPlusLambda(
        population,
        toolbox,
        mu=POPULATION_SIZE,
        lambda_=POPULATION_SIZE,
        cxpb=CROSSOVER_PROBABILITY,
        mutpb=MUTATION_PROBABILITY,
        ngen=GENERATIONS,
        stats=statistics,
        halloffame=pareto_front,
        verbose=True,
    )

    candidates = list(pareto_front)

    if not candidates:
        candidates = list(population)

    # Save every Pareto alternative before selecting one.
    pareto_df = save_pareto_solutions(candidates, toolbox)

    print(f"\nPareto solutions found: {len(pareto_df)}")
    print(f"Pareto solutions saved: {PARETO_FILE}")

    if not pareto_df.empty:
        print("\nBest objective values in the Pareto set:")
        print(
            pareto_df[
                [
                    "objective_1_weighted_shortage",
                    "objective_2_worst_task_shortage",
                ]
            ].head(10).to_string(index=False)
        )

    # Select one compromise for the allocation output.
    best = select_compromise(candidates, toolbox)
    allocated = decode(best)

    results = save_results(
        tasks,
        requirements,
        allocated,
        availability,
    )

    display_columns = [
        column for column in [
            "task_id",
            "road_id",
            "resource_name",
            "required_quantity",
            "allocated_quantity",
            "shortage_quantity",
            "unit",
            "allocation_status",
            "data_status",
        ]
        if column in results.columns
    ]

    print("\nSelected NSGA-II demonstration allocation:")
    print(results[display_columns].to_string(index=False))

    objective_1, objective_2 = toolbox.evaluate(best)

    print("\nSelected solution objectives:")
    print(
        "1. Priority-weighted proportional unmet demand:",
        round(objective_1, 6),
    )
    print(
        "2. Worst task-level average proportional shortage:",
        round(objective_2, 6),
    )

    print(f"\nSaved allocation: {OUTPUT_FILE}")
    print("Resource capacity validation: PASSED")
    print(
        "WARNING: SIMULATED demonstration only. "
        "This is not a validated RDA allocation plan."
    )


if __name__ == "__main__":
    main()

