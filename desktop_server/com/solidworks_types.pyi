"""
SolidWorks API Type Stubs for Python
====================================
Provides type hints and autocomplete for SolidWorks COM API.
Based on SolidWorks API 2024 (SW32).

Usage:
    from desktop_server.com.solidworks_types import ISldWorks, IModelDoc2
"""

from typing import Any, List, Tuple, Optional, Union, overload
from enum import IntEnum


# =============================================================================
# Enumerations
# =============================================================================

class swDocumentTypes_e(IntEnum):
    """Document type constants."""
    swDocNONE = 0
    swDocPART = 1
    swDocASSEMBLY = 2
    swDocDRAWING = 3


class swEndConditions_e(IntEnum):
    """Feature end conditions."""
    swEndCondBlind = 0
    swEndCondThroughAll = 1
    swEndCondThroughAllBoth = 2
    swEndCondUpToVertex = 3
    swEndCondUpToSurface = 4
    swEndCondOffsetFromSurface = 5
    swEndCondMidPlane = 6
    swEndCondUpToBody = 7


class swMateType_e(IntEnum):
    """Mate types."""
    swMateCOINCIDENT = 0
    swMateCONCENTRIC = 1
    swMatePERPENDICULAR = 2
    swMatePARALLEL = 3
    swMateTANGENT = 4
    swMateDISTANCE = 5
    swMateANGLE = 6
    swMateUNKNOWN = 7
    swMateSYMMETRIC = 8
    swMateCAMFOLLOWER = 9
    swMateGEAR = 10
    swMateWIDTH = 11
    swMateLOCK = 12
    swMateSCREW = 13
    swMateLINEARCOUPLER = 14
    swMateUNIVERSALJOINT = 15
    swMatePATH = 16
    swMateSLOT = 17
    swMateHINGE = 18
    swMateMAGNET = 19


class swMateAlign_e(IntEnum):
    """Mate alignment."""
    swMateAlignALIGNED = 0
    swMateAlignANTI_ALIGNED = 1
    swMateAlignCLOSEST = 2


class swSelectType_e(IntEnum):
    """Selection types."""
    swSelNOTHING = 0
    swSelVERTICES = 1
    swSelEDGES = 2
    swSelFACES = 3
    swSelSKETCHES = 4
    swSelSKETCHSEGS = 5
    swSelSKETCHPOINTS = 6
    swSelDATUMPLANES = 7
    swSelDATUMAXES = 8
    swSelDATUMPOINTS = 9
    swSelOLEITEMS = 10
    swSelATTRIBUTES = 11
    swSelSECTIONLINES = 12
    swSelDETAILCIRCLES = 13
    swSelSECTIONTEXT = 14
    swSelSHEET = 15
    swSelCOMPONENTS = 16
    swSelMATES = 17
    swSelBODYFEATURES = 18
    swSelREFCURVES = 19
    swSelREFSURFACES = 20
    swSelCENTERLINES = 21
    swSelREFEDGES = 22
    swSelREFFACES = 23


class swViewTypes_e(IntEnum):
    """Standard view types."""
    swFrontView = 1
    swBackView = 2
    swLeftView = 3
    swRightView = 4
    swTopView = 5
    swBottomView = 6
    swIsometricView = 7
    swTrimetricView = 8
    swDimetricView = 9


class swSaveAsVersion_e(IntEnum):
    """Save as version."""
    swSaveAsCurrentVersion = 0
    swSaveAsSW2004 = 1
    swSaveAsSW2007 = 2


class swFileSaveError_e(IntEnum):
    """File save errors."""
    swGenericSaveError = 0
    swReadOnlySaveError = 1
    swFileNameEmpty = 2
    swFileNameContainsAtSign = 3
    swFileSaveAsNoOverwriteNormal = 4


class swCustomInfoType_e(IntEnum):
    """Custom property types."""
    swCustomInfoUnknown = 0
    swCustomInfoText = 30
    swCustomInfoDate = 64
    swCustomInfoNumber = 3
    swCustomInfoYesOrNo = 11


