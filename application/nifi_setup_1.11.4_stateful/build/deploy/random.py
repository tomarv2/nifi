import uuid


def my_random_string(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]


print(my_random_string(10))