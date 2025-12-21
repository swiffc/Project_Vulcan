# PROJECT VULCAN - USEFUL REPOSITORIES & VISUAL STANDARDS

---

# CRITICAL RULE: ALWAYS SHOW VISUAL EXAMPLES

## WRONG:
"Consider using a hole table."

## RIGHT:
```
CURRENT:                    RECOMMENDED:
0"-+-3/16"-+-3/8"-+...      HOLE TABLE:
   |      |      |          ID | X   | Y   | DIA
   o      o      o          A1 |3/16"|1-5/8"|11/16"
(stacked dims)              A2 |3/8" |1-5/8"|11/16"
```

---

# USEFUL GITHUB REPOS

## Drawing OCR:
- **eDOCr**: github.com/javvi51/eDOCr - Engineering drawing OCR
- **Image2CAD**: github.com/adityaintwala/Image2CAD - Drawing to DXF
- **Text Detection**: github.com/2Obe/Text-Detection-on-Technical-Drawings

## Structural Engineering:
- **AISC Database**: github.com/buddyd16/Structural-Engineering
- **steelpy**: pypi.org/project/steelpy/
- **pyaisc**: github.com/mwhit74/pyaisc

## Hole Detection:
- **OpenCV HoughCircles**: Built-in circle detection

---

# MANDATORY CROSS-CHECK

EVERY PART must be checked against mating parts:

1. **HOLE ALIGNMENT**: +/-1/16" tolerance
2. **HOLE SIZE MATCH**: Same bolt = same hole
3. **PATTERN COUNT**: Same number of holes
4. **ASSEMBLY FIT**: No interferences

This is NOT optional - it's the CORE function!

---

# VISUAL TEMPLATES

## Edge Distance:
```
PROBLEM:          CORRECT:
+------+          +--------+
| o    |0.5"      |   o    |1.5"
+------+          +--------+
TOO CLOSE!        ADEQUATE
```

## Hole Alignment:
```
MISMATCH:         ALIGNED:
Part A: o at 6-1/4"    o at 6-1/4"
Part B: o at 6"        o at 6-1/4"
        ^ FAIL!        ^ OK!
```