class swDimensionType_e(IntEnum):
    """Dimension types."""
    swLinearDimension = 0
    swAngularDimension = 1
    swRadialDimension = 2
    swDiameterDimension = 3
    swOrdinateDimension = 4
    swChamferDimension = 5
    swHorOrdinateDimension = 6


# =============================================================================
# Interface Definitions
# =============================================================================

class ISldWorks:
    """Main SolidWorks application interface."""

    @property
    def Visible(self) -> bool: ...
    @Visible.setter
    def Visible(self, value: bool) -> None: ...

    @property
    def ActiveDoc(self) -> Optional['IModelDoc2']: ...

    @property
    def RevisionNumber(self) -> str: ...

    @property
    def FrameState(self) -> int: ...
    @FrameState.setter
    def FrameState(self, value: int) -> None: ...

    def NewDocument(
        self,
        TemplateName: str,
        PaperSize: int,
        Width: float,
        Height: float
    ) -> 'IModelDoc2': ...

    def OpenDoc6(
        self,
        FileName: str,
        Type: int,
        Options: int,
        Configuration: str,
        Errors: int,
        Warnings: int
    ) -> 'IModelDoc2': ...

    def CloseDoc(self, Name: str) -> None: ...

    def ActivateDoc3(
        self,
        Name: str,
        UseUserPreferences: bool,
        Option: int,
        Errors: int
    ) -> 'IModelDoc2': ...

    def GetDocuments(self) -> List['IModelDoc2']: ...

    def QuitDoc(self, Name: str) -> None: ...

    def SendMsgToUser2(
        self,
        Message: str,
        Icon: int,
        Buttons: int
    ) -> int: ...

    def GetUserPreferenceToggle(self, UserPreference: int) -> bool: ...
    def SetUserPreferenceToggle(self, UserPreference: int, Value: bool) -> bool: ...

    def GetUserPreferenceIntegerValue(self, UserPreference: int) -> int: ...
    def SetUserPreferenceIntegerValue(self, UserPreference: int, Value: int) -> bool: ...

    def GetUserPreferenceDoubleValue(self, UserPreference: int) -> float: ...
    def SetUserPreferenceDoubleValue(self, UserPreference: int, Value: float) -> bool: ...

    def GetUserPreferenceStringValue(self, UserPreference: int) -> str: ...
    def SetUserPreferenceStringValue(self, UserPreference: int, Value: str) -> bool: ...


class IModelDoc2:
    """Model document interface (parts, assemblies, drawings)."""

    @property
    def Extension(self) -> 'IModelDocExtension': ...

    @property
    def FeatureManager(self) -> 'IFeatureManager': ...

    @property
    def SketchManager(self) -> 'ISketchManager': ...

    @property
    def SelectionManager(self) -> 'ISelectionMgr': ...

    @property
    def ConfigurationManager(self) -> 'IConfigurationManager': ...

    def GetType(self) -> int: ...

    def GetTitle(self) -> str: ...

    def GetPathName(self) -> str: ...

    def GetSaveFlag(self) -> bool: ...

    def Save3(
        self,
        Options: int,
        Errors: int,
        Warnings: int
    ) -> bool: ...

    def SaveAs4(
        self,
        NewName: str,
        Version: int,
        Options: int,
        Errors: int,
        Warnings: int
    ) -> bool: ...

    def EditRebuild3(self) -> bool: ...

    def ForceRebuild3(self, TopOnly: bool) -> bool: ...

    def ClearSelection2(self, Value: bool) -> None: ...

    def ViewZoomtofit2(self) -> None: ...

    def ShowNamedView2(self, ViewName: str, ViewId: int) -> None: ...

    def InsertSketch2(self, UpdateEditRebuild: bool) -> None: ...

    def EditSketch(self) -> None: ...

    def SketchAddConstraints(self, Constraint: str) -> bool: ...

    def SetPickMode(self) -> None: ...

    def GetFirstFeature(self) -> Optional['IFeature']: ...

    def FeatureByName(self, Name: str) -> Optional['IFeature']: ...

    def GetActiveConfiguration(self) -> 'IConfiguration': ...

    def GetConfigurationNames(self) -> List[str]: ...

    def ShowConfiguration2(self, ConfigName: str) -> bool: ...

    def Parameter(self, Name: str) -> 'IParameter': ...

    def GetCustomInfoValue(self, Config: str, Field: str) -> str: ...

    def AddCustomInfo3(
        self,
        Config: str,
        FieldName: str,
        FieldType: int,
        FieldValue: str
    ) -> bool: ...

    def DeleteCustomInfo2(self, Config: str, FieldName: str) -> bool: ...


