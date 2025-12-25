import pytest
from agents.cad_agent.validators.drawing_analyzer import DrawingAnalyzer
import os

@pytest.fixture
def analyzer():
    return DrawingAnalyzer()

def test_analyze_dxf(analyzer, tmp_path):
    # Create a dummy DXF file
    dxf_content = """0
SECTION
2
HEADER
9
$ACADVER
1
AC1009
0
ENDSEC
0
SECTION
2
ENTITIES
0
CIRCLE
10
10.0
20
0.0
30
0.0
40
5.0
0
LINE
10
0.0
20
0.0
30
0.0
11
20.0
21
0.0
22
0.0
0
TEXT
10
0.0
20
30.0
30
0.0
40
2.5
1
Test
0
ENDSEC
0
EOF
    """
    dxf_file = tmp_path / "sample.dxf"
    dxf_file.write_text(dxf_content)

    analysis = analyzer.analyze_dxf(str(dxf_file))

    assert analysis.file_type == "dxf"
    assert len(analysis.dimensions) == 0 # No dimension entities in this simple file
    assert len(analysis.materials) == 1 # materials is used for holes
    assert analysis.materials[0]["type"] == "circle"
    assert analysis.materials[0]["diameter"] == 10
    assert len(analysis.weld_callouts) == 1 # weld_callouts is used for lines/arcs
    assert analysis.weld_callouts[0]["type"] == "line"
    assert analysis.weld_callouts[0]["length"] == 20
    assert "Test" in analysis.extracted_text
