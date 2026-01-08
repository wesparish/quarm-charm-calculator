"""
Quarm Charm Calculator - Resist Calculation Logic

This module implements the charm break calculation logic from EQMacEmu's
zone/spells.cpp CheckResistSpell method, specifically for charm spells.
"""

import random
from typing import Dict, Tuple
from charm_spells_data import CHARM_SPELLS, get_charm_spell, get_charm_spell_by_name, get_all_charm_spells


class CharmCalculator:
    """
    Calculates charm effectiveness and break probability based on EQMacEmu resist logic.

    Based on EQMacEmu zone/spells.cpp:CheckResistSpell() and zone/spell_effects.cpp SE_Charm tick logic
    """

    # Common charm spell resist modifiers
    # Now loaded from charm_spells_data.py
    CHARM_SPELLS = CHARM_SPELLS

    @staticmethod
    def get_all_spells():
        """Get all charm spells."""
        return get_all_charm_spells()

    @staticmethod
    def get_spell(spell_id):
        """Get a specific charm spell by ID."""
        return get_charm_spell(spell_id)

    @staticmethod
    def get_spell_by_name(name):
        """Get a specific charm spell by name."""
        return get_charm_spell_by_name(name)

    def __init__(self):
        self.use_classic_resists = True  # Quarm uses classic resists
        self.charm_min_resist = 5  # From RuleI(Spells, CharmMinResist)

    def calculate_resist_chance(self, caster_level: int, target_level: int,
                                target_mr: int, resist_diff: int,
                                caster_charisma: int = 75,
                                is_enchanter: bool = True,
                                is_tick_save: bool = False) -> Dict:
        """
        Calculate the resist chance for a charm spell.

        Args:
            caster_level: Level of the caster (player)
            target_level: Level of the target NPC
            target_mr: Magic resist value of the target NPC
            resist_diff: Resist modifier from the spell (negative = easier to land)
            caster_charisma: Charisma stat of the caster (default 75)
            is_enchanter: Whether the caster is an enchanter (only enchanters get CHA bonus)
            is_tick_save: Whether this is a tick save check (charm break check)

        Returns:
            Dictionary with resist_chance, roll_needed, and other details
        """

        # Adjust caster level for tick saves (charm breaks)
        effective_caster_level = caster_level + 4 if is_tick_save else caster_level

        # Base resist value
        target_resist = target_mr
        resist_chance = 0

        # Calculate level modifier
        leveldiff = target_level - effective_caster_level
        temp_level_diff = leveldiff

        # NPC level difference caps for high level NPCs
        # For NPCs level 51+, level difference is capped
        if target_level >= 51:
            a = 50 - effective_caster_level
            if a > 0:
                temp_level_diff = a
            else:
                temp_level_diff = 0

        # Cap level difference at -9 for low targets
        if temp_level_diff < -9:
            temp_level_diff = -9

        # Calculate base level modifier: (level_diff^2) / 2
        level_mod = temp_level_diff * temp_level_diff // 2
        if temp_level_diff < 0:
            level_mod = -level_mod

        # Additional resist bump for targets significantly above caster
        if effective_caster_level < 50:
            bump_level = effective_caster_level + 4 + effective_caster_level // 6
            if target_level >= bump_level:
                level_mod += 70 + effective_caster_level * 6
        else:
            if effective_caster_level < 64:
                if leveldiff >= 13:
                    level_mod = effective_caster_level * 5
            else:
                if leveldiff >= 16:
                    level_mod = effective_caster_level * 5

        # Apply the Six Level Rule (Quarm specific)
        # If target is 7+ levels or 25%+ higher than caster, massive resist bonus
        if target_level >= max(effective_caster_level + 7, int(effective_caster_level * 1.25)):
            level_mod = 1000  # Effectively unresistable

        # Enchanter charisma bonus for charm spells (ENCHANTER ONLY!)
        # From zone/spells.cpp: if (!tick_save && caster->GetClass() == Class::Enchanter)
        resist_modifier = resist_diff
        if is_enchanter and not is_tick_save and caster_charisma > 75:
            resist_modifier -= (caster_charisma - 75) // 8

        # Build resist chance
        resist_chance = target_resist + level_mod + resist_modifier

        # Charm-specific minimum resist chance on tick saves
        if is_tick_save:
            if resist_chance < self.charm_min_resist:
                resist_chance = self.charm_min_resist

        # Classic resist minimum floors (applied to non-tick saves in classic)
        if self.use_classic_resists and not is_tick_save:
            # NPCs have minimum resist chances based on level difference
            if leveldiff > -11 and target_level > 14:
                if resist_chance < 10:  # SpellResistHighMinimumResistChance
                    resist_chance = 10
            elif leveldiff < -20 or target_level < 15:
                if resist_chance < 2:  # SpellResistLowMinimumResistChance
                    resist_chance = 2
            else:
                if resist_chance < 6:  # SpellResistBetweenMinimumResistChance
                    resist_chance = 6

        # Cap at 200 for classic
        if self.use_classic_resists and resist_chance > 200:
            resist_chance = 200

        return {
            'resist_chance': resist_chance,
            'level_mod': level_mod,
            'resist_modifier': resist_modifier,
            'leveldiff': leveldiff,
            'success_chance': max(0, min(100, (200 - resist_chance) / 2))  # Convert 0-200 roll to percentage
        }

    def calculate_charm_break_probability(self, caster_level: int, target_level: int,
                                         target_mr: int, resist_diff: int,
                                         caster_charisma: int = 75,
                                         is_enchanter: bool = True,
                                         num_ticks: int = 100,
                                         num_simulations: int = 10000) -> Dict:
        """
        Simulate charm break probability over time.

        Charm breaks are checked each tick (6 seconds). The process is:
        1. 50% chance the check even happens
        2. If check happens, run CheckResistSpell with tick_save=True
        3. If resist check fails (returns != 100), charm breaks

        Args:
            caster_level: Level of the caster
            target_level: Level of the target
            target_mr: Magic resist of the target
            resist_diff: Spell resist modifier
            caster_charisma: Charisma of caster (only matters for enchanters on initial cast)
            is_enchanter: Whether the caster is an enchanter (CHA bonus only for enchanters)
            num_ticks: Number of ticks to simulate (1 tick = 6 seconds)
            num_simulations: Number of Monte Carlo simulations to run

        Returns:
            Dictionary with break probabilities at various time points
        """

        # Calculate the base resist chance for tick saves
        resist_info = self.calculate_resist_chance(
            caster_level, target_level, target_mr, resist_diff,
            caster_charisma, is_enchanter, is_tick_save=True
        )

        # Single tick break probability
        # 50% chance check happens, then roll 0-200 vs resist_chance
        resist_chance = resist_info['resist_chance']
        check_happens_prob = 0.50
        resist_succeeds_prob = min(1.0, resist_chance / 200.0)
        single_tick_break_prob = check_happens_prob * resist_succeeds_prob

        # Run Monte Carlo simulation
        breaks_by_tick = [0] * (num_ticks + 1)
        charms_still_active = 0  # Count charms that lasted the full duration
        break_times = []  # Track actual break times for percentile calculations

        for _ in range(num_simulations):
            broke = False
            for tick in range(1, num_ticks + 1):
                # 50% chance check happens
                if random.randint(0, 99) < 50:
                    # Roll 0-200 vs resist_chance
                    roll = random.randint(0, 200)
                    if roll <= resist_chance:
                        # Charm broke!
                        breaks_by_tick[tick] += 1
                        break_times.append(tick * 6)  # Store break time in seconds
                        broke = True
                        break

            if not broke:
                charms_still_active += 1
                break_times.append(num_ticks * 6)  # Count as lasting full duration

        # Calculate cumulative probabilities
        cumulative_breaks = 0
        tick_probabilities = []

        for tick in range(1, num_ticks + 1):
            cumulative_breaks += breaks_by_tick[tick]
            prob_broke_by_tick = (cumulative_breaks / num_simulations) * 100
            prob_still_held = 100 - prob_broke_by_tick

            tick_probabilities.append({
                'tick': tick,
                'seconds': tick * 6,
                'minutes': round(tick * 6 / 60, 1),
                'prob_broke': round(prob_broke_by_tick, 2),
                'prob_held': round(prob_still_held, 2)
            })

        # Calculate expected duration (mean time to break)
        # For charms that never broke, use num_ticks as a conservative estimate
        total_ticks = sum((breaks_by_tick[i] * i) for i in range(1, num_ticks + 1))
        total_ticks += charms_still_active * num_ticks
        avg_ticks = total_ticks / num_simulations if num_simulations > 0 else 0

        # Calculate percentiles and min/max from break_times
        sorted_break_times = sorted(break_times)

        def percentile(data, p):
            """Calculate percentile from sorted data."""
            if not data:
                return 0
            k = (len(data) - 1) * (p / 100.0)
            f = int(k)
            c = f + 1
            if c >= len(data):
                return data[-1]
            return data[f] + (k - f) * (data[c] - data[f])

        duration_stats = {
            'min': min(break_times) if break_times else 0,
            'max': max(break_times) if break_times else 0,
            'avg': avg_ticks * 6,
            'median': percentile(sorted_break_times, 50),
            'p90': percentile(sorted_break_times, 90),
            'p95': percentile(sorted_break_times, 95),
            'p99': percentile(sorted_break_times, 99),
        }

        return {
            'single_tick_break_probability': round(single_tick_break_prob * 100, 2),
            'resist_info': resist_info,
            'tick_probabilities': tick_probabilities,
            'expected_duration_seconds': round(avg_ticks * 6, 1),
            'expected_duration_minutes': round(avg_ticks * 6 / 60, 2),
            'duration_stats': {
                'min_seconds': round(duration_stats['min'], 1),
                'min_minutes': round(duration_stats['min'] / 60, 2),
                'max_seconds': round(duration_stats['max'], 1),
                'max_minutes': round(duration_stats['max'] / 60, 2),
                'avg_seconds': round(duration_stats['avg'], 1),
                'avg_minutes': round(duration_stats['avg'] / 60, 2),
                'median_seconds': round(duration_stats['median'], 1),
                'median_minutes': round(duration_stats['median'] / 60, 2),
                'p90_seconds': round(duration_stats['p90'], 1),
                'p90_minutes': round(duration_stats['p90'] / 60, 2),
                'p95_seconds': round(duration_stats['p95'], 1),
                'p95_minutes': round(duration_stats['p95'] / 60, 2),
                'p99_seconds': round(duration_stats['p99'], 1),
                'p99_minutes': round(duration_stats['p99'] / 60, 2),
            },
            'charms_still_active': charms_still_active,
            'percent_lasting_full_duration': round((charms_still_active / num_simulations) * 100, 2),
            'num_simulations': num_simulations
        }

    def calculate_initial_land_chance(self, caster_level: int, target_level: int,
                                      target_mr: int, resist_diff: int,
                                      caster_charisma: int = 75,
                                      is_enchanter: bool = True) -> Dict:
        """
        Calculate the probability the charm will land initially (not tick save).

        Args:
            caster_level: Level of the caster
            target_level: Level of the target
            target_mr: Magic resist of the target
            resist_diff: Spell resist modifier
            caster_charisma: Charisma of caster (only matters for enchanters)
            is_enchanter: Whether the caster is an enchanter (CHA bonus only for enchanters)

        Returns:
            Dictionary with success probability and resist details
        """
        resist_info = self.calculate_resist_chance(
            caster_level, target_level, target_mr, resist_diff,
            caster_charisma, is_enchanter, is_tick_save=False
        )

        return resist_info

