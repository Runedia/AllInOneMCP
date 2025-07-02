"""
Tool Recommendation System - AI selects the most efficient tools
Enhanced with performance metrics and comprehensive tool coverage
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolRecommendation:
    """Tool recommendation information"""
    tool_name: str
    priority: int  # 1=highest priority, 2=recommended, 3=basic
    use_cases: List[str]
    advantages: List[str]
    when_to_use: str
    avoid_when: str
    performance_note: str = ""  # Performance metrics or efficiency tips
    token_efficiency: str = ""  # Token usage optimization


class ToolAdvisor:
    """Tool selection advisor with comprehensive recommendations"""

    def __init__(self):
        self.tool_groups = self._initialize_tool_groups()
        self.recommendations = self._initialize_recommendations()

    def _initialize_tool_groups(self) -> Dict[str, List[str]]:
        """Group tools by functionality"""
        return {
            "text_replacement": [
                "regex_replace"          # Expert - pattern matching
            ],
            "line_editing": [
                "insert_line",           # Basic - single line insert
                "replace_line_range",    # Advanced - multi-line replace
                "delete_lines",          # Advanced - multi-line delete
                "patch_apply"            # Expert - safe individual operations
            ],
            "file_reading": [
                "read_file",            # Basic - entire file
                "get_file_section"      # Expert - specific parts only
            ],
            "file_operations": [
                "write_file",           # Basic - full file write
                "copy_file",            # Advanced - OS-optimized copy
                "move_file",            # Advanced - rename/move
                "delete_file",          # Advanced - safe deletion
                "backup_file",          # Expert - timestamp backup
                "backup_files",         # Expert - batch backup operations
                "append_to_file"        # Advanced - efficient append
            ],
            "directory_operations": [
                "list_directory",       # Basic - simple listing
                "create_directory",     # Basic - single directory
                "create_directories",   # Advanced - multiple directories
                "count_files",          # Advanced - file statistics
                "get_directory_size",   # Advanced - size calculation
                "get_recent_files",     # Advanced - recent changes
                "analyze_project"       # Expert - comprehensive analysis
            ],
            "file_info": [
                "file_exists",          # Expert - existence check only
                "file_info"             # Expert - metadata without content
            ],
            "code_formatting": [
                "smart_indent"          # Expert - automatic indentation
            ],
            "advanced_editing": [
                "insert_at_position",   # Advanced - byte-level precision
                "count_occurrences"     # Advanced - pattern search
            ],
            "function_analysis": [
                "find_function",       # Expert - tree-sitter function search
                "list_functions",      # Expert - complete function inventory
                "extract_function",    # Expert - precise function extraction
                "get_function_info"    # Expert - function metadata analysis
            ]
        }

    def _initialize_recommendations(self) -> Dict[str, ToolRecommendation]:
        """Initialize comprehensive tool recommendations"""
        return {
            # TEXT REPLACEMENT TOOLS
            "regex_replace": ToolRecommendation(
                tool_name="regex_replace",
                priority=1,
                use_cases=["Pattern-based replacement", "Multiple variants simultaneously", "Group capture usage", "Complex transformations"],
                advantages=["Powerful pattern matching", "Single operation for complex changes", "Memory efficient", "Group capture support"],
                when_to_use="Multiple patterns, similar variants, or complex text transformations",
                avoid_when="Simple literal string replacement",
                performance_note="Highly optimized for pattern matching",
                token_efficiency="High efficiency - handles multiple patterns in one pass"
            ),

            # LINE EDITING TOOLS  
            "insert_line": ToolRecommendation(
                tool_name="insert_line",
                priority=3,
                use_cases=["Single line insertion", "Simple additions"],
                advantages=["Simple operation", "Line change tracking", "Safe for beginners"],
                when_to_use="Adding exactly one line",
                avoid_when="Multiple line insertions or complex edits needed",
                performance_note="Efficient for single operations, inefficient when repeated",
                token_efficiency="Low efficiency if used multiple times"
            ),
            "replace_line_range": ToolRecommendation(
                tool_name="replace_line_range",
                priority=2,
                use_cases=["Multi-line replacement", "Block modifications", "Function rewrites"],
                advantages=["Handles multiple lines", "Line change tracking", "Memory efficient"],
                when_to_use="Replacing 2-20 lines with new content",
                avoid_when="Single line changes or when combined with other operations",
                performance_note="3-5x faster than multiple insert_line operations",
                token_efficiency="Good for multi-line blocks"
            ),
            "delete_lines": ToolRecommendation(
                tool_name="delete_lines",
                priority=2,
                use_cases=["Line range deletion", "Code block removal", "Cleanup operations"],
                advantages=["Efficient deletion", "Line change tracking", "Range support"],
                when_to_use="Removing consecutive lines or code blocks",
                avoid_when="Mixed operations (delete + insert + replace)",
                performance_note="Very fast for large deletions",
                token_efficiency="Excellent for removing content"
            ),
            "patch_apply": ToolRecommendation(
                tool_name="patch_apply",
                priority=2,
                use_cases=["Single safe operations", "Precise line editing", "Complex replacements", "Multiline content"],
                advantages=["No line conflicts", "Predictable results", "Safe editing", "Multiline support"],
                when_to_use="Single operation needing safety, multiline content, or when avoiding conflicts is critical",
                avoid_when="Multiple operations (use separate calls instead)",
                performance_note="Safe and predictable - prevents line number conflicts completely",
                token_efficiency="Good efficiency with complete safety guarantee"
            ),

            # FILE READING TOOLS
            "read_file": ToolRecommendation(
                tool_name="read_file",
                priority=3,
                use_cases=["Full file analysis", "Complete content needed", "Small files"],
                advantages=["Complete content access", "Simple to use"],
                when_to_use="Need entire file content or file is small (<50KB)",
                avoid_when="Large files or only specific sections needed",
                performance_note="Can be memory intensive for large files",
                token_efficiency="Use get_file_section to save 70-90% tokens on large files"
            ),
            "get_file_section": ToolRecommendation(
                tool_name="get_file_section",
                priority=1,
                use_cases=["Specific line ranges", "Large file inspection", "Code review", "Targeted analysis"],
                advantages=["Token efficient", "Memory efficient", "Fast for large files", "Context support"],
                when_to_use="Specific sections needed or files >50KB",
                avoid_when="Need complete file analysis",
                performance_note="10-100x faster for large files, minimal memory usage",
                token_efficiency="Saves 70-90% tokens compared to read_file on large files"
            ),

            # FILE OPERATIONS
            "write_file": ToolRecommendation(
                tool_name="write_file",
                priority=3,
                use_cases=["Full file creation", "Complete overwrites", "New file creation"],
                advantages=["Simple operation", "Complete control"],
                when_to_use="Creating new files or completely replacing content",
                avoid_when="Just adding content (use append_to_file) or partial modifications",
                performance_note="Efficient for complete rewrites",
                token_efficiency="Standard efficiency"
            ),
            "copy_file": ToolRecommendation(
                tool_name="copy_file",
                priority=2,
                use_cases=["File duplication", "Backup creation", "Template copying"],
                advantages=["OS-optimized copying", "Preserves metadata", "Very fast"],
                when_to_use="Duplicating files efficiently",
                avoid_when="Need to modify content during copy",
                performance_note="5-10x faster than read+write combination",
                token_efficiency="Extremely efficient - no content reading"
            ),
            "move_file": ToolRecommendation(
                tool_name="move_file",
                priority=2,
                use_cases=["File relocation", "Renaming", "Organization"],
                advantages=["Single atomic operation", "OS-optimized", "Fast"],
                when_to_use="Relocating or renaming files",
                avoid_when="Need to keep original (use copy_file)",
                performance_note="Near-instantaneous on same filesystem",
                token_efficiency="Extremely efficient - no content processing"
            ),
            "delete_file": ToolRecommendation(
                tool_name="delete_file",
                priority=2,
                use_cases=["File removal", "Cleanup operations", "Safe deletion"],
                advantages=["Confirmation options", "Error handling", "Force option available"],
                when_to_use="Removing unwanted files",
                avoid_when="Might need file later (use backup_file first)",
                performance_note="Instantaneous operation",
                token_efficiency="No content processing needed"
            ),
            "backup_file": ToolRecommendation(
                tool_name="backup_file",
                priority=1,
                use_cases=["Safety before risky operations", "Version preservation", "Rollback preparation"],
                advantages=["Timestamped backups", "Safety net", "Very fast"],
                when_to_use="Before any risky file modifications",
                avoid_when="File is already backed up recently",
                performance_note="Essential safety practice, minimal overhead",
                token_efficiency="Extremely efficient - OS-level copy"
            ),
            "backup_files": ToolRecommendation(
                tool_name="backup_files",
                priority=1,
                use_cases=["Batch backup operations", "Multiple file safety", "Consistent backup sets", "Pre-deployment safety"],
                advantages=["Consistent timestamps", "Batch efficiency", "Failure tracking", "Size statistics"],
                when_to_use="Need to backup multiple files with consistent timestamps",
                avoid_when="Only need single file backup (use backup_file)",
                performance_note="Much more efficient than multiple backup_file calls",
                token_efficiency="High efficiency for batch operations with detailed reporting"
            ),
            "append_to_file": ToolRecommendation(
                tool_name="append_to_file",
                priority=2,
                use_cases=["Adding content to end", "Log writing", "Incremental updates"],
                advantages=["Memory efficient", "No file reading needed", "Fast"],
                when_to_use="Adding content without reading existing file",
                avoid_when="Need to insert in middle or beginning",
                performance_note="Much faster than read+modify+write",
                token_efficiency="High efficiency - no file reading"
            ),
            # DIRECTORY OPERATIONS
            "list_directory": ToolRecommendation(
                tool_name="list_directory",
                priority=3,
                use_cases=["Simple directory listing", "File enumeration"],
                advantages=["Simple output", "Fast for small directories"],
                when_to_use="Basic directory browsing or small directories",
                avoid_when="Need statistics, large directories, or project overview",
                performance_note="Can be slow for large directories",
                token_efficiency="Use analyze_project for better overview"
            ),
            "create_directory": ToolRecommendation(
                tool_name="create_directory",
                priority=3,
                use_cases=["Single directory creation", "Simple folder setup"],
                advantages=["Simple and reliable", "Recursive creation"],
                when_to_use="Creating single directories",
                avoid_when="Complex directory structures needed",
                performance_note="Fast and reliable",
                token_efficiency="Minimal token usage"
            ),
            "create_directories": ToolRecommendation(
                tool_name="create_directories",
                priority=2,
                use_cases=["Multiple directory creation", "Complex directory structures", "Project initialization", "Batch folder setup"],
                advantages=["Single operation for multiple paths", "Automatic parent creation", "Error handling per path", "Batch efficiency"],
                when_to_use="Creating multiple directories or complex folder structures",
                avoid_when="Only need single directory (use create_directory)",
                performance_note="Much more efficient than multiple create_directory calls",
                token_efficiency="High efficiency for batch operations"
            ),
            "count_files": ToolRecommendation(
                tool_name="count_files",
                priority=2,
                use_cases=["File statistics", "Extension counting", "Quick overview"],
                advantages=["Summary format", "Extension filtering", "Fast"],
                when_to_use="Need file counts by type",
                avoid_when="Need detailed file information",
                performance_note="Much faster than manual counting via list_directory",
                token_efficiency="Compact summary output"
            ),
            "get_directory_size": ToolRecommendation(
                tool_name="get_directory_size",
                priority=2,
                use_cases=["Disk usage analysis", "Storage planning", "Size checking"],
                advantages=["Recursive calculation", "Compact output"],
                when_to_use="Need total directory size",
                avoid_when="Need per-file size breakdown",
                performance_note="Efficient recursive calculation",
                token_efficiency="Single summary value"
            ),
            "get_recent_files": ToolRecommendation(
                tool_name="get_recent_files",
                priority=2,
                use_cases=["Finding latest changes", "Recent work tracking", "Update monitoring"],
                advantages=["Sorted by modification time", "Configurable limit"],
                when_to_use="Finding recently modified files",
                avoid_when="Need all files or specific search criteria",
                performance_note="Very fast with small result sets",
                token_efficiency="Minimal output focused on recent changes"
            ),
            "analyze_project": ToolRecommendation(
                tool_name="analyze_project",
                priority=1,
                use_cases=["Project overview", "Large directory analysis", "Structure understanding"],
                advantages=["Comprehensive overview", "File type breakdown", "Compact summary"],
                when_to_use="Understanding large projects or directory structures",
                avoid_when="Need detailed per-file information",
                performance_note="Optimized for large projects, much faster than manual analysis",
                token_efficiency="Extremely compact overview replacing hundreds of list operations"
            ),

            # FILE INFO TOOLS
            "file_exists": ToolRecommendation(
                tool_name="file_exists",
                priority=1,
                use_cases=["Existence checking", "Validation", "Conditional operations"],
                advantages=["Instant response", "Minimal overhead", "Boolean result"],
                when_to_use="Just checking if file/directory exists",
                avoid_when="Need file metadata or content",
                performance_note="Fastest possible file operation",
                token_efficiency="Maximum efficiency - single Yes/No response"
            ),
            "file_info": ToolRecommendation(
                tool_name="file_info",
                priority=1,
                use_cases=["Metadata inspection", "Size checking", "Date verification", "Permission checking"],
                advantages=["No content reading", "Complete metadata", "Fast"],
                when_to_use="Need file properties without content",
                avoid_when="Need file content",
                performance_note="Much faster than reading file for metadata",
                token_efficiency="Compact metadata without content"
            ),

            # CODE FORMATTING
            "smart_indent": ToolRecommendation(
                tool_name="smart_indent",
                priority=1,
                use_cases=["Indentation fixing", "Code formatting", "Bulk indent changes"],
                advantages=["Automatic detection", "Consistent results", "Tab/space intelligent"],
                when_to_use="Fixing indentation issues",
                avoid_when="Complex formatting beyond indentation needed",
                performance_note="Can fix 50+ lines instantly",
                token_efficiency="Much faster than manual line-by-line editing"
            ),

            # ADVANCED EDITING
            "insert_at_position": ToolRecommendation(
                tool_name="insert_at_position",
                priority=2,
                use_cases=["Byte-level precision", "Binary file editing", "Exact positioning"],
                advantages=["Precise control", "Binary file support"],
                when_to_use="Need exact byte positioning or binary files",
                avoid_when="Line-based editing is sufficient",
                performance_note="Precise but more complex than line-based tools",
                token_efficiency="Use line-based tools for text files"
            ),
            "count_occurrences": ToolRecommendation(
                tool_name="count_occurrences",
                priority=2,
                use_cases=["Pattern frequency", "Text analysis", "Search statistics"],
                advantages=["Efficient counting", "Case sensitivity options", "Line statistics"],
                when_to_use="Need occurrence counts without replacement",
                avoid_when="Need to replace found text (use regex_replace)",
                performance_note="Much faster than manual search through content",
                token_efficiency="Compact statistical output"
            ),
            # 🆕 FUNCTION ANALYSIS TOOLS (Tree-sitter based)
            "find_function": ToolRecommendation(
                tool_name="find_function",
                priority=1,
                use_cases=["Function location finding", "Exact line number detection", "Multi-language function search", "Code navigation"],
                advantages=["Syntax-aware parsing", "Multi-language support", "Precise boundaries", "10x more accurate than regex"],
                when_to_use="Need to locate specific function with exact line numbers across multiple languages",
                avoid_when="Simple text search is sufficient",
                performance_note="10x more accurate than regex - syntax-aware parsing with multi-language support",
                token_efficiency="Single call provides precise location data eliminating manual parsing"
            ),
            "list_functions": ToolRecommendation(
                tool_name="list_functions",
                priority=1,
                use_cases=["Function inventory", "Code refactoring analysis", "Project structure overview", "Function complexity mapping"],
                advantages=["Complete function listing", "Type detection", "Complexity analysis", "Single file scan"],
                when_to_use="Need comprehensive overview of all functions in a file for refactoring or analysis",
                avoid_when="Only need to find one specific function",
                performance_note="Parses entire file once to extract all functions - much faster than repeated searches",
                token_efficiency="Replaces dozens of manual searches with structured data output"
            ),
            "extract_function": ToolRecommendation(
                tool_name="extract_function",
                priority=1,
                use_cases=["Function code extraction", "Documentation generation", "Code review", "Function copying"],
                advantages=["Perfect boundaries", "Comment inclusion", "Multi-language support", "Precise extraction"],
                when_to_use="Need exact function code with perfect boundaries for copying or documentation",
                avoid_when="Manual copy-paste from known line numbers is simpler",
                performance_note="Guarantees correct function boundaries including optional comments",
                token_efficiency="Precise extraction eliminates guesswork and manual line counting"
            ),
            "get_function_info": ToolRecommendation(
                tool_name="get_function_info",
                priority=1,
                use_cases=["Function metadata analysis", "Parameter inspection", "Complexity assessment", "Code quality metrics"],
                advantages=["Parameter analysis", "Complexity scoring", "Signature extraction", "Rich metadata"],
                when_to_use="Need detailed function analysis including parameters, complexity, and metadata",
                avoid_when="Simple function location is all that's needed",
                performance_note="Advanced static analysis providing comprehensive function insights",
                token_efficiency="Rich metadata in single call replacing multiple analysis steps"
            ),
        }

    def get_better_tool(self, current_tool: str, context: Optional[str] = None) -> Optional[str]:
        """Suggest better tool than current one"""
        for group_name, tools in self.tool_groups.items():
            if current_tool in tools:
                # Find tools with higher priority (lower number)
                current_priority = self.recommendations.get(current_tool, ToolRecommendation("", 999, [], [], "", "")).priority

                better_tools = []
                for tool in tools:
                    if tool != current_tool:
                        tool_priority = self.recommendations.get(tool, ToolRecommendation("", 999, [], [], "", "")).priority
                        if tool_priority < current_priority:
                            better_tools.append((tool, tool_priority))

                if better_tools:
                    # Return highest priority tool
                    best_tool = min(better_tools, key=lambda x: x[1])
                    return best_tool[0]

        return None

    def get_recommendation_message(self, suggested_tool: str, current_tool: str) -> str:
        """Generate recommendation message"""
        suggestion = self.recommendations.get(suggested_tool)
        if not suggestion:
            return ""

        msg = f"[TIP] **Better Tool Available**: Consider using `{suggested_tool}` instead of `{current_tool}`\\n"
        msg += f"[TARGET] **When to use**: {suggestion.when_to_use}\\n"
        msg += f"[GOOD FOR] **Advantages**: {', '.join(suggestion.advantages)}\\n"

        if suggestion.performance_note:
            msg += f"[BEST] **Performance**: {suggestion.performance_note}\\n"

        if suggestion.token_efficiency:
            msg += f"[TARGET] **Efficiency**: {suggestion.token_efficiency}\\n"

        return msg

    def get_tool_guide(self) -> str:
        """Generate comprehensive tool usage guide"""
        guide = "[TOOL SELECTION GUIDE] **Tool Selection Guide**\\n\\n"

        for group_name, tools in self.tool_groups.items():
            guide += f"**{group_name.replace('_', ' ').title()}:**\\n"

            # Sort by priority (lower number = higher priority)
            sorted_tools = sorted(tools, key=lambda t: self.recommendations.get(t, ToolRecommendation("", 999, [], [], "", "")).priority)

            for tool in sorted_tools:
                rec = self.recommendations.get(tool)
                if rec:
                    priority_emoji = "[BEST]" if rec.priority == 1 else "[ADVANCED]" if rec.priority == 2 else "[BASIC]"
                    guide += f"  {priority_emoji} `{tool}`: {rec.when_to_use}"

                    if rec.performance_note:
                        guide += f" ({rec.performance_note})"

                    guide += "\\n"

            guide += "\\n"

        return guide

    def get_performance_comparison(self, tool_category: str) -> str:
        """Get performance comparison for tool category"""
        if tool_category not in self.tool_groups:
            return "Category not found"

        tools = self.tool_groups[tool_category]
        comparison = f"[BEST] **Performance Comparison - {tool_category.replace('_', ' ').title()}:**\\n\\n"

        for tool in sorted(tools, key=lambda t: self.recommendations.get(t, ToolRecommendation("", 999, [], [], "", "")).priority):
            rec = self.recommendations.get(tool)
            if rec:
                priority_emoji = "[BEST]" if rec.priority == 1 else "[ADVANCED]" if rec.priority == 2 else "[BASIC]"
                comparison += f"{priority_emoji} **{tool}**\\n"
                comparison += f"   [PERFORMANCE] Performance: {rec.performance_note}\\n"
                comparison += f"   [TARGET] Token Efficiency: {rec.token_efficiency}\\n"
                comparison += f"   [GOOD FOR] Best for: {rec.when_to_use}\\n\\n"

        return comparison

    def analyze_operation(self, operation_type: str, **kwargs) -> str:
        """Analyze operation and recommend optimal tools"""
        recommendations = []

        if operation_type == "text_replace":
            recommendations.append("regex_replace")
            reason = "Pattern-based text replacement recommended"

        elif operation_type == "line_edit":
            line_count = kwargs.get("line_count", 1)
            operation_count = kwargs.get("operation_count", 1)
            needs_safety = kwargs.get("needs_safety", False)
            multiline_content = kwargs.get("multiline_content", False)

            if operation_count >= 3:
                recommendations.append("patch_apply")
                reason = f"Multiple operations ({operation_count}) - use {operation_count} separate patch_apply calls for safety"
            elif needs_safety or multiline_content:
                recommendations.append("patch_apply")
                reason = "Complex content or safety requirements - patch_apply provides conflict-free editing"
            elif line_count > 1:
                recommendations.append("replace_line_range")
                reason = f"Multi-line operation ({line_count} lines)"
            else:
                recommendations.append("insert_line")
                reason = "Single line operation"

        elif operation_type == "file_read":
            file_size = kwargs.get("file_size", 0)
            need_full_content = kwargs.get("need_full_content", True)

            if not need_full_content or file_size > 50000:  # 50KB threshold
                recommendations.append("get_file_section")
                reason = f"Large file ({file_size} bytes) or partial content needed"
            else:
                recommendations.append("read_file")
                reason = "Small file or full content required"

        if recommendations:
            tool = recommendations[0]
            rec = self.recommendations.get(tool)
            if rec:
                return f"[TARGET] **Recommended**: `{tool}` - {reason}\\n[TIP] {rec.when_to_use}"

        return "No specific recommendation available"


# Global instance
tool_advisor = ToolAdvisor()


def get_tool_recommendations() -> str:
    """Get tool recommendation guide"""
    return tool_advisor.get_tool_guide()


def suggest_better_tool(current_tool: str) -> Optional[str]:
    """Suggest better tool"""
    return tool_advisor.get_better_tool(current_tool)


def get_operation_recommendation(operation_type: str, **kwargs) -> str:
    """Get operation-specific tool recommendation"""
    return tool_advisor.analyze_operation(operation_type, **kwargs)


def get_performance_comparison(category: str) -> str:
    """Get performance comparison for tool category"""
    return tool_advisor.get_performance_comparison(category)
