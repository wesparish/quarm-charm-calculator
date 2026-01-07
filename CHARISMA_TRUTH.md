# Charisma and Charm - The Truth

## TL;DR: **Charisma ONLY helps Enchanters!**

If you're a Druid or Necromancer, **charisma does NOT affect your charm spells at all**. Don't waste plat on CHA gear!

## The Source Code Proof

From `zone/spells.cpp` lines 4151-4161 in EQMacEmu:

```cpp
if (!tick_save && caster->GetClass() == Class::Enchanter) {
    // See http://www.eqemulator.org/forums/showthread.php?t=43370

    if (IsCharmSpell(spell_id) || IsMezSpell(spell_id)) {
        if (caster->GetCHA() > 75) {
            resist_modifier -= (caster->GetCHA() - 75) / 8;
        }

        Log(Logs::Detail, Logs::Spells, "CheckResistSpell(): Spell: %d  Charisma is modifying resist value. resist_modifier is: %i", spell_id, resist_modifier);
    }
}
```

**Key Points:**
1. The check `caster->GetClass() == Class::Enchanter` means this ONLY applies to Enchanters
2. The CHA bonus applies to charm AND mez spells
3. The bonus is: reduce resist_modifier by `(CHA - 75) / 8`
4. This only applies on the **initial cast**, NOT on tick saves (charm break checks)

## What This Means

### For Enchanters (Level 60):
- **75 CHA**: No bonus (baseline)
- **150 CHA**: -9 resist modifier (~9% better land chance)
- **200 CHA**: -15 resist modifier (~15% better land chance)
- **255 CHA**: -22 resist modifier (~22% better land chance)

### For Druids & Necromancers:
- **Any CHA**: No effect on charm whatsoever
- Your charm is based purely on: spell resist diff, your level, target level, and target MR
- Focus your stats/gear on other things!

## Calculator Fixed

The Quarm Charm Calculator has been updated to correctly handle this:
- Now has a **Class Selection** dropdown
- Select "Enchanter" to get CHA bonuses
- Select "Druid" or "Necromancer" and CHA won't affect calculations
- UI will warn you if you're not an enchanter

## Test Results

Running the same scenario as Enchanter vs Druid:
- **Level 60 Enchanter (200 CHA)** vs Level 55 NPC (50 MR), Allure:
  - Resist modifier: **-65** (spell -50, CHA bonus -15)
  - Land chance: 95%

- **Level 60 Druid (200 CHA)** vs Level 55 NPC (50 MR), Allure:
  - Resist modifier: **-50** (spell -50, NO CHA bonus)
  - Land chance: 95% (still good, but slightly worse)

The difference becomes more pronounced against higher MR targets!

## Why This Matters

Many players assume CHA helps all charmers. This is a common misconception!

**Enchanters:**
- Stack CHA - it's one of your most important stats
- CHA gear directly improves charm/mez land rates
- Worth spending plat on CHA augs, items, buffs

**Druids/Necros:**
- Don't waste money on CHA gear for charming
- Focus on HP, mana, resists, and other useful stats instead
- Your charm success depends on spell choice and target selection, not CHA

## References

- EQMacEmu Source: `zone/spells.cpp` line 4151
- Forum Discussion: http://www.eqemulator.org/forums/showthread.php?t=43370
- This applies to Quarm server (based on EQMacEmu)