class IModelDocExtension:
    """Model document extension interface."""

    @property
    def CustomPropertyManager(self) -> 'ICustomPropertyManager': ...

    def SelectByID2(
        self,
        Name: str,
        Type: str,
        X: float,
        Y: float,
        Z: float,
        Append: bool,
        Mark: int,
        Callout: Any,
        SelectOption: int
    ) -> bool: ...

    def CreateMassProperty(self) -> 'IMassProperty': ...

    def SaveAs3(
        self,
        Name: str,
        Version: int,
        Options: int,
        ExportData: Any,
        AdvancedSaveAs: Any,
        Errors: int,
        Warnings: int
    ) -> bool: ...

    def GetMaterialPropertyValues2(
        self,
        MaterialDensity: float,
        Diffuse: int,
        Specular: int,
        Specularity: float,
        Ambient: int,
        Transparency: float,
        Emission: int
    ) -> bool: ...

    def SetMaterialPropertyValues2(
        self,
        MaterialDensity: float,
        Diffuse: int,
        Specular: int,
        Specularity: float,
        Ambient: int,
        Transparency: float,
        Emission: int
    ) -> bool: ...


class IFeatureManager:
    """Feature manager interface."""

    def FeatureExtrusion3(
        self,
        Sd: bool,
        Flip: bool,
        Dir: bool,
        T1: int,
        T2: int,
        D1: float,
        D2: float,
        Dchk1: bool,
        Dchk2: bool,
        Ddir1: bool,
        Ddir2: bool,
        Dang1: float,
        Dang2: float,
        OffsetReverse1: bool,
        OffsetReverse2: bool,
        TranslateSurface1: bool,
        TranslateSurface2: bool,
        OffsetDistance1: float,
        OffsetDistance2: float,
        Thinwall: bool,
        ThinwallType: int,
        Thickness1: float,
        Merge: bool,
        NormallyCut: bool,
        FlipCutDirection: bool,
        Optimize: bool
    ) -> 'IFeature': ...

    def FeatureRevolve2(
        self,
        SingleDir: bool,
        IsSolid: bool,
        IsThinwall: bool,
        IsCut: bool,
        ReverseDir: bool,
        BothDirectionUpToSameEntity: bool,
        Dir1Type: int,
        Dir2Type: int,
        Dir1Angle: float,
        Dir2Angle: float,
        OffsetReverse1: bool,
        OffsetReverse2: bool,
        OffsetDistance1: float,
        OffsetDistance2: float,
        ThinType: int,
        ThinThickness1: float,
        ThinThickness2: float,
        Merge: bool,
        FlipCutDirection: bool,
        Optimize: bool
    ) -> 'IFeature': ...

    def FeatureFillet3(
        self,
        Options: int,
        R1: float,
        Ftyp: int,
        OverflowType: int,
        Radtyp1: int,
        Radtyp2: int,
        Setbackd1: float,
        Setbackd2: float,
        PointRadiusD1: float,
        PointRadiusD2: float,
        TanProp: bool,
        Featprop: bool,
        PartialEllipse: bool,
        TrimFlag: bool,
        Trimbits: bool,
        Conic: bool,
        ConicType: float,
        AsymmetricType: bool
    ) -> 'IFeature': ...

    def FeatureChamfer(
        self,
        Options: int,
        ChamType: int,
        Width: float,
        Angle: float,
        OtherDist: float,
        VertexChamDist1: float,
        VertexChamDist2: float,
        VertexChamDist3: float
    ) -> 'IFeature': ...

    def InsertProtrusionSwept4(
        self,
        Propa: bool,
        Twist: int,
        StartAlign: int,
        EndAlign: int,
        TwistAngle: float,
        MergeBodies: bool,
        SolMod: int,
        TangToPaths: bool,
        AdvancedSmooth: bool,
        StartMatchingType: int,
        EndMatchingType: int,
        IsThin: bool,
        T1: float,
        T2: float,
        ThinType: int
    ) -> 'IFeature': ...

    def InsertProtrusionBlend2(
        self,
        Closed: bool,
        KeepTangent: bool,
        Thin: bool,
        ThinForward: float,
        ThinReverse: float,
        ThinType: int,
        StartMatchingType: int,
        EndMatchingType: int,
        Merge: bool
    ) -> 'IFeature': ...

    def FeatureLinearPattern4(
        self,
        Num1: int,
        Space1: float,
        Num2: int,
        Space2: float,
        BoolFlipDir1: bool,
        BoolFlipDir2: bool,
        Dir1Name: str,
        Dir2Name: str,
        D1GeomPattern: bool,
        D2GeomPattern: bool,
        D1VarySketch: bool,
        D2VarySketch: bool,
        D1Instance: List[int],
        D2Instance: List[int],
        AutoSelect: bool,
        SeedPosition: int
    ) -> 'IFeature': ...

    def FeatureCut4(
        self,
        Sd: bool,
        Flip: bool,
        Dir: bool,
        T1: int,
        T2: int,
        D1: float,
        D2: float,
        Dchk1: bool,
        Dchk2: bool,
        Ddir1: bool,
        Ddir2: bool,
        Dang1: float,
        Dang2: float,
        OffsetReverse1: bool,
        OffsetReverse2: bool,
        TranslateSurface1: bool,
        TranslateSurface2: bool,
        NormallyCut: bool,
        Optimize: bool,
        FlipCutDirection: bool,
        MultiBodyFeature: bool
    ) -> 'IFeature': ...

    def InsertStructuralWeldment5(
        self,
        ProfileDir: str,
        ProfileName: str,
        ProfileSize: str,
        ContactClearance: float,
        bMerge: bool,
        bWeldGroups: bool,
        bWeldMateSetback: bool,
        WeldMateOffset: float,
        CornerType: int,
        MiterGapType: int,
        MiterGap: float,
        CornerProfile: str
    ) -> 'IFeature': ...


