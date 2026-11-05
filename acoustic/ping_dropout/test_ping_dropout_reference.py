"""Unit checks for the generic reference implementation (no campaign data)."""
import unittest
import numpy as np
from ping_dropout_reference import calculate_ping_dropout


class TestReference(unittest.TestCase):
    def test_reference_updates_and_depth_cutoff(self):
        sv = np.array([[-1, -20, -30], [-1, -70, -80], [-1, -10, -50]], float)
        r = calculate_ping_dropout(sv, surface_cutoff_bin=1, window_pings=2)
        np.testing.assert_array_equal(r.dropped, [0.0, 1.0, 0.0])
        np.testing.assert_allclose(r.reference_sv_db, [-20.0, -20.0, -10.0])
        np.testing.assert_allclose(r.fraction, [0, 0.5, 0.5])

    def test_file_boundary_reset(self):
        sv = np.array([[-10, -20], [-70, -80], [-70, -80]], float)
        r = calculate_ping_dropout(sv, surface_cutoff_bin=0, window_pings=3, file_ids=['a','a','b'])
        np.testing.assert_array_equal(r.dropped, [0, 1, 0])
        np.testing.assert_array_equal(r.reference_sv_db, [-10, -10, -70])

    def test_nan_does_not_invent_missing_ping(self):
        sv = np.array([[-10, -20], [np.nan, np.nan], [-70, -80]], float)
        r = calculate_ping_dropout(sv, surface_cutoff_bin=0, window_pings=3)
        self.assertTrue(np.isnan(r.dropped[1]))
        np.testing.assert_allclose(r.fraction, [0, 0, 0.5])

    def test_percent_output_is_100_times_fraction(self):
        sv = np.array([[-20, -25], [-70, -80], [-20, -25]], float)
        r = calculate_ping_dropout(sv, surface_cutoff_bin=0, window_pings=2)
        np.testing.assert_allclose(r.fraction, [0, 0.5, 0.5])
        np.testing.assert_allclose(r.percent, [0, 50, 50])

    def test_running_reference_differs_from_end_of_file_maximum(self):
        sv = np.array([[-85, -90], [-20, -25], [-75, -80]], float)
        r = calculate_ping_dropout(sv, surface_cutoff_bin=0, window_pings=3)
        np.testing.assert_array_equal(r.dropped, [0, 0, 1])
        retrospective_flags = (np.array([-85., -20., -75.]) < -60.).astype(int)
        np.testing.assert_array_equal(retrospective_flags, [1, 0, 1])

    def test_time_window_with_irregular_samples(self):
        sv = np.array([[-10, -20], [-70, -80], [-70, -80], [-10, -15]], float)
        r = calculate_ping_dropout(sv, surface_cutoff_bin=0, window_seconds=120,
                                   times=np.array([0, 20, 200, 210]))
        np.testing.assert_allclose(r.fraction, [0, 0.5, 1, 0.5])


if __name__ == "__main__":
    unittest.main()
