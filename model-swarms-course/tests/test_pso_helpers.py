import numpy as np

from model_swarms_course.pso import expand_population, model_swarms_velocity_update, rastrigin


def test_rastrigin_global_minimum_at_origin() -> None:
    assert rastrigin(np.array([0.0, 0.0])) == 0.0
    assert rastrigin(np.array([1.0, 1.0])) > 0.0


def test_model_swarms_velocity_update_deterministic() -> None:
    velocity = np.array([0.1, -0.2])
    pos = np.array([1.0, 2.0])
    pbest = np.array([1.5, 1.8])
    gbest = np.array([2.0, 1.0])
    gworst = np.array([-1.0, -1.0])

    updated = model_swarms_velocity_update(
        velocity,
        pos,
        pbest,
        gbest,
        gworst,
        inertia=0.2,
        cognitive_coeff=0.3,
        social_coeff=0.4,
        repel_coeff=0.1,
        use_randomness=False,
    )

    expected = np.array([0.77, -0.2])
    np.testing.assert_allclose(updated, expected, rtol=1e-7, atol=1e-7)


def test_expand_population_reaches_target_count() -> None:
    experts = [np.array([-1.0, 0.0]), np.array([0.5, 1.0]), np.array([1.0, -0.5])]
    expanded = expand_population(experts, target_count=10, seed=7)
    assert len(expanded) == 10
    assert np.array_equal(expanded[0], experts[0])
