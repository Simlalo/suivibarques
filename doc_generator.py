
#!/usr/bin/env python3
"""
Project Documentation Generator (Surgical Edition)
Gathers all project files into a comprehensive markdown document for AI context.
Includes: Complexity Scoring, Architecture Validation, and Dependency Scanning.
"""

import os
import sys
import time
import mimetypes
import subprocess
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import fnmatch
import argparse

class ProjectDocumentationGenerator:
    def __init__(self, project_path=".", output_file="project_documentation.md"):
        self.project_path = Path(project_path).resolve()
        self.output_file = output_file
        self.stats = {
            'total_files': 0,
            'included_files': 0,
            'ignored_files': 0,
            'total_lines': 0,
            'file_types': Counter(),
            'total_size': 0
        }
        
        # Standard ignore patterns
        self.ignore_patterns = [
            # Dependencies and build outputs
            'node_modules/**',
            '.next/**',
            'dist/**',
            'build/**',
            'out/**',
            '.vercel/**',
            '.netlify/**',
            'venv/**',
            'env/**',
            '__pycache__/**',
            '*.pyc',
            
            # Environment and config
            '.env*', 
            '*.log',
            '*.tmp',
            '*.temp',
            
            # Git and version control
            '.git/**',
            '.gitignore',
            
            # IDE and editor files
            '.vscode/**',
            '.idea/**',
            '*.swp',
            '*.swo',
            '*~',
            
            # OS files
            '.DS_Store',
            'Thumbs.db',
            
            # Cache directories
            '.cache/**',
            '.parcel-cache/**',
            'coverage/**',
            '.nyc_output/**',
            
            # Lock files (too verbose)
            'package-lock.json',
            'yarn.lock',
            'pnpm-lock.yaml',
            
            # Large or binary files
            '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
            '*.pdf', '*.zip', '*.tar.gz', '*.rar',
            '*.mp4', '*.mov', '*.avi',
            '*.woff', '*.woff2', '*.ttf', '*.eot',
        ]
        
        # Custom ignore patterns for specific projects
        self.custom_ignores = []
        
        # File size limit (in bytes) - 1MB default
        self.max_file_size = 1024 * 1024
        
        # Extensions to always include (even if large)
        self.force_include_extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.json',
            '.md', '.py', '.html', '.xml', '.yaml', '.yml', '.sql'
        }
        
        # Disable git operations by default (causes hanging)
        self.enable_git_info = False
    
    def add_custom_ignore(self, pattern):
        """Add custom ignore pattern"""
        self.custom_ignores.append(pattern)
    
    def should_ignore(self, file_path):
        """Check if file should be ignored"""
        relative_path = file_path.relative_to(self.project_path)
        path_str = str(relative_path)
        
        # Check against all ignore patterns
        all_patterns = self.ignore_patterns + self.custom_ignores
        
        for pattern in all_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(str(file_path.name), pattern):
                return True
        
        return False
    
    def is_binary_file(self, file_path):
        """Check if file is binary"""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and not mime_type.startswith('text'):
                return True
            
            # Try to read first few bytes
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:  # Null bytes indicate binary
                    return True
        except:
            return True
        
        return False
    
    def get_file_info(self, file_path):
        """Get file metadata"""
        try:
            stat = file_path.stat()
            
            # Git info disabled by default to prevent hanging
            git_info = {}
            if self.enable_git_info:
                git_info = self.get_git_info(file_path)
            
            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'git_modified': git_info.get('modified'),
                'git_author': git_info.get('author')
            }
        except:
            return {
                'size': 0,
                'created': datetime.now(),
                'modified': datetime.now(),
                'git_modified': None,
                'git_author': None
            }
    
    def get_git_info(self, file_path):
        """Get git information for file"""
        try:
            relative_path = file_path.relative_to(self.project_path)
            
            # Get last modification date from git
            result = subprocess.run([
                'git', 'log', '-1', '--format=%ai|%an', str(relative_path)
            ], capture_output=True, text=True, cwd=self.project_path, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                return {
                    'modified': parts[0] if len(parts) > 0 else None,
                    'author': parts[1] if len(parts) > 1 else None
                }
        except:
            pass
        
        return {}
    
    def get_language_from_extension(self, file_path):
        """Map file extension to language for syntax highlighting"""
        extension_map = {
            '.js': 'javascript',
            '.jsx': 'jsx',
            '.ts': 'typescript',
            '.tsx': 'tsx',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.md': 'markdown',
            '.py': 'python',
            '.html': 'html',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.env': 'bash'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'text')
    
    def count_lines(self, file_path):
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0

    # --- SURGICAL PROBES START ---
    def analyze_complexity(self, content, file_path):
        """
        Surgical Probe 1: Cognitive Complexity Scorer
        Counts indentation and branching to find 'Spaghetti Code'.
        """
        score = 0
        # Keywords that increase complexity
        branching = ['if ', 'else', 'for ', 'while ', 'case ', 'catch', '&&', '||', '?']
        
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            # Check for branching logic
            if any(b in stripped for b in branching):
                score += 1
            # Check for deep nesting (indentation > 4 tabs/8 spaces)
            if len(line) - len(line.lstrip()) > 16: 
                score += 1
        
        # Return analysis
        status = "🟢 Healthy"
        if score > 50: status = "🔴 CRITICAL (Refactor needed)"
        elif score > 25: status = "🟡 Warning (Complex)"
        
        return score, status

    def analyze_architecture_violations(self, content, file_path):
        """
        Surgical Probe 2: Architecture Validator
        Ensures UI components don't talk to Supabase directly (should go through Service Layer).
        """
        violations = []
        file_str = str(file_path).lower()
        
        # Rule: Components/Pages should not import 'supabaseClient' directly
        # They should import 'marintrack-db' or hooks.
        if 'components' in file_str or 'pages' in file_str:
            if "from '../lib/supabaseClient'" in content or 'from "@/lib/supabaseClient"' in content:
                violations.append("DIRECT_DB_ACCESS: Component bypassing Service Layer")
                
        return violations

    def analyze_dependencies(self, content):
        """
        Surgical Probe 3: Dependency Scanner
        Finds what this file imports.
        """
        # Regex to find imports
        import_pattern = r"import .* from ['\"](.*)['\"]"
        matches = re.findall(import_pattern, content)
        return matches
    # --- SURGICAL PROBES END ---
    
    def scan_project(self):
        """Scan project and categorize files"""
        included_files = []
        ignored_files = []
        
        print("Scanning files...")
        file_count = 0
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                file_count += 1
                if file_count % 100 == 0:
                    print(f"  Scanned {file_count} files...", end='\r')
                
                self.stats['total_files'] += 1
                
                if self.should_ignore(file_path):
                    ignored_files.append(file_path)
                    self.stats['ignored_files'] += 1
                else:
                    file_info = self.get_file_info(file_path)
                    
                    # Check file size
                    if (file_info['size'] > self.max_file_size and 
                        file_path.suffix.lower() not in self.force_include_extensions):
                        ignored_files.append(file_path)
                        self.stats['ignored_files'] += 1
                        continue
                    
                    # Check if binary
                    if self.is_binary_file(file_path):
                        ignored_files.append(file_path)
                        self.stats['ignored_files'] += 1
                        continue
                    
                    included_files.append((file_path, file_info))
                    self.stats['included_files'] += 1
                    self.stats['total_size'] += file_info['size']
                    self.stats['file_types'][file_path.suffix.lower() or 'no extension'] += 1
        
        print(f"  Scan complete! Found {file_count} files.      ")
        return included_files, ignored_files
    
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def generate_toc(self, included_files):
        """Generate table of contents"""
        toc = []
        categories = defaultdict(list)
        
        for file_path, _ in included_files:
            relative_path = file_path.relative_to(self.project_path)
            category = self.categorize_file(file_path)
            categories[category].append(relative_path)
        
        for category in sorted(categories.keys()):
            toc.append(f"  - [{category}](#{category.lower().replace(' ', '-')})")
            for file_path in sorted(categories[category]):
                safe_name = str(file_path).replace('/', '-').replace('.', '-')
                toc.append(f"    - [{file_path}](#{safe_name})")
        
        return '\n'.join(toc)
    
    def categorize_file(self, file_path):
        """Categorize file by its location and type"""
        relative_path = file_path.relative_to(self.project_path)
        parts = relative_path.parts
        
        # Check by directory structure
        if any(part in ['components', 'component'] for part in parts):
            return 'Components'
        elif any(part in ['pages', 'app'] for part in parts):
            return 'Pages/Routes'
        elif any(part in ['api', 'server'] for part in parts):
            return 'API/Server'
        elif any(part in ['utils', 'lib', 'helpers'] for part in parts):
            return 'Utilities'
        elif any(part in ['styles', 'css'] for part in parts):
            return 'Styles'
        elif any(part in ['types', 'interfaces'] for part in parts):
            return 'Types'
        elif any(part in ['hooks'] for part in parts):
            return 'Hooks'
        elif any(part in ['context', 'store', 'redux'] for part in parts):
            return 'State Management'
        elif any(part in ['public', 'static', 'assets'] for part in parts):
            return 'Static Assets'
        elif file_path.suffix.lower() in ['.json', '.js', '.ts'] and len(parts) == 1:
            return 'Configuration'
        elif file_path.name.lower() in ['readme.md', 'license', 'changelog.md']:
            return 'Documentation'
        else:
            return 'Other Files'
    
    def generate_markdown(self):
        """Generate the complete markdown documentation"""
        print("Scanning project...")
        included_files, ignored_files = self.scan_project()
        
        print(f"\nFound {self.stats['total_files']} files total")
        print(f"Including {self.stats['included_files']} files")
        print(f"Ignoring {self.stats['ignored_files']} files")
        
        # Calculate lines of code with progress
        print("\nCounting lines of code...")
        for i, (file_path, file_info) in enumerate(included_files):
            if i % 10 == 0:
                print(f"  Processing {i+1}/{len(included_files)} files...", end='\r')
            
            lines = self.count_lines(file_path)
            self.stats['total_lines'] += lines
        
        print(f"  Line counting complete!                    ")
        
        # Git info disabled by default to prevent hanging
        if self.enable_git_info and len(included_files) < 50:
            print("\nGetting git information...")
            for i, (file_path, file_info) in enumerate(included_files):
                if i % 5 == 0:
                    print(f"  Processing {i+1}/{len(included_files)} files...", end='\r')
                git_info = self.get_git_info(file_path)
                file_info.update(git_info)
            print("  Git info complete!                    ")
        
        print("\nGenerating markdown...")
        
        # Generate markdown content
        markdown_content = []
        
        # Header
        markdown_content.append(f"# Project Documentation")
        markdown_content.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_content.append(f"Project path: `{self.project_path}`")
        markdown_content.append("")
        
        # Statistics
        markdown_content.append("## Project Statistics")
        markdown_content.append("")
        markdown_content.append(f"- **Total files scanned:** {self.stats['total_files']:,}")
        markdown_content.append(f"- **Files included:** {self.stats['included_files']:,}")
        markdown_content.append(f"- **Files ignored:** {self.stats['ignored_files']:,}")
        markdown_content.append(f"- **Total lines of code:** {self.stats['total_lines']:,}")
        markdown_content.append(f"- **Total size (included files):** {self.format_size(self.stats['total_size'])}")
        markdown_content.append("")
        
        # File types breakdown
        markdown_content.append("### File Types")
        markdown_content.append("")
        for ext, count in self.stats['file_types'].most_common():
            markdown_content.append(f"- **{ext or 'no extension'}:** {count} files")
        markdown_content.append("")
        
        # Table of contents
        markdown_content.append("## Table of Contents")
        markdown_content.append("")
        markdown_content.append(self.generate_toc(included_files))
        markdown_content.append("")
        
        # Project structure (simplified for large projects)
        if self.stats['total_files'] < 200:
            markdown_content.append("## Complete Project Structure")
            markdown_content.append("")
            markdown_content.append("```")
            markdown_content.append(self.generate_tree_structure())
            markdown_content.append("```")
            markdown_content.append("")
        else:
            markdown_content.append("## Project Structure")
            markdown_content.append("")
            markdown_content.append("*(Project structure omitted due to large number of files - see file contents below)*")
            markdown_content.append("")
        
        # Categorized file contents with Surgical Analysis
        categories = defaultdict(list)
        for file_path, file_info in included_files:
            category = self.categorize_file(file_path)
            categories[category].append((file_path, file_info))
        
        # New Diagnostics Storage
        complexity_report = []
        architecture_report = []

        for category in sorted(categories.keys()):
            markdown_content.append(f"## {category}")
            markdown_content.append("")
            
            for file_path, file_info in sorted(categories[category]):
                relative_path = file_path.relative_to(self.project_path)
                safe_name = str(relative_path).replace('/', '-').replace('.', '-')
                
                # File header
                markdown_content.append(f"### {relative_path}")
                markdown_content.append("")
                
                # File metadata
                markdown_content.append("**File Info:**")
                markdown_content.append(f"- Size: {self.format_size(file_info['size'])}")
                markdown_content.append(f"- Lines: {self.count_lines(file_path):,}")
                markdown_content.append(f"- Created: {file_info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                markdown_content.append(f"- Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if file_info.get('git_modified'):
                    markdown_content.append(f"- Git Last Modified: {file_info['git_modified']}")
                if file_info.get('git_author'):
                    markdown_content.append(f"- Git Last Author: {file_info['git_author']}")
                
                markdown_content.append("")
                
                # File content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # --- RUN SURGICAL PROBES ---
                        complexity, health = self.analyze_complexity(content, file_path)
                        violations = self.analyze_architecture_violations(content, file_path)
                        imports = self.analyze_dependencies(content)
                        
                        # Store results for summary
                        if complexity > 25:
                            complexity_report.append(f"- **{relative_path}**: Score {complexity} ({health})")
                        if violations:
                            for v in violations:
                                architecture_report.append(f"- 🚨 **{relative_path}**: {v}")

                        # Append Diagnosis to the file section in Markdown
                        markdown_content.append(f"> **Surgical Diagnosis:**")
                        markdown_content.append(f"> - Complexity: {complexity} {health}")
                        if violations:
                            markdown_content.append(f"> - ⚠️ **Violations:** {', '.join(violations)}")
                        markdown_content.append(f"> - Imports: {len(imports)} external modules")
                        markdown_content.append("")

                        # Content
                        language = self.get_language_from_extension(file_path)
                        markdown_content.append(f"```{language}")
                        markdown_content.append(content)
                        markdown_content.append("```")
                        markdown_content.append("")
                except Exception as e:
                    markdown_content.append(f"```")
                    markdown_content.append(f"Error reading file: {str(e)}")
                    markdown_content.append("```")
                    markdown_content.append("")
        
        # --- INSERT DIAGNOSTIC DASHBOARD ---
        # We insert this right after the Statistics section (approx index 15)
        # to ensure it's seen early
        dashboard = []
        dashboard.append("## 🏥 Surgical Analysis Report")
        dashboard.append("")
        dashboard.append("### 🧠 Complexity Hotspots (Refactor Candidates)")
        if complexity_report:
            dashboard.extend(complexity_report)
        else:
            dashboard.append("No complex files detected.")
            
        dashboard.append("")
        dashboard.append("### 🏗️ Architectural Integrity")
        if architecture_report:
            dashboard.extend(architecture_report)
        else:
            dashboard.append("No architectural violations detected.")
        dashboard.append("")
        
        # Find insertion point (before Table of Contents)
        insert_index = 0
        for i, line in enumerate(markdown_content):
            if "## Table of Contents" in line:
                insert_index = i
                break
        
        if insert_index > 0:
            markdown_content[insert_index:insert_index] = dashboard
        else:
            markdown_content.extend(dashboard) # Fallback

        # Ignored files section (simplified for large projects)
        if ignored_files and len(ignored_files) < 100:
            markdown_content.append("## Ignored Files")
            markdown_content.append("")
            markdown_content.append("The following files were excluded from the documentation:")
            markdown_content.append("")
            
            for file_path in sorted(ignored_files):
                relative_path = file_path.relative_to(self.project_path)
                try:
                    file_info = self.get_file_info(file_path)
                    size_str = self.format_size(file_info['size'])
                    markdown_content.append(f"- `{relative_path}` ({size_str})")
                except:
                    markdown_content.append(f"- `{relative_path}`")
            
            markdown_content.append("")
        elif ignored_files:
            markdown_content.append("## Ignored Files")
            markdown_content.append("")
            markdown_content.append(f"**{len(ignored_files)} files were excluded** (list omitted due to size)")
            markdown_content.append("")
        
        return '\n'.join(markdown_content)
    
    def generate_tree_structure(self):
        """Generate a tree-like structure of the project"""
        tree_lines = []
        
        def add_to_tree(path, prefix="", is_last=True):
            if path.is_file():
                connector = "└── " if is_last else "├── "
                size = self.format_size(path.stat().st_size)
                ignored = " (ignored)" if self.should_ignore(path) else ""
                tree_lines.append(f"{prefix}{connector}{path.name} ({size}){ignored}")
            else:
                if path == self.project_path:
                    tree_lines.append(f"{path.name}/")
                else:
                    connector = "└── " if is_last else "├── "
                    tree_lines.append(f"{prefix}{connector}{path.name}/")
                
                # Get subdirectories and files
                try:
                    children = sorted([p for p in path.iterdir()], 
                                    key=lambda x: (x.is_file(), x.name.lower()))
                    
                    for i, child in enumerate(children):
                        is_last_child = i == len(children) - 1
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        add_to_tree(child, new_prefix, is_last_child)
                except PermissionError:
                    pass
        
        add_to_tree(self.project_path)
        return '\n'.join(tree_lines)
    
    def save_documentation(self, content):
        """Save the markdown content to file"""
        output_path = Path(self.output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\nDocumentation generated successfully!")
        print(f"Output file: {output_path.resolve()}")
        print(f"File size: {self.format_size(len(content.encode('utf-8')))}")

def main():
    parser = argparse.ArgumentParser(description='Generate project documentation for AI context')
    parser.add_argument('path', nargs='?', default='.', help='Path to project directory')
    parser.add_argument('-o', '--output', default='project_documentation.md', help='Output file name')
    parser.add_argument('--max-size', type=int, default=1024*1024, help='Maximum file size in bytes')
    parser.add_argument('--ignore', action='append', help='Additional ignore patterns')
    parser.add_argument('--enable-git', action='store_true', help='Enable git information (may be slow)')
    parser.add_argument('--dry-run', action='store_true', help='Just scan and show stats, don\'t generate markdown')
    
    args = parser.parse_args()
    
    print(f"Project Documentation Generator (Surgical)")
    print(f"Project path: {Path(args.path).resolve()}")
    print(f"Output file: {args.output}")
    print()
    
    # Create generator
    generator = ProjectDocumentationGenerator(args.path, args.output)
    generator.max_file_size = args.max_size
    generator.enable_git_info = args.enable_git
    
    # Add custom ignore patterns
    if args.ignore:
        for pattern in args.ignore:
            generator.add_custom_ignore(pattern)
    
    try:
        if args.dry_run:
            print("DRY RUN - Just scanning...")
            included_files, ignored_files = generator.scan_project()
            print("\nScan completed!")
            print(f"Would include {len(included_files)} files")
            print(f"Would ignore {len(ignored_files)} files")
            
            # Show some examples
            if included_files:
                print("\nSample included files:")
                for file_path, _ in included_files[:5]:
                    rel_path = file_path.relative_to(generator.project_path)
                    print(f"  - {rel_path}")
                if len(included_files) > 5:
                    print(f"  ... and {len(included_files) - 5} more")
            
            if ignored_files:
                print("\nSample ignored files:")
                for file_path in ignored_files[:5]:
                    rel_path = file_path.relative_to(generator.project_path)
                    print(f"  - {rel_path}")
                if len(ignored_files) > 5:
                    print(f"  ... and {len(ignored_files) - 5} more")
        else:
            # Generate documentation
            content = generator.generate_markdown()
            generator.save_documentation(content)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()