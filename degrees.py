import csv
import sys
import requests

# Maps names to a set of corresponding person_ids
names = {}
# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


url_people = "https://drive.google.com/u/0/uc?id=1zbsRHR2CkM84nYhWs5jiz1h2NxpzKToP&export=download"
url_movies = "https://drive.google.com/u/0/uc?id=1fKdqvcdatvPkfYICvwHIAldwdn2-fvo_&export=download"
url_stars = "https://drive.google.com/u/0/uc?id=1R6qS42WGAhQgBok89i5y3H3gKvJwlIC5&export=download"

def load_data():
    """
    Load data from CSV files into memory.
    """
    # Load people
    p = requests.get(url_people)
    open("people.csv", "wb").write(p.content)
    with open("people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])
    print("Part one Successfully loaded.")
    # Load movies
    m = requests.get(url_movies)
    open("movies.csv", "wb").write(m.content)
    with open("movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }
    print("Part two Successfully loaded.")
    # Load stars
    s = requests.get(url_stars)
    open("stars.csv", "wb").write(s.content)
    with open("stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass
    print("Part three Successfully loaded.")

def main():
    # Load data from files into memory
    print("Loading data...")
    load_data()
    print("Data loaded.")
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    # print(neighbors_for_person(source))
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    path = []
    explored = dict()
    explore = [source]
    def nb(id):
        nb = list()
        for item in neighbors_for_person(id):
            if item[1] != id:
                nb.append(item)
        return nb
    options = nb(source)
    for item in options:
        explored[item] = []
    while True:
        opt1 = options
        if len(opt1) == 0:
            return None
        explore.append(opt1[0][1])
        for item in nb(opt1[0][1]):
            if item[1] in explore:    
                pass
            elif item[1] == target:
                nod = item
                while True:
                    explored[item] = opt1[0]
                    path = [nod] + path
                    nod = explored[nod]
                    if nod == []:
                        return path
            elif item not in explored:
                options.append(item)
                explored[item] = opt1[0]
        options.remove(opt1[0])


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
