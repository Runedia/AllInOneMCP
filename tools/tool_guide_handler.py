"""
Enhanced Tool Guide Handler - with performance comparisons and detailed recommendations
"""

from typing import Dict, Any
from tools.recommendations.tool_advisor import tool_advisor, get_performance_comparison


async def handle_tool_guide(arguments: Dict[str, Any]) -> str:
    """Comprehensive tool guidance with performance metrics"""
    operation_type = arguments.get("operation_type", "general")
    show_full_guide = arguments.get("show_full_guide", False)
    show_performance = arguments.get("show_performance", False)
    
    # 💡 Enhanced usage recommendation message
    header_msg = "🎯 **Smart Tool Recommendations** - Use this guide before complex operations for maximum efficiency!\\n\\n"
    
    if show_full_guide or operation_type == "general":
        # Full comprehensive guide
        base_guide = tool_advisor.get_tool_guide()
        footer = "\\n\\n💡 **Pro Tip**: For specific recommendations, use tool_guide with operation_type parameter!\\n"
        footer += "⚡ **Performance Tip**: Add show_performance=true for detailed efficiency metrics!"
        return header_msg + base_guide + footer
    
    # Performance comparison for specific categories
    if show_performance and operation_type in ["text_replacement", "line_editing", "file_reading", "file_operations", "directory_operations"]:
        return header_msg + get_performance_comparison(operation_type)
    
    # Specific operation recommendations with performance insights
    if operation_type == "text_replace":
        return header_msg + """🔍 **Text Replacement Tools:**

⚡ **regex_replace** (BEST): Use for patterns, multiple variants, or complex replacements
   - Example: `\\\\d+` to replace all numbers
   - Supports capture groups: `(\\\\w+)\\\\s+(\\\\w+)` → `$2 $1`
   - Performance: Up to 10x faster than multiple find_and_replace calls
   - Token efficiency: Handles multiple patterns in one pass

📝 **find_and_replace** (BASIC): Use only for exact string matches
   - Simple and safe for literal text
   - No pattern matching capabilities
   - Performance: Memory efficient streaming, but limited to literal matches

💡 **Recommendation**: Use regex_replace unless you need exact literal matching.

🚀 **Performance Tip**: For multiple similar replacements, regex_replace can be 10x faster!

📊 **Token Efficiency**: regex_replace saves tokens by combining multiple operations into one."""

    elif operation_type == "line_edit":
        return header_msg + """✂️ **Line Editing Tools:**

⚡ **patch_apply** (BEST): Use for 3+ operations or complex edits
   - Atomic operations (all succeed or all fail)
   - No line number conflicts
   - Most efficient for multiple changes
   - Performance: 5-20x faster than sequential operations
   - Token efficiency: Maximum efficiency - single atomic operation

🔧 **replace_line_range** (ADVANCED): Use for multi-line changes
   - Better than multiple insert_line calls
   - Good for replacing 2-20 lines
   - Performance: 3-5x faster than multiple insert_line operations

📝 **insert_line** (BASIC): Use only for single line insertion
   - Simple but inefficient for multiple operations
   - Performance: Efficient for single operations, inefficient when repeated

💡 **Recommendation**: Always prefer patch_apply for multiple edits.

🚀 **Pro Tip**: patch_apply prevents line number conflicts that often break sequential edits!

📊 **Efficiency Rule**: 1 operation = insert_line, 2-5 operations = consider patch_apply, 6+ operations = always patch_apply"""

    elif operation_type == "file_read":
        return header_msg + """📖 **File Reading Tools:**

⚡ **get_file_section** (BEST): Use for specific parts or large files
   - Token efficient - only reads what you need
   - Perfect for code review or targeted analysis
   - Supports context lines around target area
   - Performance: 10-100x faster for large files, minimal memory usage
   - Token efficiency: Saves 70-90% tokens compared to read_file on large files

📝 **read_file** (BASIC): Use only when you need the entire file
   - Memory and token intensive
   - Required for full file analysis
   - Performance: Can be memory intensive for large files

💡 **Recommendation**: Always use get_file_section unless you truly need the entire file.

🚀 **Token Saver**: Reading specific sections can save 70-90% of tokens on large files!

📊 **Size Threshold**: Files >50KB should almost always use get_file_section"""

    elif operation_type == "file_operations":
        return header_msg + """📁 **File Operations Tools:**

⚡ **backup_file** (ESSENTIAL): Use before any risky operations
   - Timestamped backups for safety
   - Performance: Essential safety practice, minimal overhead
   - Token efficiency: Extremely efficient - OS-level copy

🔧 **copy_file** (ADVANCED): Use for file duplication
   - OS-optimized copying, preserves metadata
   - Performance: 5-10x faster than read+write combination
   - Token efficiency: Extremely efficient - no content reading

🔧 **move_file** (ADVANCED): Use for relocation/renaming
   - Single atomic operation
   - Performance: Near-instantaneous on same filesystem

🔧 **append_to_file** (ADVANCED): Use for adding content to end
   - Memory efficient, no file reading needed
   - Performance: Much faster than read+modify+write

📝 **write_file** (BASIC): Use for complete file creation/replacement
   - Simple operation, complete control

💡 **Safety Rule**: Always backup_file before risky operations!

🚀 **Performance Tip**: copy_file is 5-10x faster than manual read+write!"""

    elif operation_type == "directory_operations":
        return header_msg + """📂 **Directory Analysis Tools:**

⚡ **analyze_project** (BEST): Use for large directory analysis
   - Comprehensive overview, file type breakdown
   - Performance: Optimized for large projects, much faster than manual analysis
   - Token efficiency: Extremely compact overview replacing hundreds of operations

🔧 **count_files** (ADVANCED): Use for file statistics
   - Summary format, extension filtering
   - Performance: Much faster than manual counting via list_directory

🔧 **get_recent_files** (ADVANCED): Use for finding latest changes
   - Sorted by modification time, configurable limit
   - Performance: Very fast with small result sets

📝 **list_directory** (BASIC): Use for simple browsing
   - Simple output, fast for small directories
   - Performance: Can be slow for large directories

💡 **Recommendation**: Use analyze_project for any directory >100 files

🚀 **Efficiency Tip**: analyze_project gives better overview than dozens of list_directory calls!"""

    elif operation_type == "code_format":
        return header_msg + """🎨 **Code Formatting Tools:**

⚡ **smart_indent** (BEST): Use for indentation changes
   - Automatic detection, consistent results
   - Tab/space intelligent
   - Performance: Can fix 50+ lines instantly
   - Token efficiency: Much faster than manual line-by-line editing

🔧 **replace_line_range**: Use for complex formatting that needs custom logic
   - More flexible but requires manual work

💡 **Recommendation**: Always try smart_indent first for indentation issues.

🚀 **Time Saver**: smart_indent can fix 50+ lines in seconds!

📊 **Use Case**: If it's just indentation, smart_indent. If it's complex formatting, use replace_line_range or patch_apply."""

    elif operation_type == "performance":
        return header_msg + """⚡ **Performance Optimization Guide:**

**High-Impact Optimizations:**
🚀 Use `get_file_section` instead of `read_file` → 70-90% token savings
🚀 Use `patch_apply` instead of multiple edits → 5-20x faster
🚀 Use `regex_replace` for patterns → up to 10x faster
🚀 Use `analyze_project` for directories → replaces 100+ operations

**Token Efficiency Rankings:**
1. ⚡ `file_exists` - Single Yes/No (maximum efficiency)
2. ⚡ `get_file_section` - Only reads needed parts
3. ⚡ `patch_apply` - Single atomic operation
4. 🔧 `copy_file` - No content processing
5. 📝 `read_file` - Reads entire content

**Speed Rankings:**
1. ⚡ `file_exists` - Instant
2. ⚡ `backup_file` - OS-level copy
3. ⚡ `smart_indent` - Bulk operations
4. 🔧 `get_file_section` - Targeted reading
5. 📝 `find_and_replace` - Sequential processing

💡 **Golden Rule**: Always choose the most specific tool for your task!"""

    else:
        return header_msg + f"❓ Unknown operation type: '{operation_type}'\\n\\n💡 **Available types**: text_replace, line_edit, file_read, file_operations, directory_operations, code_format, performance, general\\n\\n🔧 **For performance details**: Add show_performance=true to any category"