class ISketchManager:
    """Sketch manager interface."""

    def CreateLine(
        self,
        X1: float,
        Y1: float,
        Z1: float,
        X2: float,
        Y2: float,
        Z2: float
    ) -> 'ISketchSegment': ...

    def CreateCircle(
        self,
        Xc: float,
        Yc: float,
        Zc: float,
        Xp: float,
        Yp: float,
        Zp: float
    ) -> 'ISketchSegment': ...

    def CreateCircleByRadius(
        self,
        Xc: float,
        Yc: float,
        Zc: float,
        Radius: float
    ) -> 'ISketchSegment': ...

    def CreateCornerRectangle(
        self,
        X1: float,
        Y1: float,
        Z1: float,
        X2: float,
        Y2: float,
        Z2: float
    ) -> List['ISketchSegment']: ...

    def CreateCenterRectangle(
        self,
        Xc: float,
        Yc: float,
        Zc: float,
        Xp: float,
        Yp: float,
        Zp: float
    ) -> List['ISketchSegment']: ...

    def Create3PointArc(
        self,
        X1: float,
        Y1: float,
        Z1: float,
        X2: float,
        Y2: float,
        Z2: float,
        X3: float,
        Y3: float,
        Z3: float
    ) -> 'ISketchSegment': ...

    def CreateEllipse(
        self,
        Xc: float,
        Yc: float,
        Zc: float,
        Xa: float,
        Ya: float,
        Za: float,
        Xb: float,
        Yb: float,
        Zb: float
    ) -> 'ISketchSegment': ...

    def CreatePolygon(
        self,
        Xc: float,
        Yc: float,
        Zc: float,
        Xp: float,
        Yp: float,
        Zp: float,
        NumSides: int,
        Inscribed: bool
    ) -> List['ISketchSegment']: ...

    def CreateSpline2(
        self,
        Points: List[float],
        SimulateNatural: bool
    ) -> 'ISketchSegment': ...

    def InsertSketch(self, UpdateEditRebuild: bool) -> None: ...

    def ActiveSketch(self) -> Optional['ISketch']: ...

    def AddToDB(self, Add: bool) -> None: ...


