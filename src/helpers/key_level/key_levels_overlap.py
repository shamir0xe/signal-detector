from src.models.key_level import KeyLevel


class KeyLevelsOverlap:
    @staticmethod
    def do(a: KeyLevel, b: KeyLevel) -> bool:
        a_edges = a.get_edges()
        b_edges = b.get_edges()

        condition_1 = False
        condition_1 |= b_edges[0] < a_edges[0] < b_edges[1]
        condition_1 |= b_edges[0] < a_edges[1] < b_edges[1]

        # condition_2 = False
        # condition_2 |= a_edges[0] < b_edges[0] < a_edges[1]
        # condition_2 |= a_edges[0] < b_edges[1] < a_edges[1]
        
        return condition_1
