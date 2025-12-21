# PROJECT VULCAN - MULTI-DRAWING ASSEMBLY STRUCTURE
## Understanding Assembly Relationships

---

# ASSEMBLY STRUCTURE

```
S25139-5A (Sheet 1) <- MASTER ASSEMBLY
    |
    +-- Shows how ALL parts fit together
    +-- Contains complete BOM (27 items)
    |
    +-- DETAIL DRAWINGS (Sheets 2-49):
        +-- 5A-1 MID_COLUMN
        +-- 5A-2 END_COLUMN
        +-- 5A-X FLOOR_EXTENSION-2
        +-- ... all parts
```

---

# KEY INSIGHT

**Sheet 1 (5A) = ASSEMBLY = Master reference for ALL mating relationships**

The bot MUST understand:
1. Parts shown touching in assembly = must have matching holes
2. BOM shows QUANTITY - must check ALL instances

---

# MATING RELATIONSHIP EXAMPLE

5A-X (FLOOR_EXTENSION-2) connects to:
- 5A-R (FLOOR_SPLICE_PANEL) - splice at edges
- 5A-W (FLOOR_STIFFENER) - bolts to underside  
- 5A-Y (FLOOR_EXTENSION-3) - adjacent section

For each pair: VERIFY HOLES ALIGN!

---

# BOT WORKFLOW

1. Find Assembly Drawing (Sheet 1)
2. Extract Complete BOM
3. Build Mating Relationship Map
4. Cross-Check All Hole Patterns
5. Flag Mismatches

---

# OLD vs NEW APPROACH

**OLD (Single Part):**
```
Check 5A-X alone -> "Looks good!" 
```
WRONG! Doesn't verify it fits!

**NEW (Assembly-Aware):**
```
Check 5A-X against 5A-W, 5A-R, 5A-Y
-> "Holes align? YES/NO"
```
CORRECT! Verified it fits in assembly