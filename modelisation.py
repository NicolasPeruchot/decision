import json
from enum import Enum
from gurobipy import Model, GRB, quicksum


class DATASET(Enum):
    TOY = "toy"
    MEDIUM = "medium"
    LARGE = "large"


def load_data(name):
    """name must be an instance of DATASET like DATASET.TOY for example"""
    if not isinstance(name, DATASET):
        raise TypeError("direction must be an instance of DATASET Enum")
    with open(f"decision/data/{name.value}_instance.json", "r") as f:
        data = json.load(f)
    return data


def get_dims(data):
    return (
        len(data["staff"]),
        data["horizon"],
        len(data["qualifications"]),
        len(data["jobs"]),
    )


def init_model():
    m = Model("Project modelling")
    return m


def get_var_by_name(model, matrix_name, indexes):
    string = matrix_name + "["
    for i in indexes:
        if i != 0:
            string += ","
        string += str(i)
    string += "]"
    return model.getVarByName(matrix_name + "[%d]" % (i for i in indexes)).X


def create_decision_variables(model, n_staff, horizon, n_qualifs, n_jobs):
    X = model.addMVar((n_staff, horizon, n_qualifs, n_jobs), vtype=GRB.BINARY, name="X")
    J = model.addMVar(n_jobs, vtype=GRB.BINARY, name="J")
    D = model.addMVar((n_jobs, 3), lb=0, ub=horizon + 1, vtype=GRB.INTEGER, name="D")
    return model, X, J, D


def add_constraints_for_J(model, X, J, jobs, qualifications):
    for index_job in range(len(J)):
        model.addGenConstrIndicator(
            J[index_job],
            True,
            (
                sum(X[:, :, index_k, index_job])
                >= jobs[index_job]["working_days_per_qualification"][k]
                for index_k, k in enumerate(qualifications)
            ),
        )
        model.addGenConstrIndicator(
            J[index_job],
            False,
            not (
                sum(X[:, :, index_k, index_job])
                >= jobs[index_job]["working_days_per_qualification"][k]
                for index_k, k in enumerate(qualifications)
            ),
        )


def add_constraints_for_D(model, X, J, D, horizon):
    for index_job in range(len(J)):

        start_date = min([j for j in range(horizon) if sum(X[:, j, :, index_job]) >= 0])
        end_date = max([j for j in range(horizon) if sum(X[:, j, :, index_job]) >= 0])
        range = end_date - start_date + 1

        model.addGenConstrIndicator(
            J[index_job],
            True,
            D[index_job, :] == [start_date, end_date, range],
        )
        model.addGenConstrIndicator(J[index_job], False, D[index_job, :] == [0, horizon + 1, 0])


def add_profit_as_first_objective(model, J, D, jobs):

    benef = sum(
        [
            J[index_job] * (job.gain - job.daily_penalty * max(D[index_job, 1] - job.due_date, 0))
            for index_job, job in enumerate(jobs)
        ]
    )

    model.setObjective(benef, GRB.MAXIMIZE)


def in_qualification(i, k):
    data = {data["staff"][i]["name"]: data["staff"][i] for i in range(len(data["staff"]))}
    data = data[i]["qualifications"]
    return k in data


def add_qualification_constraints(model, n_staff, horizon, n_qualifs, n_jobs, X):
    model.addConstrs(
        X[i, j, k, l] == 0
        for i in range(n_staff)
        for j in range(horizon)
        for k in range(n_qualifs)
        for l in range(n_jobs)
        if not in_qualification(i, k)
    )


def in_vacation(i, j):
    data = {data["staff"][i]["name"]: data["staff"][i] for i in range(len(data["staff"]))}
    data = data[i]["vacations"]
    return j in data


def add_vacation_constraints(model, n_staff, horizon, n_qualifs, n_jobs, X):
    model.addConstrs(
        X[i, j, k, l] == 0
        for i in range(n_staff)
        for j in range(horizon)
        for k in range(n_qualifs)
        for l in range(n_jobs)
        if in_vacation(i, j)
    )


def min_nb_projet_per_staff(model, n_staff, horizon, n_qualifs, n_jobs):
    obj1 = quicksum(M(i, j, k, l) for j in horizon for k in n_qualifs)
    obj1 = quicksum()


def main():
    # Importing data
    data = load_data(DATASET.TOY)
    n_staff, horizon, n_qualifs, n_jobs = get_dims(data)

    # Instanciation du modèle
    model = init_model()

    # Création des variables : binaires dans X et J, entières de 0 à horizon + 3
    model, X, J, D = create_decision_variables(model, n_staff, horizon, n_qualifs, n_jobs)

    # maj du modèle
    model.update()

    # Ajout des 3 constraintes
    add_constraints_for_J(model, X, J, jobs=data["jobs"], qualifications=data["qualifications"])
    add_constraints_for_D(model, X, J, D, horizon)
    add_qualification_constraints(model, n_staff, horizon, n_qualifs, n_jobs, X)
    add_vacation_constraints(model, n_staff, horizon, n_qualifs, n_jobs, X)

    # Fonction Objectif
    add_profit_as_first_objective(model, J, D, data["jobs"])

    # Paramétrage (mode mute)
    # model.params.outputflag = 0

    # Résolution du PL
    model.optimize()


if __name__ == "__main__":
    main()
