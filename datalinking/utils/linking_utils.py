def is_firstname_same(person1, person2):
    return person1.normalized_first_names[0] == person2.normalized_first_names[0]


def are_firstnames_same(person1, person2, min_names=2):
    names1 = set(person1.normalized_first_names)
    names2 = set(person2.normalized_first_names)
    return names1 == names2 and len(names1) >= min_names


def is_birthplace_same(person1, person2):
    return person1.birthplace == person2.birthplace
