from sympy import symbols, Not, Or, And
from sympy.logic.inference import satisfiable

class Literal:
    def __init__(self, name, positive=True):
        self.name = name
        self.positive = positive

    def negate(self):
        return Literal(self.name, not self.positive)

    def to_sympy(self):
        sym = symbols(self.name)
        return sym if self.positive else Not(sym)

    def __eq__(self, other):
        return self.name == other.name and self.positive == other.positive

    def __hash__(self):
        return hash((self.name, self.positive))

    def __repr__(self):
        return f"{'' if self.positive else '~'}{self.name}"

class KnowledgeBase:
    def __init__(self):
        self.clauses = []
    
    def add_clause(self, literals_list):
        """Añade una cláusula a la base de conocimientos. literals_list es lista de Literals."""
        sympy_lits = [lit.to_sympy() for lit in literals_list]
        clause = Or(*sympy_lits)
        if clause not in self.clauses:
            self.clauses.append(clause)

    def add_fact(self, literal):
        """Añade un hecho (cláusula unitaria) a la KB."""
        fact = literal.to_sympy()
        if fact not in self.clauses:
            self.clauses.append(fact)

    def update_fact(self, literal):
        """Actualiza un hecho en la KB, asegurando que no haya contradicciones directas."""
        fact = literal.to_sympy()
        neg_fact = literal.negate().to_sympy()
        if neg_fact in self.clauses:
            self.clauses.remove(neg_fact)
        if fact not in self.clauses:
            self.clauses.append(fact)

    def entails(self, query_literal):
        """
        Verifica si KB |= query_literal usando SymPy.
        Devuelve (True, explicacion) o (False, "").
        """
        query_expr = query_literal.to_sympy()
        neg_query_expr = Not(query_expr)
        
        if not self.clauses:
            return False, ""
            
        kb_expr = And(*self.clauses)
        
        # Verificar satisfacibilidad
        is_satisfiable = satisfiable(And(kb_expr, neg_query_expr))
        
        if is_satisfiable is False:
            estado = "Verdadero" if query_literal.positive else "Falso"
            explicacion = f"Usando inferencia proposicional con SymPy, se demuestra que {query_literal.name} es {estado}."
            return True, explicacion
        else:
            return False, ""
