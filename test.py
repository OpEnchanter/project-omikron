class GameObject:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __hash__(self):
        # Use a unique identifier for hashing, such as the object's id
        return hash(self.id)

    def __eq__(self, other):
        # Compare objects based on their unique identifier
        if isinstance(other, GameObject):
            return self.id == other.id
        return False

# Create instances of GameObject
planet1 = GameObject(1, "Earth")
planet2 = GameObject(2, "Mars")

# Create a dictionary using GameObject instances as keys
planetEnemies = {planet1: [], planet2: []}

# Access dictionary values using the same instances
dist = 100  # example distance
planetRadius = 200  # example radius

# Example logic using the planet object as a key
planet = planet1  # This should be one of the keys used to populate the dictionary

if dist < planetRadius and planetEnemies[planet] == []:
    print("No enemies on this planet")

# If accessing with a new object with the same id
new_planet1 = GameObject(1, "Earth")

# Check if it works with a new object with the same id
if dist < planetRadius and planetEnemies[new_planet1] == []:
    print("No enemies on this planet with new object")