class ISelectionMgr:
    """Selection manager interface."""

    def GetSelectedObjectCount2(self, Mark: int) -> int: ...

    def GetSelectedObject6(self, Index: int, Mark: int) -> Any: ...

    def GetSelectedObjectType3(self, Index: int, Mark: int) -> int: ...

    def GetSelectionPoint2(self, Index: int, Mark: int) -> Tuple[float, float, float]: ...

    def SetSelectedObjectMark(
        self,
        Index: int,
        Mark: int,
        SelectOption: int
    ) -> bool: ...

    def DeSelect2(self, Index: int, Mark: int) -> bool: ...

    def EnableContourSelection(self, Enable: bool) -> None: ...


class ICustomPropertyManager:
    """Custom property manager interface."""

    def GetNames(self) -> List[str]: ...

    def Get5(
        self,
        FieldName: str,
        UseCached: bool,
        ValOut: str,
        ResolvedValOut: str,
        WasResolved: bool
    ) -> int: ...

    def Set2(self, FieldName: str, FieldValue: str) -> int: ...

    def Add3(
        self,
        FieldName: str,
        FieldType: int,
        FieldValue: str,
        OverwriteExisting: int
    ) -> int: ...

    def Delete2(self, FieldName: str) -> int: ...

    def GetType2(self, FieldName: str) -> int: ...

    def Count(self) -> int: ...


class IMassProperty:
    """Mass property interface."""

    @property
    def Mass(self) -> float: ...

    @property
    def Volume(self) -> float: ...

    @property
    def SurfaceArea(self) -> float: ...

    @property
    def CenterOfMass(self) -> Tuple[float, float, float]: ...

    @property
    def PrincipalAxesOfInertia(self) -> Tuple[Tuple[float, ...], ...]: ...

    @property
    def PrincipalMomentsOfInertia(self) -> Tuple[float, float, float]: ...

    @property
    def MomentsOfInertia(self) -> Tuple[float, ...]: ...

    @property
    def Density(self) -> float: ...


class IFeature:
    """Feature interface."""

    @property
    def Name(self) -> str: ...
    @Name.setter
    def Name(self, value: str) -> None: ...

    def GetTypeName2(self) -> str: ...

    def GetNextFeature(self) -> Optional['IFeature']: ...

    def IsSuppressed(self) -> bool: ...

    def SetSuppression2(
        self,
        SuppressState: int,
        Config: int,
        ConfigNames: List[str]
    ) -> bool: ...

    def GetFirstSubFeature(self) -> Optional['IFeature']: ...

    def GetNextSubFeature(self) -> Optional['IFeature']: ...

    def GetFaces(self) -> List['IFace2']: ...

    def GetBody(self) -> 'IBody2': ...

    def Select2(self, Append: bool, Mark: int) -> bool: ...


class IConfiguration:
    """Configuration interface."""

    @property
    def Name(self) -> str: ...

    @property
    def CustomPropertyManager(self) -> 'ICustomPropertyManager': ...

    def GetParameters(self) -> List['IParameter']: ...


class IConfigurationManager:
    """Configuration manager interface."""

    @property
    def ActiveConfiguration(self) -> 'IConfiguration': ...

    def GetConfigurationNames(self) -> List[str]: ...

    def AddConfiguration2(
        self,
        Name: str,
        Comment: str,
        AltName: str,
        Options: int,
        ParentConfig: str,
        Description: str,
        AdvancedOptions: int
    ) -> 'IConfiguration': ...

    def DeleteConfiguration2(self, Name: str) -> bool: ...


class ISketchSegment:
    """Sketch segment interface."""

    @property
    def ConstructionGeometry(self) -> bool: ...
    @ConstructionGeometry.setter
    def ConstructionGeometry(self, value: bool) -> None: ...

    def GetLength(self) -> float: ...

    def IGetStartPoint2(self) -> Tuple[float, float, float]: ...

    def IGetEndPoint2(self) -> Tuple[float, float, float]: ...

    def Select4(
        self,
        Append: bool,
        SelectionData: Any
    ) -> bool: ...


