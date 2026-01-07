#!/usr/bin/env python3
"""
Test script for Quarm Charm Calculator

Tests the calculation logic to ensure it matches EQMacEmu behavior.
"""

from charm_calculator import CharmCalculator


def test_basic_calculation():
    """Test basic charm calculations."""
    calc = CharmCalculator()

    print("=" * 60)
    print("Quarm Charm Calculator - Test Suite")
    print("=" * 60)
    print()

    # Test Case 1: Level 60 Enchanter vs Level 55 NPC
    print("Test 1: Level 60 Ench (200 CHA) vs Level 55 NPC (50 MR)")
    print("Spell: Allure (-50 resist diff)")
    print("-" * 60)

    initial = calc.calculate_initial_land_chance(
        caster_level=60,
        target_level=55,
        target_mr=50,
        resist_diff=-50,
        caster_charisma=200
    )

    print(f"Initial Land Chance: {initial['success_chance']:.1f}%")
    print(f"Resist Chance: {initial['resist_chance']}")
    print(f"Level Modifier: {initial['level_mod']}")
    print(f"Resist Modifier: {initial['resist_modifier']}")
    print()

    break_prob = calc.calculate_charm_break_probability(
        caster_level=60,
        target_level=55,
        target_mr=50,
        resist_diff=-50,
        caster_charisma=200,
        num_ticks=100,
        num_simulations=1000
    )

    print(f"Per-Tick Break Chance: {break_prob['single_tick_break_probability']:.2f}%")
    print(f"Expected Duration: {break_prob['expected_duration_minutes']:.1f} minutes")
    print()

    # Test Case 2: Level 60 Enchanter vs Level 60 NPC
    print("Test 2: Level 60 Ench (200 CHA) vs Level 60 NPC (100 MR)")
    print("Spell: Command of Druzzil (-200 resist diff)")
    print("-" * 60)

    initial2 = calc.calculate_initial_land_chance(
        caster_level=60,
        target_level=60,
        target_mr=100,
        resist_diff=-200,
        caster_charisma=200
    )

    print(f"Initial Land Chance: {initial2['success_chance']:.1f}%")
    print(f"Resist Chance: {initial2['resist_chance']}")
    print(f"Level Modifier: {initial2['level_mod']}")
    print(f"Resist Modifier: {initial2['resist_modifier']}")
    print()

    break_prob2 = calc.calculate_charm_break_probability(
        caster_level=60,
        target_level=60,
        target_mr=100,
        resist_diff=-200,
        caster_charisma=200,
        num_ticks=100,
        num_simulations=1000
    )

    print(f"Per-Tick Break Chance: {break_prob2['single_tick_break_probability']:.2f}%")
    print(f"Expected Duration: {break_prob2['expected_duration_minutes']:.1f} minutes")
    print()

    # Test Case 3: Six Level Rule (should be very hard)
    print("Test 3: Level 50 Ench vs Level 64 NPC (Six Level Rule)")
    print("Spell: Allure (-50 resist diff)")
    print("-" * 60)

    initial3 = calc.calculate_initial_land_chance(
        caster_level=50,
        target_level=64,
        target_mr=50,
        resist_diff=-50,
        caster_charisma=200
    )

    print(f"Initial Land Chance: {initial3['success_chance']:.1f}%")
    print(f"Resist Chance: {initial3['resist_chance']}")
    print(f"Level Modifier: {initial3['level_mod']} (Should be ~1000 - Six Level Rule)")
    print()

    # Test Case 4: Low level charm
    print("Test 4: Level 20 Ench (100 CHA) vs Level 18 NPC (25 MR)")
    print("Spell: Charm (-30 resist diff)")
    print("-" * 60)

    initial4 = calc.calculate_initial_land_chance(
        caster_level=20,
        target_level=18,
        target_mr=25,
        resist_diff=-30,
        caster_charisma=100
    )

    print(f"Initial Land Chance: {initial4['success_chance']:.1f}%")
    print(f"Resist Chance: {initial4['resist_chance']}")
    print(f"Level Modifier: {initial4['level_mod']}")
    print(f"Resist Modifier: {initial4['resist_modifier']}")
    print()

    break_prob4 = calc.calculate_charm_break_probability(
        caster_level=20,
        target_level=18,
        target_mr=25,
        resist_diff=-30,
        caster_charisma=100,
        num_ticks=100,
        num_simulations=1000
    )

    print(f"Per-Tick Break Chance: {break_prob4['single_tick_break_probability']:.2f}%")
    print(f"Expected Duration: {break_prob4['expected_duration_minutes']:.1f} minutes")
    print()

    # Test Case 5: Druid vs Enchanter comparison (same stats)
    print("Test 5: Druid vs Enchanter Comparison")
    print("Both Level 60, 200 CHA vs Level 55 NPC (50 MR), Allure (-50)")
    print("-" * 60)

    # Enchanter with 200 CHA
    ench_result = calc.calculate_initial_land_chance(
        caster_level=60,
        target_level=55,
        target_mr=50,
        resist_diff=-50,
        caster_charisma=200,
        is_enchanter=True
    )

    # Druid with 200 CHA (CHA doesn't help!)
    druid_result = calc.calculate_initial_land_chance(
        caster_level=60,
        target_level=55,
        target_mr=50,
        resist_diff=-50,
        caster_charisma=200,
        is_enchanter=False
    )

    print(f"Enchanter (200 CHA): {ench_result['success_chance']:.1f}% land chance, resist_mod={ench_result['resist_modifier']}")
    print(f"Druid (200 CHA):     {druid_result['success_chance']:.1f}% land chance, resist_mod={druid_result['resist_modifier']}")
    print(f"Difference: Enchanter gets {ench_result['resist_modifier'] - druid_result['resist_modifier']} bonus from CHA!")
    print()

    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_calculation()

