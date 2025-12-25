# API 661 COMPREHENSIVE STANDARDS DATABASE
## Full Scope Reference for ACHE Design Validation

**Standard**: API 661 / ISO 13706, 7th Edition (2013, Reaffirmed 2018/2024)
**Supplementary**: IOGP S-710 (JIP33)

---

## 1. TUBE BUNDLE ASSEMBLY (Section 7.1)

### 1.1 Bundle Frame Requirements (7.1.1)
| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Lateral movement | ≥ 6 mm (1/4") both directions OR ≥ 12.7 mm (1/2") one direction | 7.1.1.2 |
| Tube support spacing | ≤ 1.83 m (6 ft) center-to-center | 7.1.1.4 |
| Tube keeper location | At each tube support | 7.1.1.5 |
| Tube keeper attachment | **BOLTED to side frames (NOT welded)** | 7.1.1.5 |
| Air seals / P-strips | Throughout bundle AND bay | 7.1.1.8 |
| Thermal expansion provision | Shall be provided | 7.1.1.3 |

### 1.2 Condenser Tube Slope
| Configuration | Slope Requirement | Reference |
|---------------|-------------------|-----------|
| Single-pass condenser | ≥ 10 mm/m (1/8 in/ft) toward outlet | 7.1.1.6 |
| Multi-pass (last pass) | ≥ 10 mm/m (1/8 in/ft) toward outlet | 7.1.1.7 |

---

## 2. HEADER BOX DESIGN (Section 7.1.6)

### 2.1 Header Types
| Type | Description | Max Pressure | Application |
|------|-------------|--------------|-------------|
| **Plug header** | Threaded plugs opposite each tube | Any (required ≥435 psi or H2) | High pressure |
| **Cover plate header** | Removable bolted cover plate | < 435 psi (3 MPa) | Fouling service |
| **Bonnet header** | Removable dished/flanged bonnet | < 435 psi (3 MPa) | Exotic alloy tubesheets |

### 2.2 Split Header Requirements (7.1.6.1.2) ⭐ CRITICAL
| Condition | Requirement |
|-----------|-------------|
| **Trigger** | ΔT between inlet/outlet > 110°C (200°F) |
| **Required action** | U-tube construction, split headers, or other strain relief |
| **Reason** | Prevent pass partition distortion and tube joint leakage |
| **Analysis** | Required regardless of ΔT per 7.1.6.1.3 |

### 2.3 Header Design Codes
| Code | Application |
|------|-------------|
| ASME VIII Div 1, Appendix 13 | Rectangular pressure vessels |
| WRC 107/297 | Nozzle loads on rectangular headers |
| FEA (per ASME U-2(g)) | Complex geometries |

---

## 3. PLUG REQUIREMENTS (7.1.7)

### 3.1 Plug Specifications
| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Type | Shoulder type with straight-threaded shank | 7.1.7.1 |
| Hollow plugs | **NOT allowed** | 7.1.7.2 |
| Head type | Hexagonal | 7.1.7.3 |
| Head min dimension | ≥ plug shoulder diameter (across flats) | 7.1.7.3 |
| Seal | Gasket between plug flange and plug sheet | 7.1.7.4 |
| Centering | Self-centering taper or equivalent | 7.1.7.5 |

### 3.2 Plug Spacing (Table 2)
| Bolt Ø (mm/in) | Min Spacing Bmin (mm/in) |
|----------------|--------------------------||
| 16 / - | 38 / 1-1/2 |
| 20 / 3/4 | 41 / 1-5/8 |
| 22 / 7/8 | 44 / 1-3/4 |
| 24 / 1 | 48 / 1-7/8 |
| 27 / - | 51 / 2 |
| 30 / - | 83 / 3-1/4 |

### 3.3 Gasket Requirements
| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Material | Softer than gasket contact surface | 8.1 |
| Metal gasket hardness (CS) | ≤ HRB 68 | 8.1.9 |
| Metal gasket hardness (SS) | ≤ HRB 82 | 8.1.9 |
| Gaskets | One piece | 7.1.8.7 |

---

## 4. NOZZLE REQUIREMENTS (7.1.9, 7.1.10)