class ISketch:
    """Sketch interface."""

    def GetSketchPoints2(self) -> List['ISketchPoint']: ...

    def GetSketchSegments(self) -> List['ISketchSegment']: ...

    def GetSketchRelations(self) -> List['ISketchRelation']: ...

    def GetConstraintCount(self) -> int: ...


class ISketchPoint:
    """Sketch point interface."""

    @property
    def X(self) -> float: ...

    @property
    def Y(self) -> float: ...

    @property
    def Z(self) -> float: ...


class ISketchRelation:
    """Sketch relation interface."""

    def GetRelationType(self) -> int: ...

    def GetEntitiesCount(self) -> int: ...


class IFace2:
    """Face interface."""

    def GetArea(self) -> float: ...

    def GetEdges(self) -> List['IEdge']: ...

    def GetSurface(self) -> 'ISurface': ...

    def IsSafe(self) -> bool: ...


class IEdge:
    """Edge interface."""

    def GetCurve(self) -> 'ICurve': ...

    def GetStartVertex(self) -> 'IVertex': ...

    def GetEndVertex(self) -> 'IVertex': ...

    def GetTwoAdjacentFaces2(self) -> Tuple['IFace2', 'IFace2']: ...


class IVertex:
    """Vertex interface."""

    def GetPoint(self) -> Tuple[float, float, float]: ...


class IBody2:
    """Body interface."""

    def GetType(self) -> int: ...

    def GetFaces(self) -> List['IFace2']: ...

    def GetEdges(self) -> List['IEdge']: ...

    def GetVertices(self) -> List['IVertex']: ...

    def GetMassProperties(
        self,
        Density: float
    ) -> Tuple[float, ...]: ...


class ISurface:
    """Surface interface."""

    def IsSphere(self) -> bool: ...
    def IsCylinder(self) -> bool: ...
    def IsPlane(self) -> bool: ...
    def IsCone(self) -> bool: ...
    def IsTorus(self) -> bool: ...


class ICurve:
    """Curve interface."""

    def IsLine(self) -> bool: ...
    def IsCircle(self) -> bool: ...
    def IsEllipse(self) -> bool: ...


class IParameter:
    """Parameter/dimension interface."""

    @property
    def Value(self) -> float: ...
    @Value.setter
    def Value(self, value: float) -> None: ...

    @property
    def SystemValue(self) -> float: ...
    @SystemValue.setter
    def SystemValue(self, value: float) -> None: ...

    @property
    def FullName(self) -> str: ...


# =============================================================================
# Assembly-Specific Interfaces
# =============================================================================

class IAssemblyDoc(IModelDoc2):
    """Assembly document interface."""

    def GetComponentCount(self, TopOnly: bool) -> int: ...

    def GetComponents(self, TopOnly: bool) -> List['IComponent2']: ...

    def AddComponent5(
        self,
        PathName: str,
        Config: int,
        ConfigName: str,
        UseConfigTemplate: bool,
        ConfigTemplateName: str,
        X: float,
        Y: float,
        Z: float
    ) -> 'IComponent2': ...

    def AddMate5(
        self,
        MateTypeFromEnum: int,
        AlignFromEnum: int,
        Flip: bool,
        Distance: float,
        DistanceAbsUpperLimit: float,
        DistanceAbsLowerLimit: float,
        GearRatioNumerator: float,
        GearRatioDenominator: float,
        Angle: float,
        AngleAbsUpperLimit: float,
        AngleAbsLowerLimit: float,
        ForPositioningOnly: bool,
        LockRotation: bool,
        WidthMateOption: int,
        ErrorStatus: int
    ) -> 'IMate2': ...

    def EditAssembly(self) -> None: ...

    def EditPart(self) -> None: ...


