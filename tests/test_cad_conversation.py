"""
Multi-Turn Conversation & User Experience Test
Tests bot's ability to handle conversations, context retention, unclear requests, typos
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

project_root = Path(__file__).parent.parent
nlp_parser = load_module("cad_nlp_parser", project_root / "core" / "cad_nlp_parser.py")
prompt_lib = load_module("prompt_library", project_root / "core" / "prompt_library.py")

CADNLPParser = nlp_parser.CADNLPParser
PromptLibrary = prompt_lib.PromptLibrary


class ConversationSimulator:
    """Simulates multi-turn conversations."""
    
    def __init__(self):
        self.parser = CADNLPParser("solidworks")
        self.prompt_library = PromptLibrary()
        self.conversation_context = {
            "last_dimensions": {},
            "last_material": None,
            "last_standard": None,
            "current_part": None,
            "operations_done": []
        }
    
    def process_turn(self, user_input: str) -> Dict[str, Any]:
        """Process a conversation turn with context."""
        result = {
            "input": user_input,
            "parsed_new": {},
            "parsed_from_context": {},
            "understanding_score": 0.0,
            "needs_clarification": False,
            "suggestions": [],
            "success": True
        }
        
        # Parse current input
        params = self.parser.parse(user_input)
        material = self.parser.extract_material(user_input)
        standard = self.parser.extract_standard(user_input)
        
        result["parsed_new"] = {
            "dimensions": len(params),
            "material": material,
            "standard": standard
        }
        
        # Check for context references
        context_keywords = ["same", "that", "it", "this", "previous", "last"]
        uses_context = any(kw in user_input.lower() for kw in context_keywords)
        
        if uses_context:
            result["parsed_from_context"] = {
                "dimensions": len(self.conversation_context["last_dimensions"]),
                "material": self.conversation_context["last_material"],
                "standard": self.conversation_context["last_standard"]
            }
        
        # Update context
        if params:
            self.conversation_context["last_dimensions"] = params
        if material:
            self.conversation_context["last_material"] = material
        if standard:
            self.conversation_context["last_standard"] = standard
        
        # Calculate understanding score
        understanding = 100.0
        
        if not params and not material and not standard and not uses_context:
            understanding -= 50  # Very vague
            result["needs_clarification"] = True
            result["suggestions"] = [
                "Please specify dimensions (e.g., '6 inch diameter')",
                "What material should I use?",
                "Are there any applicable standards?"
            ]
        elif not params and uses_context and not self.conversation_context["last_dimensions"]:
            understanding -= 30  # References context that doesn't exist
            result["needs_clarification"] = True
            result["suggestions"] = ["No previous dimensions to reference"]
        
        # Detect vague language
        vague_words = ["bigger", "smaller", "longer", "shorter", "thicker", "thinner"]
        if any(word in user_input.lower() for word in vague_words):
            understanding -= 20
            result["needs_clarification"] = True
            result["suggestions"].append("Please specify exact dimensions instead of relative terms")
        
        result["understanding_score"] = max(0, understanding)
        
        return result


def run_conversation_tests():
    """Run multi-turn conversation tests."""
    
    print("\n" + "="*80)
    print("💬 MULTI-TURN CONVERSATION & UX TEST")
    print("="*80 + "\n")
    
    # Test scenarios - realistic conversations
    conversations = [
        {
            "name": "Progressive Build",
            "turns": [
                "Create a new part",
                "Make it 6 inches in diameter",
                "Extrude it 2 inches",
                "Use 316 stainless steel",
                "Add 8 bolt holes on a 5 inch bolt circle"
            ]
        },
        {
            "name": "Context Reference",
            "turns": [
                "Build a 6 inch flange, A105 material",
                "Make the same thing but in 316SS",
                "Actually, use the same material as before",
                "Add bolt holes to it"
            ]
        },
        {
            "name": "Unclear to Clear",
            "turns": [
                "Make something",
                "A flange",
                "6 inch diameter",
                "Quarter inch thick",
                "ASME B16.5 standard"
            ]
        },
        {
            "name": "Typos & Variations",
            "turns": [
                "Crete a flang 6 inch",  # Typo
                "mak it thikcer",  # Multiple typos
                "316 stainles steel",  # Common typo
                "ASMe b16.5",  # Case variation
            ]
        },
        {
            "name": "Mixed Units",
            "turns": [
                "Build a bracket 200mm long",
                "Make it 6 inches wide",
                "Add holes every 2 inches",
                "Use 3mm thick material"
            ]
        },
        {
            "name": "Ambiguous to Specific",
            "turns": [
                "I need a pipe",
                "2 inch",
                "Schedule 40",
                "8 inches long",
                "Carbon steel per B31.3"
            ]
        }
    ]
    
    total_conversations = len(conversations)
    total_turns = sum(len(c["turns"]) for c in conversations)
    successful_understanding = 0
    needed_clarification = 0
    
    for conv in conversations:
        print(f"\n{'='*80}")
        print(f"🗨️  Conversation: {conv['name']}")
        print(f"{'='*80}\n")
        
        simulator = ConversationSimulator()
        
        for i, turn in enumerate(conv["turns"], 1):
            print(f"Turn {i}/{len(conv['turns'])}")
            print(f"User: \"{turn}\"")
            
            result = simulator.process_turn(turn)
            
            # Display understanding
            score_emoji = "✅" if result["understanding_score"] >= 80 else "🟡" if result["understanding_score"] >= 50 else "🔴"
            print(f"{score_emoji} Understanding: {result['understanding_score']:.0f}%")
            
            # Display parsed data
            if result["parsed_new"]["dimensions"] > 0:
                print(f"  📏 New dimensions: {result['parsed_new']['dimensions']}")
            if result["parsed_new"]["material"]:
                print(f"  🔩 Material: {result['parsed_new']['material']}")
            if result["parsed_new"]["standard"]:
                print(f"  📋 Standard: {result['parsed_new']['standard']}")
            
            # Display context usage
            if result.get("parsed_from_context") and result["parsed_from_context"].get("dimensions", 0) > 0:
                print(f"  🔄 Using context: {result['parsed_from_context']['dimensions']} dimensions from previous")
            
            # Display clarifications
            if result["needs_clarification"]:
                print(f"  ⚠️ Needs clarification:")
                for suggestion in result["suggestions"]:
                    print(f"     - {suggestion}")
                needed_clarification += 1
            else:
                successful_understanding += 1
            
            print()
    
    # Summary
    print("="*80)
    print("📊 CONVERSATION TEST SUMMARY")
    print("="*80)
    print(f"Total Conversations: {total_conversations}")
    print(f"Total Turns: {total_turns}")
    print(f"Successful Understanding: {successful_understanding}/{total_turns} ({successful_understanding/total_turns*100:.1f}%)")
    print(f"Needed Clarification: {needed_clarification}/{total_turns} ({needed_clarification/total_turns*100:.1f}%)")
    
    return True


def run_ux_tests():
    """Test user experience scenarios."""
    
    print("\n" + "="*80)
    print("🎯 USER EXPERIENCE TEST - Real-World Scenarios")
    print("="*80 + "\n")
    
    parser = CADNLPParser("solidworks")
    
    # Test scenarios with common user mistakes/patterns
    ux_scenarios = [
        {
            "category": "Common Typos",
            "tests": [
                "Crete a flange",  # Create
                "6 inche diameter",  # inches
                "qaurter inch thick",  # quarter
                "316 stainles steel",  # stainless
                "ASMe b16.5",  # ASME
                "exturde 2 inches",  # extrude
            ]
        },
        {
            "category": "Natural Language Variations",
            "tests": [
                "I need a 6 inch flange please",
                "Can you make me a flange that's 6 inches?",
                "Build me a flange, make it 6 inch diameter",
                "Create flange - 6\"",
                "flange 6in",
            ]
        },
        {
            "category": "Incomplete Requests",
            "tests": [
                "6 inch",
                "flange",
                "make it bigger",
                "add holes",
                "use steel",
            ]
        },
        {
            "category": "Overly Detailed",
            "tests": [
                "I need to create a really nice looking flange that should be approximately 6 inches in diameter give or take, and I want it to be made from high quality stainless steel, preferably 316 grade if possible",
                "Build me a flange - the diameter needs to be exactly 6.00 inches (no more, no less), thickness should be 0.25 inches, material must be ASTM A105 forged carbon steel, and it needs to comply with ASME B16.5 class 150 specifications",
            ]
        },
        {
            "category": "Casual Language",
            "tests": [
                "yo make a 6 inch flange",
                "gonna need a flange bout 6 inches",
                "lemme get a flange real quick",
                "flange pls 6in thx",
            ]
        },
        {
            "category": "Multiple Questions",
            "tests": [
                "Should I use A105 or 316SS? Make it 6 inches",
                "What size bolt holes? 3/4 or 7/8? Make 8 of them",
                "Is 150# or 300# better for this? Use B16.5",
            ]
        }
    ]
    
    total_tests = 0
    parsed_successfully = 0
    
    for scenario in ux_scenarios:
        print(f"\n{'─'*80}")
        print(f"Category: {scenario['category']}")
        print(f"{'─'*80}\n")
        
        for test_input in scenario["tests"]:
            total_tests += 1
            print(f"Input: \"{test_input}\"")
            
            # Parse
            params = parser.parse(test_input)
            material = parser.extract_material(test_input)
            standard = parser.extract_standard(test_input)
            
            # Check if we got anything useful
            got_something = len(params) > 0 or material or standard
            
            if got_something:
                parsed_successfully += 1
                print(f"  ✅ Parsed successfully")
                if params:
                    print(f"     Dimensions: {len(params)}")
                if material:
                    print(f"     Material: {material}")
                if standard:
                    print(f"     Standard: {standard}")
            else:
                print(f"  ⚠️ No data extracted - needs clarification")
            
            print()
    
    # Summary
    print("="*80)
    print("📊 UX TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Successfully Parsed: {parsed_successfully}/{total_tests} ({parsed_successfully/total_tests*100:.1f}%)")
    print(f"Robustness Score: {parsed_successfully/total_tests*100:.0f}%")
    
    if parsed_successfully / total_tests >= 0.8:
        print("\n✅ EXCELLENT - Bot handles real-world user input very well")
    elif parsed_successfully / total_tests >= 0.6:
        print("\n🟡 GOOD - Bot handles most user input, some improvement needed")
    else:
        print("\n🔴 NEEDS IMPROVEMENT - Bot struggles with variations")
    
    return True


def run_all_conversation_tests():
    """Run all conversation and UX tests."""
    
    print("\n" + "🤖"*40)
    print("COMPREHENSIVE CONVERSATION & USER EXPERIENCE TESTING")
    print("🤖"*40)
    
    # Run conversation tests
    run_conversation_tests()
    
    # Run UX tests  
    run_ux_tests()
    
    print("\n" + "="*80)
    print("✅ ALL CONVERSATION TESTS COMPLETE")
    print("="*80)
    
    return True


if __name__ == "__main__":
    success = run_all_conversation_tests()
    sys.exit(0 if success else 1)
