import random
import json


def generate_instance(num_skills, num_people, num_jobs, max_due_date):
    instance = {"horizon": max_due_date, "jobs": [], "qualifications": [], "staff": []}

    # Generate qualifications
    qualifications = ["Skill" + str(i) for i in range(1, num_skills + 1)]
    instance["qualifications"] = qualifications

    # Generate jobs
    for i in range(num_jobs):
        job = {
            "daily_penalty": random.randint(1, 5),
            "due_date": random.randint(1, max_due_date),
            "gain": random.randint(10, 30),
            "name": "Job" + str(i + 1),
            "working_days_per_qualification": {},
        }

        num_skills_per_job = random.randint(1, num_skills)
        skills_per_job = random.sample(qualifications, num_skills_per_job)
        for skill in skills_per_job:
            job["working_days_per_qualification"][skill] = random.randint(1, 3)

        instance["jobs"].append(job)

    # Generate staff
    for i in range(num_people):
        person = {"name": "Person" + str(i + 1), "qualifications": [], "vacations": []}

        num_skills_per_person = random.randint(1, num_skills)
        skills_per_person = random.sample(qualifications, num_skills_per_person)
        person["qualifications"] = skills_per_person

        num_vacations = random.randint(0, round(max_due_date / 2))
        vacations = random.sample(range(0, max_due_date), num_vacations)
        person["vacations"] = vacations

        instance["staff"].append(person)

    return instance


if __name__ == "__main__":
    data = generate_instance(num_skills=4, num_people=6, num_jobs=6, max_due_date=8)

    with open("data/generated_2_instance.json", "w") as outfile:
        json.dump(data, outfile)
