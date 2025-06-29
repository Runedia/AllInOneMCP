"""
Enhanced Tool Guide Handler - AI-friendly clean version without icons
Optimized for Windows console compatibility and AI readability
"""

from typing import Dict, Any
from tools.recommendations.tool_advisor import tool_advisor, get_performance_comparison


async def handle_tool_guide(arguments: Dict[str, Any]) -> str:
    """Comprehensive tool guidance with performance metrics - AI optimized"""
    operation_type = arguments.get("operation_type", "general")
    show_full_guide = arguments.get("show_full_guide", False)
    show_performance = arguments.get("show_performance", False)
    
    # Clean header message without icons
    header_msg = "[SMART TOOL RECOMMENDATIONS] Use this guide before complex operations for maximum efficiency!\\n\\n"
    
    if show_full_guide or operation_type == "general":
        # Full comprehensive guide
        base_guide = tool_advisor.get_tool_guide()
        footer = "\\n\\n[TIP] For specific recommendations, use tool_guide with operation_type parameter!\\n"
        footer += "[PERFORMANCE TIP] Add show_performance=true for detailed efficiency metrics!"
        return header_msg + base_guide + footer
    
    # Performance comparison for specific categories
    if show_performance and operation_type in ["text_replacement", "line_editing", "file_reading", "file_operations", "directory_operations"]:
        return header_msg + get_performance_comparison(operation_type)
    
    # Specific operation recommendations with performance insights
    if operation_type == "text_replace":
        return header_msg + """[TEXT REPLACEMENT TOOLS]

[BEST] regex_replace - Use for patterns, multiple variants, or complex replacements
   - Example: \\\\d+ to replace all numbers
   - Supports capture groups: (\\\\w+)\\\\s+(\\\\w+) → $2 $1
   - Performance: Highly optimized for pattern matching
   - Token efficiency: Handles multiple patterns in one pass


[RECOMMENDATION] Use regex_replace unless you need exact literal matching.

[PERFORMANCE TIP] For multiple similar replacements, regex_replace can be 10x faster!

[TOKEN EFFICIENCY] regex_replace saves tokens by combining multiple operations into one."""

    elif operation_type == "line_edit":
        return header_msg + """[LINE EDITING TOOLS]

[BEST] patch_apply - Use for 3+ operations or complex edits
   - Atomic operations (all succeed or all fail)
   - No line number conflicts
   - Most efficient for multiple changes
   - Performance: 5-20x faster than sequential operations
   - Token efficiency: Maximum efficiency - single atomic operation

[ADVANCED] replace_line_range - Use for multi-line changes
   - Better than multiple insert_line calls
   - Good for replacing 2-20 lines
   - Performance: 3-5x faster than multiple insert_line operations

[BASIC] insert_line - Use only for single line insertion
   - Simple but inefficient for multiple operations
   - Performance: Efficient for single operations, inefficient when repeated

[RECOMMENDATION] Always prefer patch_apply for multiple edits.

[PRO TIP] patch_apply prevents line number conflicts that often break sequential edits!

[EFFICIENCY RULE] 1 operation = insert_line, 2-5 operations = consider patch_apply, 6+ operations = always patch_apply"""

    elif operation_type == "file_read":
        return header_msg + """[FILE READING TOOLS]

[BEST] get_file_section - Use for specific parts or large files
   - Token efficient - only reads what you need
   - Perfect for code review or targeted analysis
   - Supports context lines around target area
   - Performance: 10-100x faster for large files, minimal memory usage
   - Token efficiency: Saves 70-90% tokens compared to read_file on large files

[BASIC] read_file - Use only when you need the entire file
   - Memory and token intensive
   - Required for full file analysis
   - Performance: Can be memory intensive for large files

[RECOMMENDATION] Always use get_file_section unless you truly need the entire file.

[TOKEN SAVER] Reading specific sections can save 70-90% of tokens on large files!

[SIZE THRESHOLD] Files >50KB should almost always use get_file_section"""

    elif operation_type == "file_operations":
        return header_msg + """[FILE OPERATIONS TOOLS]

[ESSENTIAL] backup_file - Use before any risky operations
   - Timestamped backups for safety
   - Performance: Essential safety practice, minimal overhead
   - Token efficiency: Extremely efficient - OS-level copy

[ADVANCED] copy_file - Use for file duplication
   - OS-optimized copying, preserves metadata
   - Performance: 5-10x faster than read+write combination
   - Token efficiency: Extremely efficient - no content reading

[ADVANCED] move_file - Use for relocation/renaming
   - Single atomic operation
   - Performance: Near-instantaneous on same filesystem

[ADVANCED] append_to_file - Use for adding content to end
   - Memory efficient, no file reading needed
   - Performance: Much faster than read+modify+write

[BASIC] write_file - Use for complete file creation/replacement
   - Simple operation, complete control

[SAFETY RULE] Always backup_file before risky operations!

[PERFORMANCE TIP] copy_file is 5-10x faster than manual read+write!"""

    elif operation_type == "directory_operations":
        return header_msg + """[DIRECTORY ANALYSIS TOOLS]

[BEST] analyze_project - Use for large directory analysis
   - Comprehensive overview, file type breakdown
   - Performance: Optimized for large projects, much faster than manual analysis
   - Token efficiency: Extremely compact overview replacing hundreds of operations

[ADVANCED] count_files - Use for file statistics
   - Summary format, extension filtering
   - Performance: Much faster than manual counting via list_directory

[ADVANCED] get_recent_files - Use for finding latest changes
   - Sorted by modification time, configurable limit
   - Performance: Very fast with small result sets

[BASIC] list_directory - Use for simple browsing
   - Simple output, fast for small directories
   - Performance: Can be slow for large directories

[RECOMMENDATION] Use analyze_project for any directory >100 files

[EFFICIENCY TIP] analyze_project gives better overview than dozens of list_directory calls!"""

    elif operation_type == "code_format":
        return header_msg + """[CODE FORMATTING TOOLS]

[BEST] smart_indent - Use for indentation changes
   - Automatic detection, consistent results
   - Tab/space intelligent
   - Performance: Can fix 50+ lines instantly
   - Token efficiency: Much faster than manual line-by-line editing

[ADVANCED] replace_line_range - Use for complex formatting that needs custom logic
   - More flexible but requires manual work

[RECOMMENDATION] Always try smart_indent first for indentation issues.

[TIME SAVER] smart_indent can fix 50+ lines in seconds!

[USE CASE] If it's just indentation, smart_indent. If it's complex formatting, use replace_line_range or patch_apply."""

    elif operation_type == "performance":
        return header_msg + """[PERFORMANCE OPTIMIZATION GUIDE]

[HIGH-IMPACT OPTIMIZATIONS]
- Use get_file_section instead of read_file → 70-90% token savings
- Use patch_apply instead of multiple edits → 5-20x faster
- Use regex_replace for patterns → up to 10x faster
- Use analyze_project for directories → replaces 100+ operations

[TOKEN EFFICIENCY RANKINGS]
1. [BEST] file_exists - Single Yes/No (maximum efficiency)
2. [BEST] get_file_section - Only reads needed parts
3. [BEST] patch_apply - Single atomic operation
4. [ADVANCED] copy_file - No content processing
5. [BASIC] read_file - Reads entire content

[SPEED RANKINGS]
1. [BEST] file_exists - Instant
2. [BEST] backup_file - OS-level copy
3. [BEST] smart_indent - Bulk operations
4. [ADVANCED] get_file_section - Targeted reading

[GOLDEN RULE] Always choose the most specific tool for your task!"""

    elif operation_type == "search":
        return header_msg + """[FILE SEARCH TOOLS]

[EXPERT] regex_search - Use for complex pattern matching with capture groups
   - Example: def\\\\s+(\\\\w+)\\\\([^)]*\\\\): to find function definitions
   - Supports advanced flags: i=ignorecase, m=multiline, s=dotall
   - Capture groups: Extract specific parts of matches
   - Performance: Extremely fast for complex patterns
   - Token efficiency: Most powerful for pattern-based searches

[ADVANCED] search_in_file - Use for text search in single files
   - Simple text or basic regex search
   - Context lines: Show surrounding lines for better understanding
   - Line numbers: Exact location of matches
   - Performance: Optimized for single file searches
   - Token efficiency: Good for specific file searches

[ADVANCED] search_in_directory - Use for searching across multiple files
   - File extension filtering: Search only specific file types
   - Max files limit: Performance protection (default: 100 files)
   - Directory traversal: Recursive search with hidden file/folder exclusion
   - Performance: Handles large directories efficiently
   - Token efficiency: Best for project-wide searches

[USAGE GUIDELINES]
- Use regex_search for complex patterns (function names, variables, etc.)
- Use search_in_file for simple text searches in known files
- Use search_in_directory for finding text across your project
- Always specify file_extensions for better performance in large projects

[PERFORMANCE TIPS]
- Regex patterns are compiled once and reused for efficiency
- Context lines help understand matches without separate file reads
- Directory search respects .gitignore-style hidden folder exclusions
- UTF-8 and CP949 encodings are automatically handled

[TOKEN EFFICIENCY RANKINGS]
1. [BEST] regex_search - Most efficient for pattern matching
2. [ADVANCED] search_in_file - Good for single file searches
3. [ADVANCED] search_in_directory - Best for multi-file searches

[EXAMPLES]
- Find functions: regex_search(pattern="def\\\\s+(\\\\w+)", capture_groups=true)
- Find TODOs: search_in_directory(search_text="TODO", file_extensions=[".py"])
- Simple search: search_in_file(search_text="import", context_lines=2)"""

    else:
        return header_msg + f"[UNKNOWN] Operation type: '{operation_type}'\\n\\n[AVAILABLE TYPES] text_replace, line_edit, file_read, file_operations, directory_operations, code_format, search, performance, general\\n\\n[FOR PERFORMANCE DETAILS] Add show_performance=true to any category"


