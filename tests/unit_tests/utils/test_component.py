from mamba_server.utils.component import merge_dicts


class TestClass:
    def test_merge_dicts(self):
        # Test behaviour with no conflict
        assert merge_dicts({
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }, {
            2: {
                "c": "C"
            },
            3: {
                "d": "D"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B',
                'c': 'C'
            },
            3: {
                'd': 'D'
            }
        }

        # Test behaviour with None
        assert merge_dicts({
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }, None) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }

        assert merge_dicts(None, {
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }

        assert merge_dicts({
            1: {
                "a": None
            },
            2: {
                "b": "B"
            }
        }, {
            1: {
                "a": "A"
            },
            2: {
                "b": "C"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }

        # Test behaviour with conflict
        assert merge_dicts({
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }, {
            1: {
                "a": "A"
            },
            2: {
                "b": "C"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }
