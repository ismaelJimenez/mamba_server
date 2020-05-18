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
        })
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
        })
