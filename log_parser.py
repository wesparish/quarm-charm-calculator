"""
EverQuest Log File Parser for Charm Duration Analysis

Parses EQ log files to extract charm spell cast times and break times,
calculating actual charm durations for analysis.

Automatically supports all charm spells from the database:
- Druid: 7 animal charm spells (Befriend Animal → Command of Tunare)
- Enchanter: 6 charm spells (Charm → Command of Druzzil)
- Necromancer: 1 undead charm spell (Beguile Undead)
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
import statistics
from charm_spells_data import CHARM_SPELLS as CHARM_SPELLS_DB


class CharmLogParser:
    """Parse EQ log files to extract charm duration statistics."""

    def __init__(self):
        # Load spell names from the database
        # Sort by length (longest first) to match more specific names first
        # e.g., "Beguile Undead" before "Beguile"
        self.CHARM_SPELLS = sorted(
            [spell['name'] for spell in CHARM_SPELLS_DB.values()],
            key=len,
            reverse=True
        )
        self.charm_casts = {}  # spell_name -> list of (cast_time, break_time, duration)

    def parse_log_content(self, log_content: str) -> Dict:
        """
        Parse log file content and extract charm duration data.

        Args:
            log_content: Raw log file content as string

        Returns:
            Dictionary with statistics per spell and overall
        """
        lines = log_content.split('\n')

        # Track active charms per spell
        active_charms = {}  # spell_name -> cast_time

        for line in lines:
            # Extract timestamp
            timestamp_match = re.search(r'\[(.*?)\]', line)
            if not timestamp_match:
                continue

            timestamp_str = timestamp_match.group(1)

            try:
                timestamp = datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Y')
            except ValueError:
                # Try alternative format
                try:
                    timestamp = datetime.strptime(timestamp_str, '%c')
                except ValueError:
                    continue

            # Check for charm spell casts
            for spell in self.CHARM_SPELLS:
                if f'begin casting {spell}' in line.lower() or f'You begin casting {spell}' in line:
                    active_charms[spell] = timestamp
                    break

            # Check for charm breaks
            if 'Your charm spell has worn off' in line:
                # Find which charm broke (use most recent cast)
                if active_charms:
                    # Get the most recently cast charm
                    spell_name = max(active_charms.keys(), key=lambda k: active_charms[k])
                    cast_time = active_charms[spell_name]
                    duration = (timestamp - cast_time).total_seconds()

                    # Filter out unreasonable durations (< 1 second or > 2 hours)
                    if 1 < duration < 7200:
                        if spell_name not in self.charm_casts:
                            self.charm_casts[spell_name] = []
                        self.charm_casts[spell_name].append({
                            'cast_time': cast_time,
                            'break_time': timestamp,
                            'duration': duration
                        })

                    # Remove this charm from active
                    del active_charms[spell_name]

        return self.calculate_statistics()

    def calculate_statistics(self) -> Dict:
        """Calculate statistics from parsed charm data."""
        all_durations = []
        spell_stats = {}

        for spell_name, casts in self.charm_casts.items():
            durations = [c['duration'] for c in casts]
            all_durations.extend(durations)

            if durations:
                sorted_durations = sorted(durations)
                spell_stats[spell_name] = {
                    'count': len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'avg': statistics.mean(durations),
                    'median': statistics.median(durations),
                    'p90': self._percentile(sorted_durations, 90),
                    'p95': self._percentile(sorted_durations, 95),
                    'p99': self._percentile(sorted_durations, 99),
                }

        # Overall statistics
        overall_stats = None
        if all_durations:
            sorted_all = sorted(all_durations)
            overall_stats = {
                'count': len(all_durations),
                'min': min(all_durations),
                'max': max(all_durations),
                'avg': statistics.mean(all_durations),
                'median': statistics.median(all_durations),
                'p90': self._percentile(sorted_all, 90),
                'p95': self._percentile(sorted_all, 95),
                'p99': self._percentile(sorted_all, 99),
            }

        return {
            'overall': overall_stats,
            'by_spell': spell_stats,
            'total_charms_found': len(all_durations)
        }

    @staticmethod
    def _percentile(sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0

        k = (len(sorted_data) - 1) * (percentile / 100.0)
        f = int(k)
        c = f + 1

        if c >= len(sorted_data):
            return sorted_data[-1]

        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable string."""
        mins = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"


def parse_log_file(file_path: str) -> Dict:
    """
    Parse an EQ log file and return charm duration statistics.

    Args:
        file_path: Path to the EQ log file

    Returns:
        Dictionary with charm duration statistics
    """
    parser = CharmLogParser()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    return parser.parse_log_content(content)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python log_parser.py <path_to_eq_log_file>")
        sys.exit(1)

    log_file = sys.argv[1]
    stats = parse_log_file(log_file)

    print("=" * 60)
    print("EverQuest Charm Duration Analysis")
    print("=" * 60)

    if stats['overall']:
        print("\nOVERALL STATISTICS:")
        print(f"  Total charms found: {stats['overall']['count']}")
        print(f"  Average duration:   {CharmLogParser.format_duration(stats['overall']['avg'])} ({stats['overall']['avg']:.1f}s)")
        print(f"  Median duration:    {CharmLogParser.format_duration(stats['overall']['median'])} ({stats['overall']['median']:.1f}s)")
        print(f"  Min duration:       {CharmLogParser.format_duration(stats['overall']['min'])} ({stats['overall']['min']:.1f}s)")
        print(f"  Max duration:       {CharmLogParser.format_duration(stats['overall']['max'])} ({stats['overall']['max']:.1f}s)")
        print(f"  P90 duration:       {CharmLogParser.format_duration(stats['overall']['p90'])} ({stats['overall']['p90']:.1f}s)")
        print(f"  P95 duration:       {CharmLogParser.format_duration(stats['overall']['p95'])} ({stats['overall']['p95']:.1f}s)")
        print(f"  P99 duration:       {CharmLogParser.format_duration(stats['overall']['p99'])} ({stats['overall']['p99']:.1f}s)")

    if stats['by_spell']:
        print("\nBY SPELL:")
        for spell, spell_stats in sorted(stats['by_spell'].items()):
            print(f"\n  {spell} ({spell_stats['count']} charms):")
            print(f"    Average: {CharmLogParser.format_duration(spell_stats['avg'])} ({spell_stats['avg']:.1f}s)")
            print(f"    Median:  {CharmLogParser.format_duration(spell_stats['median'])} ({spell_stats['median']:.1f}s)")
            print(f"    Min/Max: {CharmLogParser.format_duration(spell_stats['min'])} / {CharmLogParser.format_duration(spell_stats['max'])}")
            print(f"    P90/P95/P99: {CharmLogParser.format_duration(spell_stats['p90'])} / {CharmLogParser.format_duration(spell_stats['p95'])} / {CharmLogParser.format_duration(spell_stats['p99'])}")

    if not stats['overall']:
        print("\nNo charm data found in log file.")