# Additional helper functions for enhanced recommendations
async def handle_tool_comparison(arguments: Dict[str, Any]) -> str:
    """Compare specific tools directly"""
    tool1 = arguments.get("tool1", "")
    tool2 = arguments.get("tool2", "")
    
    if not tool1 or not tool2:
        return "❓ Please provide both tool1 and tool2 parameters for comparison"
    
    rec1 = tool_advisor.recommendations.get(tool1)
    rec2 = tool_advisor.recommendations.get(tool2)
    
    if not rec1 or not rec2:
        return f"❓ Tool information not found for {tool1 if not rec1 else tool2}"
    
    comparison = f"⚡ **Tool Comparison: {tool1} vs {tool2}**\\n\\n"
    
    # Priority comparison
    if rec1.priority < rec2.priority:
        comparison += f"🏆 **Winner**: {tool1} (higher priority)\\n"
    elif rec2.priority < rec1.priority:
        comparison += f"🏆 **Winner**: {tool2} (higher priority)\\n"
    else:
        comparison += f"🤝 **Equal Priority**: Both tools have same priority level\\n"
    
    comparison += f"\\n**{tool1}:**\\n"
    comparison += f"✅ When to use: {rec1.when_to_use}\\n"
    comparison += f"⚡ Performance: {rec1.performance_note}\\n"
    comparison += f"🎯 Token efficiency: {rec1.token_efficiency}\\n"
    comparison += f"❌ Avoid when: {rec1.avoid_when}\\n"
    
    comparison += f"\\n**{tool2}:**\\n"
    comparison += f"✅ When to use: {rec2.when_to_use}\\n"
    comparison += f"⚡ Performance: {rec2.performance_note}\\n"
    comparison += f"🎯 Token efficiency: {rec2.token_efficiency}\\n"
    comparison += f"❌ Avoid when: {rec2.avoid_when}\\n"
    
    return comparison
