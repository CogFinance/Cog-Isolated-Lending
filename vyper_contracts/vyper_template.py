from jinja2 import Environment, FileSystemLoader

class HighPair:
    def __init__(self):
        self.MINIMUM_TARGET_UTILIZATION = 600000000000000000 # 60%
        self.MAXIMUM_TARGET_UTILIZATION = 800000000000000000 # 80%

        self.STARTING_INTEREST_PER_SECOND = 1585489600  # 5% APR
        self.MINIMUM_INTEREST_PER_SECOND = 634195840  # Aprox 2% APR
        self.MAXIMUM_INTEREST_PER_SECOND = 317097920000  # Aprox 1000% APR 

    def __str__(self) -> str:
        return "high_pair"

class MediumPair:
    def __init__(self):
        self.MINIMUM_TARGET_UTILIZATION = 600000000000000000 # 60%
        self.MAXIMUM_TARGET_UTILIZATION = 800000000000000000 # 80%

        self.STARTING_INTEREST_PER_SECOND = 317097920  # 1% APR
        self.MINIMUM_INTEREST_PER_SECOND = 79274480  # Aprox 0.25% APR
        self.MAXIMUM_INTEREST_PER_SECOND = 31709792000  # Aprox 100% APR

    def __str__(self) -> str:
        return "medium_pair"

class LowPair:
    def __init__(self):
        self.MINIMUM_TARGET_UTILIZATION = 400000000000000000 # 40%
        self.MAXIMUM_TARGET_UTILIZATION = 800000000000000000 # 80%

        self.STARTING_INTEREST_PER_SECOND = 634195840  # 2% APR
        self.MINIMUM_INTEREST_PER_SECOND = 79274480  # Aprox 0.25% APR
        self.MAXIMUM_INTEREST_PER_SECOND = 15854896000  # Aprox 50% APR

    def __str__(self) -> str:
        return "low_pair"

class StablePair:
    """
        Risk configuration for stablecoin to stablecoin pairs, or eth to staked eth pairs, and other likewise pairs
    """
    def __init__(self):
        self.MINIMUM_TARGET_UTILIZATION = 100000000000000000 # 10%
        self.MAXIMUM_TARGET_UTILIZATION = 650000000000000000 # 65%

        self.STARTING_INTEREST_PER_SECOND = 158548960  # 0.5% APR
        self.MINIMUM_INTEREST_PER_SECOND = 79274480  # Aprox 0.25% APR
        self.MAXIMUM_INTEREST_PER_SECOND = 7927448000  # Aprox 25% APR

    def __str__(self) -> str:
        return "stable_pair"


pair_configurations = [HighPair(), MediumPair(), LowPair(), StablePair()]

environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("cog_pair.template")

for pair in pair_configurations:
    filename = f"cog_{str(pair).lower()}.vy"

    content = template.render(
        MINIMUM_TARGET_UTILIZATION = pair.MINIMUM_TARGET_UTILIZATION,
        MAXIMUM_TARGET_UTILIZATION = pair.MAXIMUM_TARGET_UTILIZATION,
        STARTING_INTEREST_PER_SECOND = pair.STARTING_INTEREST_PER_SECOND,
        MINIMUM_INTEREST_PER_SECOND = pair.MINIMUM_INTEREST_PER_SECOND,
        MAXIMUM_INTEREST_PER_SECOND = pair.MAXIMUM_INTEREST_PER_SECOND
    )

    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)
        print(f"... wrote {filename}")
