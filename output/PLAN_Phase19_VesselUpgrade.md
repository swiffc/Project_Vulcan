
# PHASE 19: Pressure Vessel Capability Upgrade (Gap Closure)

## Objective
Enable the Project Vulcan Chatbot to model complex Pressure Vessels (curved repads, nozzles, manways) by implementing the missing Surface Modeling capabilities in the SolidWorks COM Adapter.

## Current State Analysis
- **Logic**: Orchestrator understands "Nozzles" and "Repads" as engineering concepts.
- **Data**: `standards_db.py` contains Pipe/Flange dimensions.
- **Validation**: `welding_validator.py` checks bevels and root gaps.
- **Execution GAP**: `solidworks_com.py` lacks `Offset Surface` and `Thicken` commands, preventing accurate modeling of repads on curved shells.

## Execution Plan (Step-by-Step)

### Step 1: Update SolidWorks COM Adapter (`desktop_server/com/solidworks_com.py`)
- [ ] **Add `CMD_OFFSET_SURFACE`**:
  - Implement API call `SelectByID2` for face selection.
  - Implement `InsertOffsetSurface` with distance parameter (0.0 for copy).
- [ ] **Add `CMD_THICKEN`**:
  - Implement `FeatureManager.FeatureThicken` to turn surface into solid (Repad).
- [ ] **Add `CMD_CHAMFER_ANGLE`**:
  - Implement `FeatureManager.InsertFeatureChamfer` with Angle/Distance parameters (for 37.5° weld prep).

### Step 2: Create Vessel Strategies (`data/cad-strategies/`)
- [ ] **Create `repad_curved.json`**:
  - Logic: Offset Shell -> Sketch Circle -> Trim Surface -> Thicken.
- [ ] **Create `vessel_shell.json`**:
  - Logic: Revolve 360° (Shell + Heads in one or separate bodies).

### Step 3: Verify Workflow
- [ ] **Test Case**: "Build a 6ft x 30ft Vessel with 30inch Manway and Repad."
- [ ] **Validation**: Ensure Repad curvature matches Shell OD (Geometry Check).
- [ ] **Validation**: Ensure Repad contains 1/4" Weep Hole (Feature Check).

## completion criteria
- Chatbot can execute "Build Repad" command without erroring on "Unknown Command".
- SolidWorks produces a curved solid body (Repad) flush with a cylinder.
