# Quick Usage Guide

## Starting the Server

### Option 1: Using the start script (Recommended)
```bash
cd ~/workspace/QuarmCharmCalculator
./start.sh
```
This automatically creates and activates a Python virtual environment, keeping your system Python clean.

### Option 2: Manual start with virtual environment
```bash
cd ~/workspace/QuarmCharmCalculator

# First time only: create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### Option 3: System-wide (not recommended)
```bash
cd ~/workspace/QuarmCharmCalculator
pip3 install -r requirements.txt
python3 app.py
```

The server will start on http://localhost:5000

## Testing the Calculator

Run the test suite to verify calculations:
```bash
cd ~/workspace/QuarmCharmCalculator
python3 test_calculator.py
```

## Understanding the Results

### Initial Land Chance
This is the probability your charm spell will successfully land on the initial cast.
- > 90%: Excellent chance to land
- 70-90%: Good chance to land
- 50-70%: Moderate chance
- < 50%: Poor chance, consider a stronger spell or different target

### Per-Tick Break Chance
Every 6 seconds, there's a 50% chance a resist check occurs. This shows the effective probability per tick that charm breaks.
- < 2%: Very stable charm
- 2-5%: Moderately stable
- 5-10%: Unstable, expect frequent breaks
- > 10%: Very unstable

### Expected Duration
The average time the charm will last before breaking. This is calculated from 10,000 Monte Carlo simulations.

## Key Mechanics

### ⚠️ Charisma Effect (ENCHANTER ONLY!)
**CRITICAL: Charisma bonuses ONLY apply to Enchanters!**

From the EQMacEmu source code (`zone/spells.cpp` line 4151):
```cpp
if (!tick_save && caster->GetClass() == Class::Enchanter) {
    if (IsCharmSpell(spell_id) || IsMezSpell(spell_id)) {
        if (caster->GetCHA() > 75) {
            resist_modifier -= (caster->GetCHA() - 75) / 8;
        }
    }
}
```

For **Enchanters** casting charm or mez:
- Every 8 points of CHA above 75 reduces the spell's resist modifier by 1
- Example: 200 CHA = (200-75)/8 = 15.625 reduction in resist modifier
- This makes higher CHA very valuable for charm stability
- **This bonus only applies on the initial cast, NOT on tick saves (charm break checks)**

For **Druids and Necromancers**:
- Charisma does NOT affect charm at all
- Save your plat on CHA gear - it won't help your charm!
- Focus on other stats instead

### Six Level Rule (Quarm Specific)
If the NPC is BOTH:
- 7+ levels higher than you, OR
- 25%+ higher level than you

Then a massive resist bonus (1000) is applied, making charm nearly impossible.

Examples:
- Level 50 vs Level 57+: Six Level Rule applies
- Level 50 vs Level 63: Six Level Rule applies (63 > 50 * 1.25)
- Level 60 vs Level 67+: Six Level Rule applies

### Level Modifier
The level difference between caster and target affects resist chance:
- Same level: 0 modifier
- Target lower: Negative modifier (easier to charm)
- Target higher: Positive modifier (harder to charm)
- Formula: (level_diff^2) / 2

### Tick Save Mechanics
When charm is checked each tick:
1. 50% chance the check occurs at all
2. If check occurs, caster level is treated as +4 for calculation
3. Roll 0-200 vs resist_chance
4. If roll <= resist_chance, charm breaks
5. Minimum resist chance on tick saves is 5 (configurable)

## Common Scenarios

### Charming Blues (Lower Level)
- Easy initial land
- Very stable (low break chance)
- Great for long-term pets

### Charming Whites (Same Level)
- Good land chance with proper spell
- Moderate stability
- Standard hunting scenario

### Charming Yellows/Reds (Higher Level)
- Harder to land initially
- Less stable (higher break chance)
- Need higher resist diff spells (CoD)
- Watch for Six Level Rule!

## Spell Selection Guide

- **Charm (-30)**: Levels 1-29, good for blues
- **Beguile (-30)**: Levels 1-39, slightly better cap
- **Cajoling Whispers (-30)**: Levels 1-44
- **Allure (-50)**: Levels 1-49, significantly better
- **Boltran's Agacerie (-50)**: Levels 1-51
- **Ordinance (-100)**: Levels 1-53, raid-level charm
- **Command of Druzzil (-200)**: Levels 1-55, strongest charm

Higher negative resist diff = easier to land and more stable!