### 4.1 Prohibited Nozzle Sizes (7.1.9.5)
| DN (NPS) | Status |
|----------|--------|
| DN 32 (1-1/4") | ❌ PROHIBITED |
| DN 65 (2-1/2") | ❌ PROHIBITED |
| DN 90 (3-1/2") | ❌ PROHIBITED |
| DN 125 (5") | ❌ PROHIBITED |
| < DN 20 (3/4") | ❌ PROHIBITED |

### 4.2 Nozzle General Requirements
| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Min size | DN 20 (3/4") | 7.1.9.5 |
| Flanged | DN 40 (1-1/2") and larger | 7.1.9.5 |
| H2 service | ALL connections flanged | 7.1.9.3 |
| Threaded nozzles | NOT allowed (per IOGP S-710) | S-710 |
| Set-in nozzles | Flush with inside surface | S-710 |
| Inside corner radius | Min 3 mm (1/8") | S-710 |

### 4.3 Minimum Nozzle Neck Thickness (Table 3)
| Nozzle Size DN (NPS) | CS/LAS | SS/HA |
|---------------------|--------|-------|
| 20 (3/4") | Sch 80 | Sch 40S |
| 25 (1") | Sch 80 | Sch 40S |
| 40-80 (1.5"-3") | Sch 80 | Sch 40S |
| 100-200 (4"-8") | Sch 40 | Sch 40S |
| ≥250 (≥10") | 9.5mm/3/8" | 6.35mm/1/4" |

### 4.4 Maximum Nozzle Loads (Table 4 / Figure 8)
| Nozzle NPS | Fx (lb) | Fy (lb) | Fz (lb) | Mx (ft-lb) | My (ft-lb) | Mz (ft-lb) |
|------------|---------|---------|---------|------------|------------|------------|
| 2" | 300 | 400 | 300 | 400 | 800 | 400 |
| 3" | 450 | 750 | 500 | 1100 | 3000 | 750 |
| 4" | 600 | 1000 | 600 | 1600 | 6000 | 1000 |
| 6" | 750 | 1650 | 900 | 2700 | 9000 | 1800 |

**Sum of loads on fixed header**: Σ(actual/allowed) ≤ 1.0

---

## 5. TUBE-TO-TUBESHEET JOINTS (7.1.6)

### 5.1 Joint Types
| Type | Description | Application |
|------|-------------|-------------|
| Expanded only | Roller/hydraulic expanded into grooves | Standard service |
| Seal welded | Expansion + single pass TIG weld | Leak prevention |
| Strength welded | 2-pass TIG weld (primary strength) | High pressure, fixed |
| Expanded + seal welded | Both methods | Fouling/corrosive |

### 5.2 Expansion Requirements (IOGP S-710)
| Parameter | Requirement |
|-----------|-------------|
| Expansion length | Full tubesheet thickness |
| Start from | 6 mm from weld OR 3 mm from tube-side face |
| End at | 3 mm from air-side face |
| Tube protrusion | 1.5-5 mm beyond tubesheet face |
| Wall reduction check | 2% of joints (min 5) per bundle |

### 5.3 Groove Requirements (IOGP S-710)
| Parameter | Requirement |
|-----------|-------------|
| Number of grooves | Two |
| Groove width | 3 mm (1/8") |
| Groove location (expanded only) | ≥ 6 mm + CA from process face |
| Groove location (welded + expanded) | ≥ 9 mm from weld edge |

---

## 6. COVER PLATE / BONNET HEADERS (IOGP S-710)

| Header Type | Restriction |
|-------------|-------------|
| Cover plate headers | NOT allowed > 435 psig |
| Removable bonnet headers | NOT allowed |
| Gasket joint type Fig 4c | NOT allowed |
| Flange welds | Full penetration required |
| Through-bolt min Ø | 20 mm (3/4") |
| Gasket min width (perimeter) | 13 mm (1/2") |
| Gasket min width (partition) | 10 mm (3/8") |

---

## 7. FINNED TUBE REQUIREMENTS (7.1.11)

### 7.1 Fin Types
| Type | Max Temp | Application |
|------|----------|-------------|
| L-footed (tension wound) | ~175°C (350°F) | Standard service |
| LL (overlapped L) | ~175°C | Corrosive atmosphere |
| KL (knurled L) | ~230°C | Higher temp, better bond |
| Embedded (grooved) | ~400°C (750°F) | High temp, cyclic |
| Extruded (integral) | ~315°C (600°F) | High temp, corrosive |

### 7.2 Fin Specifications (IOGP S-710)
| Parameter | Requirement |
|-----------|-------------|
| Material | Aluminum (unless specified) |
| Extruded sleeve min thickness | 0.51 mm between fins |
| Min fin tip thickness | 0.2 mm (integral/extruded) |
| Fin OD tolerance | ± 1 mm |
| Fin density undertolerance | ≤ 3% |
| Min gap between adjacent tubes | 6.35 mm (1/4") |

### 7.3 Minimum Tube Wall Thickness (Table 5)
| Material | Min Wall |
|----------|----------|
| Carbon steel | 2.11 mm (14 BWG) |
| Low alloy steel | 2.11 mm |
| Austenitic SS | 1.65 mm (16 BWG) |
| Duplex SS | 1.65 mm |
| Cu-Ni | 1.65 mm |
| Titanium | 0.89 mm (20 BWG) |

---

## 8. FAN SYSTEM (Section 7.2)

### 8.1 Fan Tip Clearance (Table 6)
| Fan Diameter | Min | Max |
|--------------|-----|-----|
| ≤ 3 m (10 ft) | 6.35 mm (1/4") | 12.7 mm (1/2") |
| 3-3.5 m | 6.35 mm | 15.9 mm (5/8") |
| > 3.5 m | 6.35 mm | 19.05 mm (3/4") |

### 8.2 Fan Requirements
| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Min coverage | 40% of bundle face area | 7.2.1 |
| Max dispersion angle | 45° | Figure 6 |
| Airflow reserve | 10% at rated speed | 7.2.1.3 |
| GRP UV protection | Required | 7.2.1.6 |
| Hub seal disc | Required | S-710 |

### 8.3 Fan Guard (Table 8)
| Fan Diameter | Min Mesh Thickness |
|--------------|-------------------|
| ≤ 1.8 m (6 ft) | 1.5 mm (0.060") |
| > 1.8 m | 2.0 mm (0.080") |
| Hinged section | Required |

---

## 9. DRIVE SYSTEM (7.2.4, 7.2.5)

### 9.1 Drive Type Selection
| Power Range | Drive Type | Service Factor |
|-------------|------------|----------------|
| ≤ 30 kW (40 HP) | V-belt | ≥ 1.4 |
| ≤ 45 kW (60 HP) | HTD belt | 1.8-2.0 |
| > 45 kW (60 HP) | Gear drive | Required |

### 9.2 Bearing Requirements
| Component | L10 Life | Reference |
|-----------|----------|-----------|
| Motor bearings | ≥ 40,000 hrs | 7.2.4.1 |
| Shaft bearings | ≥ 50,000 hrs | 7.2.5 |
| Calculation | Per ISO 281/ISO 76 | 7.2.5 |

---

## 10. PLENUM AND STRUCTURE (7.3, 7.4)

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Min plenum depth | 915 mm (36") | S-710 |
| Induced draft fan location | ≥ 35% of fan Ø from upper tube row | S-710 |
| Fan ring inlet (forced) | Conical or rounded (inlet bell) | 7.3 |
| Hub seal disc | Required | S-710 |
| Brake device (induced) | Self-actuating | S-710 |

---

## 11. ACCESS AND SAFETY (7.5)

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Platform/walkway width | 915 mm (36") min | S-710 |
| Vertical clearance (forced) | 2.1 m (7 ft) from fan ring | S-710 |
| Vertical clearance (induced) | 2.1 m (7 ft) from bundle | S-710 |
| Grounding lugs | One per header | S-710 |

---

## 12. WINTERIZATION (Annex C)

### 12.1 Systems
| System | Description |
|--------|-------------|
| A | Outlet louvers + fixed-pitch fans |
| B | Internal air recirculation (non-contained) |
| C | Internal air recirculation (contained) |
| D | External air recirculation |

### 12.2 Heating Coil Requirements
| Parameter | Requirement |
|-----------|-------------|
| Location | Separate bundle |
| Width | Full width of process bundle |
| Tube pitch | ≤ 2× process bundle pitch |
| Steam coil passes | Single pass |
| Steam coil slope | ≥ 10 mm/m toward outlet |

---

## 13. TESTING AND INSPECTION

### 13.1 NDE Requirements (IOGP S-710)
| Component | Examination |
|-----------|-------------|
| Plate edges before welding | MT or PT |
| Nozzle openings | 100% UT (4" around nozzle) |
| Tube-to-tubesheet welds | PT per ASME V Article 6 |

### 13.2 Hardness Testing
| Material | Max Hardness |
|----------|-------------|
| Carbon steel HAZ | 248 HV (typical) |
| Sour service | Per NACE MR0175 |

---

## 14. VIBRATION REQUIREMENTS

### 14.1 Standards
| Standard | Application |
|----------|-------------|
| ISO 10816-3 | Machines > 15 kW |
| ISO 14694 | Fans < 300 kW |
| NEMA MG-1 | Motor vibration |

### 14.2 Limits (ISO 10816-3)
| Zone | Condition | Velocity (mm/s RMS) |
|------|-----------|--------------------|
| A | Newly commissioned | ≤ 2.8 |
| B | Unrestricted | ≤ 4.5 |
| C | Restricted | ≤ 7.1 |
| D | Unacceptable | > 7.1 |

### 14.3 Resonance Avoidance
| Requirement | Details |
|-------------|--------|
| Natural frequency | ≥ 25% away from 1× and blade pass |
| Blade pass frequency | (RPM × blades) / 60 |

---

## 15. MATERIALS (Section 8)

### 15.1 Restrictions (IOGP S-710)
| Material | Restriction |
|----------|-------------|
| Cast iron | NOT allowed for pressure components |

### 15.2 Default Materials
| Component | Material |
|-----------|----------|
| Headers | CS or SS |
| Tubes | CS, SS, or alloys |
| Plugs | Same as plug sheet |
| Plenums/Fan decks | Carbon steel |

---

## 16. VALIDATOR CHECKLIST (82 checks)

### Bundle Assembly (22)
| # | Check | Ref |
|---|-------|-----|
| 1 | Tube support spacing ≤ 6 ft | 7.1.1.4 |
| 2 | Tube keeper at each support | 7.1.1.5 |
| 3 | Tube keeper bolted (not welded) | 7.1.1.5 |
| 4 | Air seals / P-strips specified | 7.1.1.8 |
| 5 | Lateral movement provision | 7.1.1.2 |
| 6 | Condenser tube slope (single-pass) | 7.1.1.6 |
| 7 | Condenser tube slope (multi-pass) | 7.1.1.7 |
| 8 | Thermal expansion provision | 7.1.1.3 |
| 9 | Min tube OD ≥ 25.4mm | 7.1.11 |
| 10 | Min tube wall per Table 5 | Table 5 |
| 11 | Fin type appropriate for temp | 7.1.11 |
| 12 | Fin end securing method | 7.1.11.7 |
| 13-16 | Fin specs (gap, OD tol, density, metallizing) | S-710 |
| 17-22 | Reserved | - |

### Header Box (18)
| # | Check | Ref |
|---|-------|-----|
| 23 | Header type vs pressure | 7.1.6 |
| 24 | Split header if ΔT > 110°C | 7.1.6.1.2 |
| 25 | Restraint relief calculations | 7.1.6.1.3 |
| 26 | Flow area ≥ tube pass area | 7.1.6.1.4 |
| 27 | Cover plate max pressure (S-710) | S-710 |
| 28 | Bonnet not used (S-710) | S-710 |
| 29 | Full pen welds on flanges | 9.4.2 |
| 30-34 | Gasket requirements | S-710 |
| 35-40 | Reserved | - |

### Plugs (8)
| # | Check | Ref |
|---|-------|-----|
| 41-48 | Shoulder type, no hollow, hex head, spacing, gaskets | 7.1.7, 8.1 |

### Nozzles (12)
| # | Check | Ref |
|---|-------|-----|
| 49-60 | Size, flanged, thickness, loads, location | 7.1.9, 7.1.10 |

### Tube-to-Tubesheet (8)
| # | Check | Ref |
|---|-------|-----|
| 61-68 | Joint type, grooves, expansion, welding, inspection | 7.1.6, S-710 |

### Fan System (10)
| # | Check | Ref |
|---|-------|-----|
| 69-78 | Tip clearance, coverage, guard, brake, resonance | 7.2, S-710 |

### Drive System (4)
| # | Check | Ref |
|---|-------|-----|
| 79-82 | Motor/shaft bearing L10, belt SF, gear drive | 7.2.4, 7.2.5 |

---

## END OF API 661 FULL SCOPE DATABASE
**Total Checks: 82**
**Last Updated: Dec 25, 2025**
