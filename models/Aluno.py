class Aluno:

    def __init__(self, label: str, preferencias: list[str], nota: int):
        self.label = label
        self.preferencias = preferencias
        self.nota = nota

    def __str__(self) -> str:
        return "{}: {}, ({})".format(self.label, self.preferencias, self.nota)

    def __repr__(self) -> str:
        return "{}: {}, ({})".format(self.label, self.preferencias, self.nota)