class IComponent2:
    """Assembly component interface."""

    @property
    def Name2(self) -> str: ...

    @property
    def Visible(self) -> int: ...
    @Visible.setter
    def Visible(self, value: int) -> None: ...

    @property
    def ReferencedConfiguration(self) -> str: ...
    @ReferencedConfiguration.setter
    def ReferencedConfiguration(self, value: str) -> None: ...

    def GetModelDoc2(self) -> Optional['IModelDoc2']: ...

    def GetPathName(self) -> str: ...

    def Transform2(self) -> 'IMathTransform': ...

    def IsSuppressed(self) -> bool: ...

    def SetSuppression2(self, SuppressState: int) -> bool: ...

    def GetChildren(self) -> List['IComponent2']: ...

    def GetParent(self) -> Optional['IComponent2']: ...

    def Select4(
        self,
        Append: bool,
        SelectionData: Any,
        SuspendGraphicsUpdate: bool
    ) -> bool: ...

    def FeatureByName(self, Name: str) -> Optional['IFeature']: ...


class IMate2:
    """Mate interface."""

    @property
    def Type(self) -> int: ...

    @property
    def Alignment(self) -> int: ...

    def GetMateEntityCount(self) -> int: ...

    def MateEntity(self, Index: int) -> 'IMateEntity2': ...

    def GetSuppression(self) -> int: ...

    def SetSuppression(self, SuppressState: int) -> bool: ...


class IMateEntity2:
    """Mate entity interface."""

    def ReferenceComponent(self) -> 'IComponent2': ...

    def Reference(self) -> Any: ...


class IMathTransform:
    """Math transform interface."""

    @property
    def ArrayData(self) -> Tuple[float, ...]: ...

    def Inverse(self) -> 'IMathTransform': ...

    def Multiply(self, Other: 'IMathTransform') -> 'IMathTransform': ...


# =============================================================================
# Drawing-Specific Interfaces
# =============================================================================

class IDrawingDoc(IModelDoc2):
    """Drawing document interface."""

    def GetCurrentSheet(self) -> 'ISheet': ...

    def GetSheetNames(self) -> List[str]: ...

    def ActivateSheet(self, Name: str) -> bool: ...

    def CreateDrawViewFromModelView3(
        self,
        ModelName: str,
        ViewName: str,
        X: float,
        Y: float,
        Z: float
    ) -> 'IView': ...

    def NewSheet4(
        self,
        Name: str,
        PaperSize: int,
        TemplateIn: int,
        Scale1: float,
        Scale2: float,
        FirstAngle: bool,
        CustomTemplate: str,
        Width: float,
        Height: float,
        PropertyViewName: str,
        Zone: int
    ) -> bool: ...

    def InsertTableAnnotation2(
        self,
        UseAnchor: bool,
        X: float,
        Y: float,
        AnchorType: int,
        TableType: int,
        Template: str,
        RowCount: int,
        ColCount: int
    ) -> 'ITableAnnotation': ...


class ISheet:
    """Drawing sheet interface."""

    @property
    def Name(self) -> str: ...

    def GetViews(self) -> List['IView']: ...

    def GetProperties2(self) -> Tuple[float, ...]: ...

    def SetProperties2(
        self,
        PaperSize: int,
        TemplateIn: int,
        Scale1: float,
        Scale2: float,
        FirstAngle: bool,
        Width: float,
        Height: float,
        PropertyViewName: str
    ) -> bool: ...


class IView:
    """Drawing view interface."""

    @property
    def Name(self) -> str: ...

    @property
    def Type(self) -> int: ...

    @property
    def Scale2(self) -> Tuple[float, float]: ...
    @Scale2.setter
    def Scale2(self, value: Tuple[float, float]) -> None: ...

    def GetXPosition(self) -> float: ...
    def SetXPosition(self, X: float) -> None: ...

    def GetYPosition(self) -> float: ...
    def SetYPosition(self, Y: float) -> None: ...

    def GetVisibleEntities(
        self,
        Component: 'IComponent2',
        EntityType: int
    ) -> List[Any]: ...


class ITableAnnotation:
    """Table annotation interface."""

    @property
    def RowCount(self) -> int: ...

    @property
    def ColumnCount(self) -> int: ...

    @property
    def Text(self) -> str: ...

    def GetText(self, Row: int, Col: int) -> str: ...

    def SetText(self, Row: int, Col: int, Text: str) -> None: ...

    def InsertRow(self, Row: int, WhereToAdd: int) -> bool: ...

    def DeleteRow(self, Row: int) -> bool: ...

    def InsertColumn(self, Col: int, WhereToAdd: int, Width: float) -> bool: ...

    def DeleteColumn(self, Col: int) -> bool: ...