# Additional helper functions for enhanced recommendations
async def handle_tool_comparison(arguments: Dict[str, Any]) -> str:
    """Compare specific tools directly - AI optimized clean format"""
    tool1 = arguments.get("tool1", "")
    tool2 = arguments.get("tool2", "")
    
    if not tool1 or not tool2:
        return "[ERROR] Please provide both tool1 and tool2 parameters for comparison"
    
    rec1 = tool_advisor.recommendations.get(tool1)
    rec2 = tool_advisor.recommendations.get(tool2)
    
    if not rec1 or not rec2:
        return f"[ERROR] Tool information not found for {tool1 if not rec1 else tool2}"
    
    comparison = f"[TOOL COMPARISON] {tool1} vs {tool2}\\n\\n"
    
    # Priority comparison
    if rec1.priority < rec2.priority:
        comparison += f"[WINNER] {tool1} (higher priority)\\n"
    elif rec2.priority < rec1.priority:
        comparison += f"[WINNER] {tool2} (higher priority)\\n"
    else:
        comparison += f"[EQUAL PRIORITY] Both tools have same priority level\\n"
    
    comparison += f"\\n[{tool1.upper()}]\\n"
    comparison += f"[WHEN TO USE] {rec1.when_to_use}\\n"
    comparison += f"[PERFORMANCE] {rec1.performance_note}\\n"
    comparison += f"[TOKEN EFFICIENCY] {rec1.token_efficiency}\\n"
    comparison += f"[AVOID WHEN] {rec1.avoid_when}\\n"
    
    comparison += f"\\n[{tool2.upper()}]\\n"
    comparison += f"[WHEN TO USE] {rec2.when_to_use}\\n"
    comparison += f"[PERFORMANCE] {rec2.performance_note}\\n"
    comparison += f"[TOKEN EFFICIENCY] {rec2.token_efficiency}\\n"
    comparison += f"[AVOID WHEN] {rec2.avoid_when}\\n"
    
    return comparison
