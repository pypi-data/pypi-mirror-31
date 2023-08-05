import august


class TestRecalculateWidths:

    def test_short(self):
        start_widths = [2, 6, 6]
        end_widths = august.TableElement.recalculate_widths(start_widths, 80)
        assert end_widths == start_widths

    def test_long(self):
        start_widths = [12, 66, 65]
        end_widths = august.TableElement.recalculate_widths(start_widths, 80)
        expected_widths = [6, 35, 35]
        assert end_widths == expected_widths