# =============================================================================
# Simulation Interfaces (Cosmos/SolidWorks Simulation)
# =============================================================================

class ICWAddinCallBack:
    """Cosmos Simulation callback interface."""

    def OnWorkDone(self, StudyName: str, Result: int) -> None: ...


class ISimulationStudyManager:
    """Simulation study manager."""

    def GetStudyCount(self) -> int: ...

    def GetStudyNames(self) -> List[str]: ...

    def GetActiveStudy(self) -> Optional['ISimulationStudy']: ...

    def CreateNewStudy(self, Name: str, StudyType: int) -> 'ISimulationStudy': ...


class ISimulationStudy:
    """Simulation study interface."""

    @property
    def Name(self) -> str: ...

    @property
    def StudyType(self) -> int: ...

    def AddStaticLoading(self, Value: float, UnitType: int) -> bool: ...

    def AddFixture(self, FixtureType: int) -> bool: ...

    def SetMaterial(self, MaterialName: str) -> bool: ...

    def Mesh(self, MeshSize: float) -> bool: ...

    def Run(self) -> int: ...

    def GetResultsCount(self) -> int: ...

    def GetMinStress(self) -> float: ...

    def GetMaxStress(self) -> float: ...

    def GetMaxDisplacement(self) -> float: ...

    def GetSafetyFactor(self) -> float: ...


# =============================================================================
# PDM Integration Interfaces
# =============================================================================

class IEdmVault5:
    """SOLIDWORKS PDM Vault interface."""

    def Login(
        self,
        User: str,
        Password: str,
        VaultName: str
    ) -> bool: ...

    def Logout(self) -> None: ...

    @property
    def Name(self) -> str: ...

    @property
    def RootFolderPath(self) -> str: ...

    def GetFileFromPath(self, Path: str) -> 'IEdmFile5': ...

    def GetFolderFromPath(self, Path: str) -> 'IEdmFolder5': ...

    def BrowseForFolder(
        self,
        ParentWindow: int,
        Title: str
    ) -> 'IEdmFolder5': ...


class IEdmFile5:
    """PDM file interface."""

    @property
    def Name(self) -> str: ...

    @property
    def ID(self) -> int: ...

    def GetFilePath(self, FolderID: int) -> str: ...

    def GetLocalPath(self, FolderID: int) -> str: ...

    def LockFile(
        self,
        FolderID: int,
        WindowHandle: int,
        Flags: int
    ) -> None: ...

    def UnlockFile(
        self,
        FolderID: int,
        Comment: str,
        Flags: int
    ) -> None: ...

    def GetNextVersion(
        self,
        FolderID: int
    ) -> 'IEdmVersion': ...

    def GetCurrentVersion(self) -> 'IEdmVersion': ...


class IEdmFolder5:
    """PDM folder interface."""

    @property
    def Name(self) -> str: ...

    @property
    def ID(self) -> int: ...

    @property
    def LocalPath(self) -> str: ...

    def GetFirstFile(self, Filter: str) -> 'IEdmPos5': ...

    def GetNextFile(self, Pos: 'IEdmPos5') -> 'IEdmFile5': ...

    def GetFirstSubFolder(self) -> 'IEdmPos5': ...

    def GetNextSubFolder(self, Pos: 'IEdmPos5') -> 'IEdmFolder5': ...

    def AddFile(
        self,
        WindowHandle: int,
        SourcePath: str,
        Flags: int
    ) -> 'IEdmFile5': ...


class IEdmPos5:
    """PDM position interface for enumeration."""

    def IsNull(self) -> bool: ...


class IEdmVersion:
    """PDM version interface."""

    @property
    def VersionNo(self) -> int: ...

    @property
    def Comment(self) -> str: ...

    @property
    def CreateDate(self) -> str: ...

    @property
    def CreateUser(self) -> str: ...
