import unittest


from pythomata.base.DFA import DFA
from pythomata.base.Alphabet import Alphabet
from pythomata.base.Simulator import DFASimulator
from pythomata.base.Symbol import Symbol
from pythomata.base.utils import Sink


class TestDFA(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.c = Symbol("a"), Symbol("b"), Symbol("c")
        self.alphabet = Alphabet({self.a, self.b, self.c})
        self.states = frozenset({"s1", "s2", "s3", "s4", "s5"})
        self.initial_state = "s1"
        self.accepting_states = frozenset({"s3", "s2"})
        self.transition_function = {
            "s1": {
                self.a: "s2",
                self.b: "s3",
                self.c: "s5"
            },
            "s2": {
                self.b: "s1"
            },
            "s3": {
                self.b: "s1"
            },
            "s4":{
                self.c: "s1"
            },
            "s5":{
                self.c: "s5"
            }
        }
        self.dfa = DFA(self.alphabet, self.states, self.initial_state, self.accepting_states, self.transition_function)


    def test_dfa_strings(self):
        self.dfa.to_dot("tests/automata/strings.dot")


    def test_completion(self):
        dfa_complete = DFA.complete(self.dfa)
        dfa_complete.to_dot("tests/automata/strings_complete.dot")


    def test_reachable(self):
        dfa = DFA.reachable(self.dfa)
        dfa.to_dot("tests/automata/strings_reachable.dot")

    def test_coreachable(self):
        dfa = DFA.coreachable(self.dfa)
        dfa.to_dot("tests/automata/strings_coreachable.dot")

    def test_trim(self):
        dfa = DFA.reachable(self.dfa)
        dfa = DFA.coreachable(dfa)
        dfa.to_dot("tests/automata/strings_trimmed.dot")

    def test_minimize(self):
        dfa_minimized= DFA.minimize(self.dfa)
        dfa_minimized.to_dot("tests/automata/strings_minimized.dot")

    def test_minimized_and_trimmed(self):
        dfa_minimized= DFA.minimize(self.dfa)
        dfa_minimized_and_trimmed = DFA.trim(dfa_minimized)
        dfa_minimized_and_trimmed.to_dot("tests/automata/strings_minimized_and_trimmed.dot")

    def test_word_acceptance(self):
        word = [self.a, self.b, self.b, self.b, self.b]
        self.assertFalse(self.dfa.word_acceptance([]))
        self.assertTrue(self.dfa.word_acceptance(word[:1]))
        self.assertFalse(self.dfa.word_acceptance(word[:2]))
        self.assertTrue(self.dfa.word_acceptance(word[:3]))
        self.assertFalse(self.dfa.word_acceptance(word[:4]))
        self.assertTrue(self.dfa.word_acceptance(word[:5]))

    def test_simulator(self):
        # not needed, but useful for testing purposes
        complete_dfa = self.dfa.complete()
        simulator = DFASimulator(complete_dfa)
        self.assertEqual(simulator.cur_state, simulator.state2id[complete_dfa.initial_state])

        simulator.make_transition(self.a)
        self.assertTrue(simulator.is_true())

        simulator.make_transition(self.b)
        self.assertFalse(simulator.is_true())

        simulator.make_transition(self.c)
        self.assertFalse(simulator.is_true())

        simulator.make_transition(self.c)
        self.assertFalse(simulator.is_true())

        simulator.make_transition(self.a)
        self.assertEqual(simulator.id2state[simulator.cur_state], Sink())
        self.assertFalse(simulator.is_true())

        simulator.make_transition(self.b)
        self.assertEqual(simulator.id2state[simulator.cur_state], Sink())
        self.assertFalse(simulator.is_true())

        self.assertFalse(simulator.word_acceptance([self.a, self.b, self.c, self.c, self.a, self.b]))
        self.assertTrue(simulator.word_acceptance([self.a, self.b, self.a]))


    def test_issue_15(self):
        H, E, L, O = Symbol("H"), Symbol("E"), Symbol("L"), Symbol("O")
        alphabet = Alphabet({H, E, L, O})
        states = frozenset({"s0", "s1", "s2", "s3", "s4"})
        initial_state = "s0"
        accepting_states = frozenset({"s4"})
        transition_function = {
            "s0": {H: "s1"},
            "s1": {E: "s2"},
            "s2": {L: "s3"},
            "s3": {O: "s4"},
        }

        dfa = DFA(alphabet, states, initial_state, accepting_states, transition_function)
        dfa.complete().to_dot("tests/automata/issue_15_complete")
        dfa.minimize().to_dot("tests/automata/issue_15_minimized")

        self.assertTrue(dfa.word_acceptance([H, E, L, O]))
        self.assertFalse(dfa.word_acceptance([H, E, L, L, O]))
        self.assertFalse(dfa.word_acceptance([H, E, L]))
        self.assertFalse(dfa.word_acceptance([H, E, O]))
        self.assertFalse(dfa.word_acceptance([H, E, L, O, O]))
        self.assertFalse(dfa.word_acceptance([]))
