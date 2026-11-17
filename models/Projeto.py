class Projeto:

    def __init__(self, label: str, vagas: int, nota_min: int):
        self.label = label
        self.vagas = vagas
        self.nota_min = nota_min

    def __str__(self) -> str:
        return "{}: {}, {}".format(self.label, self.vagas, self.nota_min)

    def __repr__(self) -> str:
        return "{}: {}, {}".format(self.label, self.vagas, self.nota_min)
