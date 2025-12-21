# PROJECT VULCAN - HOLE PATTERN & DIMENSION LAYOUT CHECKER
## Advanced Verification for Mating Parts & Drawing Best Practices

---

# MATING PART CROSS-CHECK (CRITICAL)

## The Bot MUST:
1. IDENTIFY all parts that mate to this part
2. EXTRACT hole patterns from BOTH parts
3. COMPARE hole locations (+/-1/16" tolerance)
4. FLAG mismatches

---

# DIMENSION BEST PRACTICES (ASME Y14.5)

## RULE 1: BASELINE DIMENSIONING (Best for CNC)
```
  0"  3"   6"   12"   24"   36" -> DATUM A
  |---|----|----|-----|-----|---->
  o   o    o    o     o     o   <- holes
```
All dims from ONE datum = no tolerance stacking

## RULE 2: HOLE TABLE (Best for >6 holes)
```
| ID  | X FROM LH | Y FROM BOT | DIA    |
|-----|-----------|------------|--------|
| A1  | 3-5/8"    | 1-5/8"     | 11/16" |
| A2  | 9-11/16"  | 1-5/8"     | 11/16" |
```

---

# TOLERANCE FOR ALIGNMENT

- Standard holes: +/-1/16" (0.0625")
- Oversize holes: +/-1/8" (0.125")
- Slotted holes: +/-1/4" in slot direction

IF hole centers differ > tolerance -> FLAG MISMATCH

---

# BOT SHOULD CHECK:

- [ ] Overall dims shown?
- [ ] Datum established?
- [ ] Hole pattern clear?
- [ ] Hole table for >6 holes?
- [ ] Tolerances specified?
- [ ] Dimension stacking avoided?
- [ ] All mating part holes align?